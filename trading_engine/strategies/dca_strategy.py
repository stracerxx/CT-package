from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import time
import logging
from .engine import TradingEngine

logger = logging.getLogger('dca_strategy')

class DCAStrategy:
    """
    Dollar Cost Averaging (DCA) Trading Strategy
    
    Invests a fixed amount at regular intervals regardless of price.
    Reduces the impact of volatility and eliminates the need to time the market.
    """
    
    def __init__(self, 
                 engine: TradingEngine,
                 symbol: str,
                 investment_amount: float = 100.0,
                 interval_hours: int = 24,
                 max_positions: int = 10,
                 take_profit_pct: Optional[float] = None):
        """
        Initialize DCA Strategy
        
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            investment_amount: Fixed amount to invest each interval
            interval_hours: Time between investments in hours
            max_positions: Maximum number of positions to hold
            take_profit_pct: Optional take profit percentage (None for true DCA)
        """
        self.engine = engine
        self.symbol = symbol
        self.investment_amount = investment_amount
        self.interval_hours = interval_hours
        self.max_positions = max_positions
        self.take_profit_pct = take_profit_pct
        
        # Strategy state
        self.positions = []  # List of positions with entry price and time
        self.last_investment_time = 0
        
        logger.info(f"DCA Strategy initialized for {symbol} with {investment_amount} investment every {interval_hours} hours")
    
    def should_invest(self) -> bool:
        """Check if it's time to make a new investment"""
        current_time = time.time()
        hours_since_last = (current_time - self.last_investment_time) / 3600
        
        # Check if enough time has passed since last investment
        if hours_since_last >= self.interval_hours:
            # Check if we haven't reached max positions
            if len(self.positions) < self.max_positions:
                return True
        
        return False
    
    def make_investment(self) -> Dict:
        """Make a new DCA investment"""
        # Get current price
        ticker = self.engine.get_ticker(self.symbol)
        if not ticker or 'last' not in ticker:
            logger.error(f"Failed to get current price for {self.symbol}")
            return {'success': False, 'reason': 'Failed to get current price'}
        
        current_price = ticker['last']
        
        # Calculate amount to buy
        amount = self.investment_amount / current_price
        
        # Execute buy order
        order = self.engine.execute_trade(self.symbol, 'buy', amount)
        
        if 'id' in order:
            # Record position
            position = {
                'entry_price': current_price,
                'amount': amount,
                'entry_time': time.time(),
                'order_id': order['id']
            }
            
            self.positions.append(position)
            self.last_investment_time = time.time()
            
            logger.info(f"DCA investment: Bought {amount} {self.symbol} at {current_price}")
            
            return {
                'success': True,
                'action': 'buy',
                'amount': amount,
                'price': current_price,
                'order': order,
                'positions': len(self.positions)
            }
        else:
            logger.error(f"Failed to execute DCA buy order: {order}")
            return {
                'success': False,
                'action': 'error',
                'reason': f"Failed to execute buy order: {order.get('error', 'Unknown error')}"
            }
    
    def check_take_profit(self) -> Dict:
        """Check if any positions should be sold for profit"""
        if not self.take_profit_pct or not self.positions:
            return {'action': 'none', 'reason': 'No take profit set or no positions'}
        
        # Get current price
        ticker = self.engine.get_ticker(self.symbol)
        if not ticker or 'last' not in ticker:
            logger.error(f"Failed to get current price for {self.symbol}")
            return {'action': 'none', 'reason': 'Failed to get current price'}
        
        current_price = ticker['last']
        
        # Check each position
        positions_to_sell = []
        
        for i, position in enumerate(self.positions):
            entry_price = position['entry_price']
            profit_pct = (current_price - entry_price) / entry_price * 100
            
            if profit_pct >= self.take_profit_pct:
                positions_to_sell.append(i)
        
        if not positions_to_sell:
            return {'action': 'none', 'reason': 'No positions reached take profit level'}
        
        # Sell positions that reached take profit
        total_amount = 0
        for i in sorted(positions_to_sell, reverse=True):
            total_amount += self.positions[i]['amount']
            del self.positions[i]
        
        # Execute sell order
        order = self.engine.execute_trade(self.symbol, 'sell', total_amount)
        
        if 'id' in order:
            logger.info(f"Take profit: Sold {total_amount} {self.symbol} at {current_price}")
            
            return {
                'action': 'sell',
                'amount': total_amount,
                'price': current_price,
                'reason': f"Take profit triggered at {self.take_profit_pct}%",
                'order': order,
                'positions_sold': len(positions_to_sell),
                'remaining_positions': len(self.positions)
            }
        else:
            logger.error(f"Failed to execute take profit sell order: {order}")
            return {
                'action': 'error',
                'reason': f"Failed to execute sell order: {order.get('error', 'Unknown error')}"
            }
    
    def calculate_average_entry(self) -> Dict:
        """Calculate average entry price and total position"""
        if not self.positions:
            return {
                'average_price': 0,
                'total_amount': 0,
                'total_cost': 0,
                'positions': 0
            }
        
        total_cost = 0
        total_amount = 0
        
        for position in self.positions:
            total_cost += position['entry_price'] * position['amount']
            total_amount += position['amount']
        
        average_price = total_cost / total_amount if total_amount > 0 else 0
        
        return {
            'average_price': average_price,
            'total_amount': total_amount,
            'total_cost': total_cost,
            'positions': len(self.positions)
        }
    
    def run_iteration(self) -> Dict:
        """Run one iteration of the strategy"""
        # Check if trading is active
        if not self.engine.is_trading_active:
            return {
                'action': 'none',
                'reason': 'Trading is not active'
            }
        
        # Check if we should make a new investment
        if self.should_invest():
            return self.make_investment()
        
        # Check if any positions should be sold for profit
        if self.take_profit_pct:
            take_profit_result = self.check_take_profit()
            if take_profit_result['action'] != 'none':
                return take_profit_result
        
        # No action needed
        return {
            'action': 'none',
            'reason': 'No action needed at this time',
            'next_investment_in_hours': self.interval_hours - (time.time() - self.last_investment_time) / 3600,
            'positions': len(self.positions)
        }
    
    def get_status(self) -> Dict:
        """Get current strategy status"""
        avg_entry = self.calculate_average_entry()
        
        # Get current price
        current_price = 0
        try:
            ticker = self.engine.get_ticker(self.symbol)
            if ticker and 'last' in ticker:
                current_price = ticker['last']
        except Exception as e:
            logger.error(f"Error getting current price: {str(e)}")
        
        # Calculate unrealized profit/loss
        unrealized_pnl = 0
        unrealized_pnl_pct = 0
        
        if avg_entry['average_price'] > 0 and current_price > 0:
            unrealized_pnl = (current_price - avg_entry['average_price']) * avg_entry['total_amount']
            unrealized_pnl_pct = (current_price - avg_entry['average_price']) / avg_entry['average_price'] * 100
        
        return {
            'strategy': 'Dollar Cost Averaging',
            'symbol': self.symbol,
            'investment_amount': self.investment_amount,
            'interval_hours': self.interval_hours,
            'max_positions': self.max_positions,
            'take_profit_pct': self.take_profit_pct,
            'current_positions': len(self.positions),
            'average_entry_price': avg_entry['average_price'],
            'total_invested': avg_entry['total_cost'],
            'total_amount': avg_entry['total_amount'],
            'current_price': current_price,
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'next_investment_in_hours': self.interval_hours - (time.time() - self.last_investment_time) / 3600 if self.last_investment_time > 0 else 0
        }
