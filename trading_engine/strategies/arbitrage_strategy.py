import logging
from typing import Dict, Any
import ccxt

logger = logging.getLogger('arbitrage_strategy')

class ArbitrageStrategy:
    """
    Arbitrage Trading Strategy

    Detects price differences for a symbol between two exchanges and executes trades to profit from the spread.
    """

    def __init__(self, engine, symbol: str, exchange_a: str, exchange_b: str, threshold_pct: float = 0.5):
        """
        Args:
            engine: TradingEngine instance
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            exchange_a: Name of first exchange (must be supported by ccxt)
            exchange_b: Name of second exchange (must be supported by ccxt)
            threshold_pct: Minimum price difference percentage to trigger arbitrage
        """
        self.engine = engine
        self.symbol = symbol
        self.exchange_a = exchange_a
        self.exchange_b = exchange_b
        self.threshold_pct = threshold_pct

        # Initialize ccxt exchange instances
        self.ex_a = getattr(ccxt, exchange_a)()
        self.ex_b = getattr(ccxt, exchange_b)()

        logger.info(f"Arbitrage Strategy initialized for {symbol} between {exchange_a} and {exchange_b}")

    def get_prices(self) -> Dict[str, float]:
        """Fetch current prices from both exchanges"""
        ticker_a = self.ex_a.fetch_ticker(self.symbol)
        ticker_b = self.ex_b.fetch_ticker(self.symbol)
        return {
            self.exchange_a: ticker_a['last'],
            self.exchange_b: ticker_b['last']
        }

    def analyze_market(self) -> Dict[str, Any]:
        """Analyze price difference and generate arbitrage signal"""
        try:
            prices = self.get_prices()
            price_a = prices[self.exchange_a]
            price_b = prices[self.exchange_b]
            spread = abs(price_a - price_b)
            spread_pct = (spread / min(price_a, price_b)) * 100

            if spread_pct >= self.threshold_pct:
                if price_a < price_b:
                    return {
                        'signal': 'arbitrage',
                        'buy_exchange': self.exchange_a,
                        'sell_exchange': self.exchange_b,
                        'buy_price': price_a,
                        'sell_price': price_b,
                        'spread_pct': spread_pct
                    }
                else:
                    return {
                        'signal': 'arbitrage',
                        'buy_exchange': self.exchange_b,
                        'sell_exchange': self.exchange_a,
                        'buy_price': price_b,
                        'sell_price': price_a,
                        'spread_pct': spread_pct
                    }
            else:
                return {
                    'signal': 'none',
                    'reason': f'Spread {spread_pct:.2f}% below threshold'
                }
        except Exception as e:
            logger.error(f"Error in arbitrage analysis: {e}")
            return {
                'signal': 'error',
                'reason': str(e)
            }

    def execute_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrage trade if signal is present"""
        if signal.get('signal') == 'arbitrage':
            # Placeholder: In production, implement actual trading logic with balances, fees, etc.
            logger.info(f"Arbitrage opportunity: Buy on {signal['buy_exchange']} at {signal['buy_price']}, "
                        f"Sell on {signal['sell_exchange']} at {signal['sell_price']} (Spread: {signal['spread_pct']:.2f}%)")
            return {
                'action': 'arbitrage',
                'details': signal
            }
        else:
            return {
                'action': 'none',
                'reason': signal.get('reason', 'No arbitrage opportunity')
            }

    def run_iteration(self) -> Dict[str, Any]:
        """Run one iteration of the arbitrage strategy"""
        signal = self.analyze_market()
        result = self.execute_signal(signal)
        return result

    def get_status(self) -> Dict[str, Any]:
        """Get current strategy status"""
        return {
            'strategy': 'Arbitrage',
            'symbol': self.symbol,
            'exchange_a': self.exchange_a,
            'exchange_b': self.exchange_b,
            'threshold_pct': self.threshold_pct
        }