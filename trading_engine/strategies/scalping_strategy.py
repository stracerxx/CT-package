from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import time
import logging
from .engine import TradingEngine

logger = logging.getLogger('scalping_strategy')

class ScalpingStrategy:
    """
    Scalping Trading Strategy
    
    Makes quick trades to capture small price movements.
    Uses short timeframes and technical indicators for rapid entry and exit.
    """
    
    def __init__(self, 
                 engine: TradingEngine,
                 symbol: str,
                 timeframe: str = '1m',
                 rsi_period: int = 14,
                 rsi_overbought: int = 70,
                 rsi_oversold: int = 30,
                 ema_short: int = 9,
                 ema_long: int = 21,
                 profit_target_pct: float = 0.5,
                 max_trade_duration: int = 30):  # in minutes
        """
        Initialize Scalping Strategy
        
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for analysis (e.g., '1m', '5m')
            rsi_period: Period for RSI calculation
            rsi_overbought: RSI level considered overbought
            rsi_oversold: RSI level considered oversold
            ema_short: Period for short EMA
            ema_long: Period for long EMA
            profit_target_pct: Target profit percentage
            max_trade_duration: Maximum trade duration in minutes
        """
        self.engine = engine
        self.symbol = symbol
        self.timeframe = timeframe
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.profit_target_pct = profit_target_pct
        self.max_trade_duration = max_trade_duration
        
        # Strategy state
        self.active_position = None
        self.position_entry_time = None
        self.position_entry_price = None
        
        logger.info(f"Scalping Strategy initialized for {symbol} with {timeframe} timeframe")
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for decision making"""
        # Calculate RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate EMAs
        df[f'ema_{self.ema_short}'] = df['close'].ewm(span=self.ema_short, adjust=False).mean()
        df[f'ema_{self.ema_long}'] = df['close'].ewm(span=self.ema_long, adjust=False).mean()
        
        return df
    
    def analyze_market(self) -> Dict:
        """Analyze market and generate trading signals"""
        # Get market data
        df = self.engine.get_ohlcv(self.symbol, self.timeframe, limit=100)
        if df.empty:
            logger.error(f"Failed to get OHLCV data for {self.symbol}")
            return {'signal': 'none', 'reason': 'No data available'}
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Get latest values
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Current price
        current_price = latest['close']
        
        # Check for buy signal
        buy_signal = False
        buy_reason = []
        
        # RSI oversold condition
        if latest['rsi'] < self.rsi_oversold:
            buy_signal = True
            buy_reason.append(f"RSI oversold ({latest['rsi']:.2f})")
        
        # EMA crossover (short above long)
        if previous[f'ema_{self.ema_short}'] <= previous[f'ema_{self.ema_long}'] and \
           latest[f'ema_{self.ema_short}'] > latest[f'ema_{self.ema_long}']:
            buy_signal = True
            buy_reason.append("EMA crossover (bullish)")
        
        # Check for sell signal
        sell_signal = False
        sell_reason = []
        
        # RSI overbought condition
        if latest['rsi'] > self.rsi_overbought:
            sell_signal = True
            sell_reason.append(f"RSI overbought ({latest['rsi']:.2f})")
        
        # EMA crossover (short below long)
        if previous[f'ema_{self.ema_short}'] >= previous[f'ema_{self.ema_long}'] and \
           latest[f'ema_{self.ema_short}'] < latest[f'ema_{self.ema_long}']:
            sell_signal = True
            sell_reason.append("EMA crossover (bearish)")
        
        # Check if we have an active position
        if self.active_position:
            # Check if we should exit based on profit target
            if self.active_position == 'long' and current_price >= self.position_entry_price * (1 + self.profit_target_pct / 100):
                return {
                    'signal': 'sell',
                    'reason': f"Profit target reached ({self.profit_target_pct}%)",
                    'price': current_price
                }
            
            # Check if we should exit based on time limit
            current_time = time.time()
            if self.position_entry_time and (current_time - self.position_entry_time) / 60 >= self.max_trade_duration:
                return {
                    'signal': 'sell',
                    'reason': f"Maximum trade duration reached ({self.max_trade_duration} minutes)",
                    'price': current_price
                }
            
            # Check if we should exit based on technical indicators
            if self.active_position == 'long' and sell_signal:
                return {
                    'signal': 'sell',
                    'reason': ', '.join(sell_reason),
                    'price': current_price
                }
        else:
            # Check if we should enter a position
            if buy_signal and self.engine.is_trading_active:
                return {
                    'signal': 'buy',
                    'reason': ', '.join(buy_reason),
                    'price': current_price
                }
        
        return {
            'signal': 'none',
            'reason': 'No trading opportunity',
            'price': current_price
        }
    
    def execute_signal(self, signal: Dict) -> Dict:
        """Execute trading signal"""
        if signal['signal'] == 'buy' and not self.active_position:
            # Calculate position size (1% of available balance or max trade amount)
            balance = self.engine.get_balance()
            quote_currency = self.symbol.split('/')[1]  # e.g., USDT from BTC/USDT
            
            available_balance = balance.get('free', {}).get(quote_currency, 0)
            position_size = min(available_balance * 0.01, self.engine.max_trade_amount)
            
            # Convert to asset amount
            amount = position_size / signal['price']
            
            # Execute buy order
            order = self.engine.execute_trade(self.symbol, 'buy', amount)
            
            if 'id' in order:
                self.active_position = 'long'
                self.position_entry_time = time.time()
                self.position_entry_price = signal['price']
                
                logger.info(f"Opened long position for {amount} {self.symbol} at {signal['price']}")
                
                return {
                    'action': 'buy',
                    'amount': amount,
                    'price': signal['price'],
                    'reason': signal['reason'],
                    'order': order
                }
            else:
                logger.error(f"Failed to execute buy order: {order}")
                return {
                    'action': 'error',
                    'reason': f"Failed to execute buy order: {order.get('error', 'Unknown error')}"
                }
                
        elif signal['signal'] == 'sell' and self.active_position == 'long':
            # Get position size from active trades
            active_trades = self.engine.get_active_trades()
            position_size = 0
            
            for trade_id, trade in active_trades.items():
                if trade['symbol'] == self.symbol and trade['side'] == 'buy':
                    position_size += trade['amount']
            
            # Execute sell order
            order = self.engine.execute_trade(self.symbol, 'sell', position_size)
            
            if 'id' in order:
                # Calculate profit/loss
                entry_price = self.position_entry_price
                exit_price = signal['price']
                profit_pct = (exit_price - entry_price) / entry_price * 100
                
                logger.info(f"Closed long position for {position_size} {self.symbol} at {exit_price} (P/L: {profit_pct:.2f}%)")
                
                # Reset position
                self.active_position = None
                self.position_entry_time = None
                self.position_entry_price = None
                
                return {
                    'action': 'sell',
                    'amount': position_size,
                    'price': exit_price,
                    'reason': signal['reason'],
                    'profit_pct': profit_pct,
                    'order': order
                }
            else:
                logger.error(f"Failed to execute sell order: {order}")
                return {
                    'action': 'error',
                    'reason': f"Failed to execute sell order: {order.get('error', 'Unknown error')}"
                }
        
        return {
            'action': 'none',
            'reason': 'No action taken'
        }
    
    def run_iteration(self) -> Dict:
        """Run one iteration of the strategy"""
        # Check if trading is active
        if not self.engine.is_trading_active and not self.active_position:
            return {
                'action': 'none',
                'reason': 'Trading is not active'
            }
        
        # Analyze market
        signal = self.analyze_market()
        
        # Execute signal
        result = self.execute_signal(signal)
        
        return result
    
    def get_status(self) -> Dict:
        """Get current strategy status"""
        return {
            'strategy': 'Scalping',
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'active_position': self.active_position,
            'position_entry_time': self.position_entry_time,
            'position_entry_price': self.position_entry_price,
            'profit_target_pct': self.profit_target_pct,
            'max_trade_duration': self.max_trade_duration
        }
