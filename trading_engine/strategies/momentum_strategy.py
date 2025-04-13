from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import time
import logging
from .engine import TradingEngine

logger = logging.getLogger('momentum_strategy')

class MomentumStrategy:
    """
    Momentum Trading Strategy
    
    Trades based on the continuation of existing price trends.
    Buys assets that are showing strong upward momentum and sells when momentum weakens.
    """
    
    def __init__(self, 
                 engine: TradingEngine,
                 symbol: str,
                 timeframe: str = '1h',
                 roc_period: int = 14,
                 roc_threshold: float = 5.0,
                 rsi_period: int = 14,
                 rsi_overbought: int = 70,
                 rsi_oversold: int = 30,
                 volume_factor: float = 1.5,
                 profit_target_pct: float = 3.0,
                 stop_loss_pct: float = 2.0):
        """
        Initialize Momentum Strategy
        
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for analysis (e.g., '1h', '4h')
            roc_period: Period for Rate of Change calculation
            roc_threshold: Threshold for Rate of Change to signal momentum
            rsi_period: Period for RSI calculation
            rsi_overbought: RSI level considered overbought
            rsi_oversold: RSI level considered oversold
            volume_factor: Volume increase factor to confirm momentum
            profit_target_pct: Target profit percentage
            stop_loss_pct: Stop loss percentage
        """
        self.engine = engine
        self.symbol = symbol
        self.timeframe = timeframe
        self.roc_period = roc_period
        self.roc_threshold = roc_threshold
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.volume_factor = volume_factor
        self.profit_target_pct = profit_target_pct
        self.stop_loss_pct = stop_loss_pct
        
        # Strategy state
        self.active_position = None
        self.position_entry_time = None
        self.position_entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
        
        logger.info(f"Momentum Strategy initialized for {symbol} with {timeframe} timeframe")
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for decision making"""
        # Calculate Rate of Change (ROC)
        df['roc'] = ((df['close'] - df['close'].shift(self.roc_period)) / df['close'].shift(self.roc_period)) * 100
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate Volume Moving Average
        df['volume_ma'] = df['volume'].rolling(window=self.roc_period).mean()
        
        # Calculate Moving Averages for trend confirmation
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Calculate MACD for trend confirmation
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
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
        
        # Strong positive momentum (ROC above threshold)
        if latest['roc'] > self.roc_threshold:
            buy_signal = True
            buy_reason.append(f"Strong positive momentum (ROC: {latest['roc']:.2f}%)")
        
        # Volume confirmation (current volume above average)
        if latest['volume'] > latest['volume_ma'] * self.volume_factor:
            buy_signal = True
            buy_reason.append(f"Volume surge ({latest['volume'] / latest['volume_ma']:.2f}x average)")
        
        # Trend confirmation (price above moving averages)
        if current_price > latest['sma_20'] and latest['sma_20'] > latest['sma_50']:
            buy_signal = True
            buy_reason.append("Price above moving averages in uptrend")
        
        # MACD confirmation (MACD above signal line)
        if latest['macd'] > latest['macd_signal'] and latest['macd_histogram'] > 0:
            buy_signal = True
            buy_reason.append("MACD confirms upward momentum")
        
        # Check for sell signal
        sell_signal = False
        sell_reason = []
        
        # Momentum weakening (ROC dropping)
        if latest['roc'] < previous['roc'] and previous['roc'] > self.roc_threshold:
            sell_signal = True
            sell_reason.append(f"Momentum weakening (ROC: {latest['roc']:.2f}% < {previous['roc']:.2f}%)")
        
        # RSI overbought
        if latest['rsi'] > self.rsi_overbought:
            sell_signal = True
            sell_reason.append(f"RSI overbought ({latest['rsi']:.2f})")
        
        # MACD reversal (MACD crossing below signal line)
        if latest['macd'] < latest['macd_signal'] and previous['macd'] >= previous['macd_signal']:
            sell_signal = True
            sell_reason.append("MACD bearish crossover")
        
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
            
            # Check if we should exit based on momentum weakening
            if self.active_position == 'long' and sell_signal:
                return {
                    'signal': 'sell',
                    'reason': ', '.join(sell_reason),
                    'price': current_price
                }
        else:
            # Check if we should enter a position
            # For momentum strategy, we need multiple confirmations
            confirmation_count = len(buy_reason)
            if confirmation_count >= 2 and self.engine.is_trading_active:
                return {
                    'signal': 'buy',
                    'reason': ', '.join(buy_reason),
                    'price': current_price,
                    'confirmations': confirmation_count
                }
        
        return {
            'signal': 'none',
            'reason': 'No trading opportunity',
            'price': current_price
        }
    
    def execute_signal(self, signal: Dict) -> Dict:
        """Execute trading signal"""
        if signal['signal'] == 'buy' and not self.active_position:
            # Calculate position size (10% of available balance or max trade amount)
            balance = self.engine.get_balance()
            quote_currency = self.symbol.split('/')[1]  # e.g., USDT from BTC/USDT
            
            available_balance = balance.get('free', {}).get(quote_currency, 0)
            position_size = min(available_balance * 0.1, self.engine.max_trade_amount)
            
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
                
                logger.info(f"Opened momentum long position for {amount} {self.symbol} at {signal['price']}")
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
                
                logger.info(f"Closed momentum position for {position_size} {self.symbol} at {exit_price} (P/L: {profit_pct:.2f}%)")
                
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
            'strategy': 'Momentum Trading',
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'active_position': self.active_position,
            'position_entry_time': self.position_entry_time,
            'position_entry_price': self.position_entry_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'profit_target_pct': self.profit_target_pct,
            'stop_loss_pct': self.stop_loss_pct,
            'roc_threshold': self.roc_threshold
        }
