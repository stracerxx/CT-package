from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import time
import logging
from .engine import TradingEngine

logger = logging.getLogger('dynamic_stop_loss')

class DynamicStopLossModule:
    """
    Dynamic Stop-Loss Module
    
    Provides advanced stop-loss functionality that adapts to market conditions.
    Helps prevent unnecessary losses while allowing trades room to breathe.
    """
    
    def __init__(self, 
                 engine: TradingEngine,
                 symbol: str,
                 initial_stop_loss_pct: float = 2.0,
                 trailing_stop_pct: Optional[float] = None,
                 atr_period: int = 14,
                 atr_multiplier: float = 2.0,
                 time_based_adjustment: bool = True,
                 volatility_based_adjustment: bool = True):
        """
        Initialize Dynamic Stop-Loss Module
        
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            initial_stop_loss_pct: Initial stop loss percentage
            trailing_stop_pct: Trailing stop percentage (None to disable)
            atr_period: Period for ATR calculation
            atr_multiplier: Multiplier for ATR-based stop loss
            time_based_adjustment: Whether to adjust stop loss based on time
            volatility_based_adjustment: Whether to adjust stop loss based on volatility
        """
        self.engine = engine
        self.symbol = symbol
        self.initial_stop_loss_pct = initial_stop_loss_pct
        self.trailing_stop_pct = trailing_stop_pct
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.time_based_adjustment = time_based_adjustment
        self.volatility_based_adjustment = volatility_based_adjustment
        
        # Module state
        self.positions = {}  # Dictionary of positions with stop loss info
        
        logger.info(f"Dynamic Stop-Loss Module initialized for {symbol}")
    
    def _calculate_atr(self, timeframe: str = '1h') -> float:
        """Calculate Average True Range for volatility-based stop loss"""
        try:
            # Get OHLCV data
            df = self.engine.get_ohlcv(self.symbol, timeframe, limit=self.atr_period + 10)
            if df.empty:
                return 0
            
            # Calculate True Range
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = np.abs(df['high'] - df['close'].shift())
            df['low_close'] = np.abs(df['low'] - df['close'].shift())
            df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            
            # Calculate ATR
            atr = df['tr'].rolling(window=self.atr_period).mean().iloc[-1]
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return 0
    
    def calculate_initial_stop_loss(self, entry_price: float, side: str = 'long') -> float:
        """
        Calculate initial stop loss price
        
        Args:
            entry_price: Entry price of the position
            side: 'long' or 'short'
            
        Returns:
            Stop loss price
        """
        # Base stop loss on percentage
        base_stop_loss = entry_price * (1 - self.initial_stop_loss_pct / 100) if side == 'long' else entry_price * (1 + self.initial_stop_loss_pct / 100)
        
        # If volatility-based adjustment is enabled, use ATR
        if self.volatility_based_adjustment:
            atr = self._calculate_atr()
            if atr > 0:
                # ATR-based stop loss
                atr_stop_loss = entry_price - (atr * self.atr_multiplier) if side == 'long' else entry_price + (atr * self.atr_multiplier)
                
                # Use the wider of the two stop losses
                if side == 'long':
                    return min(base_stop_loss, atr_stop_loss)
                else:
                    return max(base_stop_loss, atr_stop_loss)
        
        return base_stop_loss
    
    def register_position(self, position_id: str, entry_price: float, amount: float, side: str = 'long') -> Dict:
        """
        Register a new position for stop loss tracking
        
        Args:
            position_id: Unique identifier for the position
            entry_price: Entry price of the position
            amount: Position size
            side: 'long' or 'short'
            
        Returns:
            Dictionary with position and stop loss info
        """
        # Calculate initial stop loss
        stop_loss_price = self.calculate_initial_stop_loss(entry_price, side)
        
        # Register position
        self.positions[position_id] = {
            'entry_price': entry_price,
            'current_price': entry_price,
            'amount': amount,
            'side': side,
            'entry_time': time.time(),
            'stop_loss_price': stop_loss_price,
            'highest_price': entry_price if side == 'long' else float('inf'),
            'lowest_price': entry_price if side == 'short' else 0,
            'stop_loss_updated': False
        }
        
        logger.info(f"Registered position {position_id} with initial stop loss at {stop_loss_price}")
        
        return self.positions[position_id]
    
    def update_position(self, position_id: str, current_price: float) -> Dict:
        """
        Update position with current price and adjust stop loss if needed
        
        Args:
            position_id: Unique identifier for the position
            current_price: Current price of the asset
            
        Returns:
            Updated position info
        """
        if position_id not in self.positions:
            logger.error(f"Position {position_id} not found")
            return {}
        
        position = self.positions[position_id]
        position['current_price'] = current_price
        
        # Update highest/lowest price
        if position['side'] == 'long':
            position['highest_price'] = max(position['highest_price'], current_price)
        else:
            position['lowest_price'] = min(position['lowest_price'], current_price)
        
        # Adjust stop loss based on trailing stop
        if self.trailing_stop_pct and position['stop_loss_updated']:
            if position['side'] == 'long':
                trailing_stop = position['highest_price'] * (1 - self.trailing_stop_pct / 100)
                if trailing_stop > position['stop_loss_price']:
                    position['stop_loss_price'] = trailing_stop
                    logger.info(f"Updated trailing stop loss for {position_id} to {trailing_stop}")
            else:
                trailing_stop = position['lowest_price'] * (1 + self.trailing_stop_pct / 100)
                if trailing_stop < position['stop_loss_price']:
                    position['stop_loss_price'] = trailing_stop
                    logger.info(f"Updated trailing stop loss for {position_id} to {trailing_stop}")
        
        # Adjust stop loss based on time
        if self.time_based_adjustment and not position['stop_loss_updated']:
            current_time = time.time()
            hours_elapsed = (current_time - position['entry_time']) / 3600
            
            # After 24 hours, move stop loss to breakeven
            if hours_elapsed >= 24:
                if position['side'] == 'long' and position['highest_price'] > position['entry_price'] * 1.01:
                    position['stop_loss_price'] = position['entry_price']
                    position['stop_loss_updated'] = True
                    logger.info(f"Moved stop loss to breakeven for {position_id} after 24 hours")
                elif position['side'] == 'short' and position['lowest_price'] < position['entry_price'] * 0.99:
                    position['stop_loss_price'] = position['entry_price']
                    position['stop_loss_updated'] = True
                    logger.info(f"Moved stop loss to breakeven for {position_id} after 24 hours")
        
        # Check if stop loss is triggered
        is_triggered = False
        if position['side'] == 'long' and current_price <= position['stop_loss_price']:
            is_triggered = True
        elif position['side'] == 'short' and current_price >= position['stop_loss_price']:
            is_triggered = True
        
        if is_triggered:
            logger.info(f"Stop loss triggered for {position_id} at {current_price}")
            position['stop_loss_triggered'] = True
            return position
        
        return position
    
    def check_positions(self) -> List[Dict]:
        """
        Check all positions and update stop losses
        
        Returns:
            List of positions with triggered stop losses
        """
        triggered_positions = []
        
        # Get current price
        try:
            ticker = self.engine.get_ticker(self.symbol)
            if not ticker or 'last' not in ticker:
                logger.error(f"Failed to get current price for {self.symbol}")
                return triggered_positions
            
            current_price = ticker['last']
            
            # Update all positions
            for position_id, position in list(self.positions.items()):
                updated_position = self.update_position(position_id, current_price)
                if updated_position.get('stop_loss_triggered', False):
                    triggered_positions.append(updated_position)
                    # Remove from tracking
                    del self.positions[position_id]
        
        except Exception as e:
            logger.error(f"Error checking positions: {str(e)}")
        
        return triggered_positions
    
    def remove_position(self, position_id: str):
        """Remove a position from tracking"""
        if position_id in self.positions:
            del self.positions[position_id]
            logger.info(f"Removed position {position_id} from stop loss tracking")
    
    def get_position(self, position_id: str) -> Dict:
        """Get position info"""
        return self.positions.get(position_id, {})
    
    def get_all_positions(self) -> Dict:
        """Get all tracked positions"""
        return self.positions
