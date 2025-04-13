from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import time
import logging
from .engine import TradingEngine

logger = logging.getLogger('swing_strategy')

class SwingTradingStrategy:
    """
    Swing Trading Strategy
    
    Aims to capture medium-term price movements over several days or weeks.
    Uses technical analysis to identify potential trend reversals.
    """
    
    def __init__(self, 
                 engine: TradingEngine,
                 symbol: str,
                 timeframe: str = '4h',
                 macd_fast: int = 12,
                 macd_slow: int = 26,
                 macd_signal: int = 9,
                 bollinger_period: int = 20,
                 bollinger_std: float = 2.0,
                 profit_target_pct: float = 5.0,
                 stop_loss_pct: float = 2.5):
        """
        Initialize Swing Trading Strategy
        
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for analysis (e.g., '4h', '1d')
            macd_fast: Period for MACD fast EMA
            macd_slow: Period for MACD slow EMA
            macd_signal: Period for MACD signal line
            bollinger_period: Period for Bollinger Bands
            bollinger_std: Standard deviation multiplier for Bollinger Bands
            profit_target_pct: Target profit percentage
            stop_loss_pct: Stop loss percentage
        """
        self.engine = engine
        self.symbol = symbol
        self.timeframe = timeframe
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bollinger_period = bollinger_period
        self.bollinger_std = bollinger_std
        self.profit_target_pct = profit_target_pct
        self.stop_loss_pct = stop_loss_pct
        
        # Strategy state
        self.active_position = None
        self.position_entry_time = None
        self.position_entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
        
        logger.info(f"Swing Trading Strategy initialized for {symbol} with {timeframe} timeframe")
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for decision making"""
        # Calculate MACD
        ema_fast = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Calculate Bollinger Bands
        df['bollinger_mid'] = df['close'].rolling(window=self.bollinger_period).mean()
        df['bollinger_std'] = df['close'].rolling(window=self.bollinger_period).std()
        df['bollinger_upper'] = df['bollinger_mid'] + (df['bollinger_std'] * self.bollinger_std)
        df['bollinger_lower'] = df['bollinger_mid'] - (df['bollinger_std'] * self.bollinger_std)
        
        # Calculate ADX (Average Directional Index) for trend strength
        # True Range
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        
        # Directional Movement
        df['up_move'] = df['high'] - df['high'].shift()
        df['down_move'] = df['low'].shift() - df['low']
        
        df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
        df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
        
        # Smoothed Averages
        period = 14
        df['tr_smoothed'] = df['tr'].rolling(window=period).sum()
        df['plus_di'] = 100 * (df['plus_dm'].rolling(window=period).sum() / df['tr_smoothed'])
        df['minus_di'] = 100 * (df['minus_dm'].rolling(window=period).sum() / df['tr_smoothed'])
        
        # ADX
        df['dx'] = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        df['adx'] = df['dx'].rolling(window=period).mean()
        
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
        
        # MACD crossover (MACD line crosses above signal line)
        if previous['macd'] <= previous['macd_signal'] and latest['macd'] > latest['macd_signal']:
            buy_signal = True
            buy_reason.append("MACD bullish crossover")
        
        # Price near Bollinger lower band with strong ADX
        if current_price <= latest['bollinger_lower'] * 1.02 and latest['adx'] > 25:
            buy_signal = True
            buy_reason.append("Price near Bollinger lower band with strong trend")
        
        # Directional movement (bullish)
        if latest['plus_di'] > latest['minus_di'] and previous['plus_di'] <= previous['minus_di']:
            buy_signal = True
            buy_reason.append("Bullish directional movement crossover")
        
        # Check for sell signal
        sell_signal = False
        sell_reason = []
        
        # MACD crossover (MACD line crosses below signal line)
        if previous['macd'] >= previous['macd_signal'] and latest['macd'] < latest['macd_signal']:
            sell_signal = True
            sell_reason.append("MACD bearish crossover")
        
        # Price near Bollinger upper band with strong ADX
        if current_price >= latest['bollinger_upper'] * 0.98 and latest['adx'] > 25:
            sell_signal = True
            sell_reason.append("Price near Bollinger upper band with strong trend")
        
        # Directional movement (bearish)
        if latest['minus_di'] > latest['plus_di'] and previous['minus_di'] <= previous['plus_di']:
            sell_signal = True
            sell_reason.append("Bearish directional movement crossover")
        
        # Check if we have an active position
        if self.active_position:
            # Check if we should exit based on stop loss
            if self.active_position == 'long' and current_price <= self.stop_loss_price:
                return {
                    'signal': 'sell',
                    'reason': f"Stop loss triggered at {self.stop_loss_price}",
                    'price': current_price
                }
            
            # Check if we should exit based on take profit
            if self.active_position == 'long' and current_price >= self.take_profit_price:
                return {
                    'signal': 'sell',
                    'reason': f"Take profit triggered at {self.take_profit_price}",
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
            # Calculate position size (5% of available balance or max trade amount)
            balance = self.engine.get_balance()
            quote_currency = self.symbol.split('/')[1]  # e.g., USDT from BTC/USDT
            
            available_balance = balance.get('free', {}).get(quote_currency, 0)
            position_size = min(available_balance * 0.05, self.engine.max_trade_amount)
            
            # Convert to asset amount
            amount = position_size / signal['price']
            
            # Execute buy order
            order = self.engine.execute_trade(self.symbol, 'buy', amount)
            
            if 'id' in order:
                self.active_position = 'long'
                self.position_entry_time = time.time()
                self.position_entry_price = signal['price']
                
                # Set stop loss and take profit levels
                self.stop_loss_price = signal['price'] * (1 - self.stop_loss_pct / 100)
                self.take_profit_price = signal['price'] * (1 + self.profit_target_pct / 100)
                
                logger.info(f"Opened long position for {amount} {self.symbol} at {signal['price']}")
                logger.info(f"Stop loss: {self.stop_loss_price}, Take profit: {self.take_profit_price}")
                
                return {
                    'action': 'buy',
                    'amount': amount,
                    'price': signal['price'],
                    'reason': signal['reason'],
                    'stop_loss': self.stop_loss_price,
                    'take_profit': self.take_profit_price,
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
                self.stop_loss_price = None
                self.take_profit_price = None
                
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
            'strategy': 'Swing Trading',
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'active_position': self.active_position,
            'position_entry_time': self.position_entry_time,
            'position_entry_price': self.position_entry_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'profit_target_pct': self.profit_target_pct,
            'stop_loss_pct': self.stop_loss_pct
        }
