import ccxt
import pandas as pd
import numpy as np
import time
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Union, Any
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trading_engine')

# Load environment variables
load_dotenv()

class TradingEngine:
    """
    Main trading engine class that integrates with CCXT and implements various trading strategies
    """
    
    def __init__(self, exchange_id: str = None, api_key: str = None, secret: str = None):
        """
        Initialize the trading engine with exchange credentials
        
        Args:
            exchange_id: CCXT exchange ID (e.g., 'binance', 'coinbase', etc.)
            api_key: API key for the exchange
            secret: API secret for the exchange
        """
        # Use environment variables if not provided
        self.exchange_id = exchange_id or os.getenv('DEFAULT_EXCHANGE', 'binance')
        self.api_key = api_key
        self.secret = secret
        self.trading_mode = os.getenv('TRADING_MODE', 'paper')  # 'paper' or 'live'
        self.max_trade_amount = float(os.getenv('MAX_TRADE_AMOUNT', '100'))
        
        # Initialize exchange connection
        self.exchange = self._initialize_exchange()
        
        # Market state
        self.market_condition_score = 0
        self.is_trading_active = False
        self.min_market_condition_score = int(os.getenv('MIN_MARKET_CONDITION_SCORE', '60'))
        self.auto_resume_threshold = int(os.getenv('AUTO_RESUME_THRESHOLD', '75'))
        
        # Active trades and positions
        self.active_trades = {}
        
        logger.info(f"Trading engine initialized with {self.exchange_id} in {self.trading_mode} mode")
    
    def _initialize_exchange(self):
        """Initialize the CCXT exchange"""
        try:
            # Create exchange instance
            exchange_class = getattr(ccxt, self.exchange_id)
            
            # Configure exchange
            exchange_config = {
                'enableRateLimit': True,  # Respect rate limits
            }
            
            # Add API credentials if in live mode
            if self.trading_mode == 'live' and self.api_key and self.secret:
                exchange_config.update({
                    'apiKey': self.api_key,
                    'secret': self.secret
                })
            
            exchange = exchange_class(exchange_config)
            
            # Load markets
            exchange.load_markets()
            logger.info(f"Successfully connected to {self.exchange_id}")
            return exchange
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {str(e)}")
            # Return a paper trading simulator if exchange initialization fails
            return self._initialize_paper_trading_simulator()
    
    def _initialize_paper_trading_simulator(self):
        """Initialize a paper trading simulator"""
        # For paper trading, we can still use CCXT but without API keys
        # This allows us to get market data but simulate trades
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            exchange = exchange_class({
                'enableRateLimit': True,
            })
            exchange.load_markets()
            logger.info(f"Initialized paper trading simulator for {self.exchange_id}")
            return exchange
        except Exception as e:
            logger.error(f"Failed to initialize paper trading simulator: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Dictionary with ticker data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            return {}
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for candles (e.g., '1m', '5m', '1h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            Pandas DataFrame with OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def execute_trade(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        """
        Execute a trade
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Price to trade at (optional, market order if None)
            
        Returns:
            Dictionary with trade result
        """
        # Enforce max trade amount
        amount = min(amount, self.max_trade_amount)
        
        # Execute trade based on mode
        if self.trading_mode == 'live':
            return self._execute_live_trade(symbol, side, amount, price)
        else:
            return self._execute_paper_trade(symbol, side, amount, price)
    
    def _execute_live_trade(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        """Execute a live trade"""
        try:
            if price:
                # Limit order
                order = self.exchange.create_order(symbol, 'limit', side, amount, price)
            else:
                # Market order
                order = self.exchange.create_order(symbol, 'market', side, amount)
            
            logger.info(f"Executed {side} order for {amount} {symbol} at {price if price else 'market price'}")
            
            # Track the trade
            trade_id = order['id']
            self.active_trades[trade_id] = {
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'status': order['status'],
                'timestamp': time.time()
            }
            
            return order
        except Exception as e:
            logger.error(f"Error executing {side} order for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def _execute_paper_trade(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        """Simulate a paper trade"""
        try:
            # Get current price if not provided
            if not price:
                ticker = self.get_ticker(symbol)
                price = ticker['last']
            
            # Create simulated order
            order_id = f"paper_{int(time.time())}_{side}_{symbol.replace('/', '')}"
            order = {
                'id': order_id,
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'cost': amount * price,
                'status': 'closed',
                'timestamp': int(time.time() * 1000),
                'datetime': pd.Timestamp.now().isoformat(),
                'fee': {
                    'cost': amount * price * 0.001,  # Simulated 0.1% fee
                    'currency': symbol.split('/')[1]
                },
                'info': {'paper_trading': True}
            }
            
            logger.info(f"Paper traded: {side} {amount} {symbol} at {price}")
            
            # Track the trade
            self.active_trades[order_id] = {
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'status': 'closed',
                'timestamp': time.time()
            }
            
            return order
        except Exception as e:
            logger.error(f"Error simulating {side} order for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def update_market_condition(self, symbols: List[str] = None) -> int:
        """
        Update market condition score based on various indicators
        
        Args:
            symbols: List of symbols to analyze (default: ['BTC/USDT', 'ETH/USDT'])
            
        Returns:
            Market condition score (0-100)
        """
        if not symbols:
            symbols = ['BTC/USDT', 'ETH/USDT']
        
        try:
            # Initialize score components
            price_momentum_score = 0
            volume_score = 0
            volatility_score = 0
            trend_score = 0
            
            for symbol in symbols:
                # Get OHLCV data
                df = self.get_ohlcv(symbol, timeframe='1h', limit=24)
                if df.empty:
                    continue
                
                # Calculate price momentum (current price vs 24h ago)
                current_price = df['close'].iloc[-1]
                price_24h_ago = df['close'].iloc[0]
                price_change_pct = (current_price - price_24h_ago) / price_24h_ago * 100
                
                # Calculate volume change
                current_volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].mean()
                volume_change_pct = (current_volume - avg_volume) / avg_volume * 100
                
                # Calculate volatility (standard deviation of returns)
                returns = df['close'].pct_change().dropna()
                volatility = returns.std() * 100
                
                # Calculate trend (simple moving averages)
                df['sma_short'] = df['close'].rolling(window=6).mean()  # 6-hour SMA
                df['sma_long'] = df['close'].rolling(window=12).mean()  # 12-hour SMA
                
                # Check if short SMA is above long SMA (bullish)
                is_bullish = df['sma_short'].iloc[-1] > df['sma_long'].iloc[-1]
                
                # Update scores
                # Price momentum: -25 to +25 points
                price_momentum_score += min(max(price_change_pct, -25), 25)
                
                # Volume: 0 to 20 points
                volume_score += min(max(volume_change_pct / 5, 0), 20)
                
                # Volatility: 0 to 15 points (lower volatility is better)
                volatility_score += max(15 - volatility, 0)
                
                # Trend: 0 or 15 points
                trend_score += 15 if is_bullish else 0
            
            # Average scores across symbols
            if symbols:
                price_momentum_score /= len(symbols)
                volume_score /= len(symbols)
                volatility_score /= len(symbols)
                trend_score /= len(symbols)
            
            # Calculate final score (0-100)
            # Price momentum: 40% weight
            # Volume: 20% weight
            # Volatility: 15% weight
            # Trend: 25% weight
            
            # Normalize price momentum to 0-40 range
            normalized_momentum = (price_momentum_score + 25) / 50 * 40
            
            final_score = normalized_momentum + volume_score + volatility_score + trend_score
            final_score = min(max(int(final_score), 0), 100)
            
            # Update market condition score
            self.market_condition_score = final_score
            
            # Update trading status based on score
            self._update_trading_status()
            
            logger.info(f"Market condition score updated: {final_score}/100")
            return final_score
            
        except Exception as e:
            logger.error(f"Error updating market condition: {str(e)}")
            return self.market_condition_score
    
    def _update_trading_status(self):
        """Update trading status based on market condition score"""
        # If trading is inactive but score is above auto-resume threshold, resume trading
        if not self.is_trading_active and self.market_condition_score >= self.auto_resume_threshold:
            self.is_trading_active = True
            logger.info(f"Trading automatically resumed (score: {self.market_condition_score})")
        
        # If trading is active but score is below minimum threshold, suspend trading
        elif self.is_trading_active and self.market_condition_score < self.min_market_condition_score:
            self.is_trading_active = False
            logger.info(f"Trading automatically suspended (score: {self.market_condition_score})")
    
    def get_active_trades(self) -> Dict:
        """Get all active trades"""
        return self.active_trades
    
    def get_market_status(self) -> Dict:
        """Get current market status"""
        return {
            'market_condition_score': self.market_condition_score,
            'is_trading_active': self.is_trading_active,
            'min_market_condition_score': self.min_market_condition_score,
            'auto_resume_threshold': self.auto_resume_threshold,
            'trading_mode': self.trading_mode
        }
    
    def set_trading_status(self, active: bool) -> Dict:
        """Manually set trading status"""
        self.is_trading_active = active
        logger.info(f"Trading {'activated' if active else 'deactivated'} manually")
        return self.get_market_status()
    
    def get_balance(self) -> Dict:
        """Get account balance"""
        try:
            if self.trading_mode == 'live':
                return self.exchange.fetch_balance()
            else:
                # Return simulated balance for paper trading
                return {
                    'total': {'USDT': 10000, 'BTC': 0.1, 'ETH': 1.0},
                    'free': {'USDT': 5000, 'BTC': 0.05, 'ETH': 0.5},
                    'used': {'USDT': 5000, 'BTC': 0.05, 'ETH': 0.5},
                    'info': {'paper_trading': True}
                }
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return {}
