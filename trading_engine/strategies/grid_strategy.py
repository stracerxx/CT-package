from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import time
import logging
from .engine import TradingEngine

logger = logging.getLogger('grid_strategy')

class GridTradingStrategy:
    """
    Grid Trading Strategy
    
    Creates a grid of buy and sell orders at regular price intervals.
    Profits from price oscillations within a range.
    """
    
    def __init__(self, 
                 engine: TradingEngine,
                 symbol: str,
                 upper_price: float,
                 lower_price: float,
                 grid_levels: int = 10,
                 total_investment: float = 1000,
                 rebalance_threshold: float = 0.05):
        """
        Initialize Grid Trading Strategy
        
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            upper_price: Upper price boundary for the grid
            lower_price: Lower price boundary for the grid
            grid_levels: Number of grid levels
            total_investment: Total investment amount
            rebalance_threshold: Threshold to trigger grid rebalancing (as percentage)
        """
        self.engine = engine
        self.symbol = symbol
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.grid_levels = grid_levels
        self.total_investment = total_investment
        self.rebalance_threshold = rebalance_threshold
        
        # Grid state
        self.grid_prices = []
        self.grid_orders = {}
        self.last_rebalance_time = 0
        
        # Initialize grid
        self._initialize_grid()
        
        logger.info(f"Grid Trading Strategy initialized for {symbol} with {grid_levels} levels")
    
    def _initialize_grid(self):
        """Initialize the price grid"""
        # Calculate price levels
        price_range = self.upper_price - self.lower_price
        grid_step = price_range / self.grid_levels
        
        # Create grid prices
        self.grid_prices = [self.lower_price + i * grid_step for i in range(self.grid_levels + 1)]
        
        logger.info(f"Grid initialized with prices from {self.lower_price} to {self.upper_price}")
    
    def _calculate_order_size(self, price: float) -> float:
        """Calculate order size for a given price level"""
        # Distribute investment equally across grid levels
        investment_per_level = self.total_investment / self.grid_levels
        
        # Calculate order size in base currency
        order_size = investment_per_level / price
        
        return order_size
    
    def place_grid_orders(self) -> Dict:
        """Place all grid orders"""
        results = {
            'buy_orders': [],
            'sell_orders': []
        }
        
        # Get current price
        ticker = self.engine.get_ticker(self.symbol)
        if not ticker or 'last' not in ticker:
            logger.error(f"Failed to get current price for {self.symbol}")
            return results
        
        current_price = ticker['last']
        
        # Place buy orders below current price
        for price in self.grid_prices:
            if price < current_price:
                order_size = self._calculate_order_size(price)
                order = self.engine.execute_trade(self.symbol, 'buy', order_size, price)
                if 'id' in order:
                    self.grid_orders[order['id']] = {
                        'price': price,
                        'size': order_size,
                        'side': 'buy'
                    }
                    results['buy_orders'].append(order)
        
        # Place sell orders above current price
        for price in self.grid_prices:
            if price > current_price:
                order_size = self._calculate_order_size(price)
                order = self.engine.execute_trade(self.symbol, 'sell', order_size, price)
                if 'id' in order:
                    self.grid_orders[order['id']] = {
                        'price': price,
                        'size': order_size,
                        'side': 'sell'
                    }
                    results['sell_orders'].append(order)
        
        logger.info(f"Placed {len(results['buy_orders'])} buy orders and {len(results['sell_orders'])} sell orders")
        return results
    
    def check_and_rebalance(self) -> Dict:
        """Check if grid needs rebalancing and rebalance if necessary"""
        # Get current price
        ticker = self.engine.get_ticker(self.symbol)
        if not ticker or 'last' not in ticker:
            logger.error(f"Failed to get current price for {self.symbol}")
            return {'rebalanced': False, 'reason': 'Failed to get current price'}
        
        current_price = ticker['last']
        
        # Check if price is outside grid boundaries
        if current_price > self.upper_price or current_price < self.lower_price:
            logger.info(f"Price {current_price} is outside grid boundaries [{self.lower_price}, {self.upper_price}]")
            
            # Check if enough time has passed since last rebalance
            current_time = time.time()
            if current_time - self.last_rebalance_time < 3600:  # 1 hour cooldown
                return {'rebalanced': False, 'reason': 'Rebalance cooldown period'}
            
            # Rebalance grid
            self._rebalance_grid(current_price)
            self.last_rebalance_time = current_time
            
            return {'rebalanced': True, 'new_grid': self.grid_prices}
        
        return {'rebalanced': False, 'reason': 'Price within grid boundaries'}
    
    def _rebalance_grid(self, current_price: float):
        """Rebalance the grid around current price"""
        # Calculate new grid boundaries
        grid_range = self.upper_price - self.lower_price
        half_range = grid_range / 2
        
        new_lower_price = max(current_price - half_range, 0)
        new_upper_price = current_price + half_range
        
        # Update grid parameters
        self.lower_price = new_lower_price
        self.upper_price = new_upper_price
        
        # Cancel existing orders
        # In a real implementation, we would cancel orders via the exchange
        self.grid_orders = {}
        
        # Reinitialize grid
        self._initialize_grid()
        
        # Place new grid orders
        self.place_grid_orders()
        
        logger.info(f"Grid rebalanced with new boundaries: [{new_lower_price}, {new_upper_price}]")
    
    def get_grid_status(self) -> Dict:
        """Get current grid status"""
        return {
            'symbol': self.symbol,
            'lower_price': self.lower_price,
            'upper_price': self.upper_price,
            'grid_levels': self.grid_levels,
            'total_investment': self.total_investment,
            'active_orders': len(self.grid_orders),
            'grid_prices': self.grid_prices
        }
