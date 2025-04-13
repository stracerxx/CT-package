import React, { useState, useEffect } from 'react';
import WalletConnectProvider from "@walletconnect/web3-provider";
import {
  Container,
  Header,
  Button,
  Card,
  Grid,
  ToggleSwitch,
  ProgressBar,
  PixelTable
} from '../styles/RetroTheme';
import axios from 'axios';

// 8-bit sound effects
const clickSound = typeof window !== "undefined" ? new Audio('/click.wav') : null;
const toggleSound = typeof window !== "undefined" ? new Audio('/toggle.wav') : null;

const Dashboard = () => {
  const [marketCondition, setMarketCondition] = useState(0);
  const [activeTrades, setActiveTrades] = useState([]);
  const [strategies, setStrategies] = useState({
    grid: false,
    scalping: false,
    swing: false,
    dca: false,
    momentum: false,
    arbitrage: false
  });
  const [perpetualMode, setPerpetualMode] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // WalletConnect state
  const [walletProvider, setWalletProvider] = useState(null);
  const [walletAddress, setWalletAddress] = useState(null);

  // Fetch data on component mount
  useEffect(() => {
    fetchDashboardData();
    // Set up polling for regular updates
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval); // Clean up on unmount
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      // Fetch market condition
      const marketResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/trading/market-condition`);
      setMarketCondition(marketResponse.data.score);
      setPerpetualMode(marketResponse.data.is_trading_active);
      
      // Fetch active trades
      const tradesResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/trading/active-trades`);
      setActiveTrades(tradesResponse.data.trades);
      
      // Fetch strategy statuses
      const strategiesResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/trading/strategies`);
      setStrategies(strategiesResponse.data.strategies);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleStrategy = async (strategy) => {
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/trading/strategies/${strategy}/toggle`);
      setStrategies({
        ...strategies,
        [strategy]: !strategies[strategy]
      });
    } catch (err) {
      console.error(`Error toggling ${strategy} strategy:`, err);
      setError(`Failed to toggle ${strategy} strategy. Please try again.`);
    }
  };

  const togglePerpetualMode = async () => {
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/trading/perpetual-mode/toggle`);
      setPerpetualMode(!perpetualMode);
    } catch (err) {
      console.error('Error toggling perpetual mode:', err);
      setError('Failed to toggle perpetual mode. Please try again.');
    }
  };

  const getMarketConditionLabel = (score) => {
    if (score < 30) return 'BEARISH';
    if (score < 50) return 'NEUTRAL';
    if (score < 70) return 'BULLISH';
    return 'VERY BULLISH';
  };

  // WalletConnect logic
  const connectWallet = async () => {
    try {
      const provider = new WalletConnectProvider({
        rpc: {
          1: "https://mainnet.infura.io/v3/..." // Replace with your Infura ID or other RPC
        }
      });
      await provider.enable();
      setWalletProvider(provider);

      // Get accounts
      const accounts = provider.accounts || (provider.wc && provider.wc.accounts) || [];
      setWalletAddress(accounts[0] || null);

      // Listen for account changes
      provider.on("accountsChanged", (accounts) => {
        setWalletAddress(accounts[0] || null);
      });
      provider.on("disconnect", () => {
        setWalletProvider(null);
        setWalletAddress(null);
      });
    } catch (err) {
      setError("Failed to connect wallet.");
      console.error("WalletConnect error:", err);
    }
  };

  return (
    <Container>
      <Header>
        <h1>CT-5 TRADING DASHBOARD</h1>
        <div style={{ display: "flex", gap: "10px" }}>
          {walletAddress ? (
            <Button secondary>
              Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
            </Button>
          ) : (
            <Button onClick={connectWallet}>Connect Wallet</Button>
          )}
          <Button onClick={() => { if (clickSound) clickSound.play(); fetchDashboardData(); }}>REFRESH</Button>
        </div>
      </Header>

      {error && (
        <Card highlight>
          <h3>ERROR</h3>
          <p>{error}</p>
        </Card>
      )}

      <Grid>
        {/* Market Condition Card */}
        <Card>
          <h2>MARKET CONDITION</h2>
          <div style={{ marginBottom: '10px' }}>
            <ProgressBar value={marketCondition} />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
              <span>0</span>
              <span style={{
                color: marketCondition < 30 ? 'red' :
                       marketCondition < 50 ? 'yellow' :
                       marketCondition < 70 ? 'lightgreen' : 'var(--secondary-color)',
                fontWeight: 'bold'
              }}>
                {getMarketConditionLabel(marketCondition)} ({marketCondition})
              </span>
              <span>100</span>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '20px' }}>
            <h3>PERPETUAL MODE</h3>
            <ToggleSwitch>
              <input
                type="checkbox"
                checked={perpetualMode}
                onChange={e => { if (toggleSound) toggleSound.play(); togglePerpetualMode(e); }}
              />
              <span></span>
            </ToggleSwitch>
          </div>
          <p style={{ marginTop: '10px', fontSize: '14px' }}>
            {perpetualMode
              ? "Perpetual Earning Mode is ACTIVE. Trading automatically based on market conditions."
              : "Perpetual Earning Mode is INACTIVE. Trading suspended."}
          </p>
        </Card>

        {/* Trading Strategies Card */}
        <Card>
          <h2>TRADING STRATEGIES</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {Object.entries(strategies).map(([strategy, isActive]) => (
              <div key={strategy} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <h3 style={{ marginBottom: '5px', textTransform: 'uppercase' }}>{strategy}</h3>
                  <p style={{ fontSize: '14px' }}>
                    {isActive ? "ACTIVE" : "INACTIVE"}
                  </p>
                </div>
                <ToggleSwitch>
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={() => { if (toggleSound) toggleSound.play(); toggleStrategy(strategy); }}
                  />
                  <span></span>
                </ToggleSwitch>
              </div>
            ))}
          </div>
        </Card>
      </Grid>

      {/* Active Trades Table */}
      <Card>
        <h2>ACTIVE TRADES</h2>
        
        {activeTrades.length === 0 ? (
          <p>No active trades at the moment.</p>
        ) : (
          <PixelTable>
            <thead>
              <tr>
                <th>SYMBOL</th>
                <th>STRATEGY</th>
                <th>SIDE</th>
                <th>AMOUNT</th>
                <th>ENTRY PRICE</th>
                <th>CURRENT PRICE</th>
                <th>P/L %</th>
              </tr>
            </thead>
            <tbody>
              {activeTrades.map((trade, index) => {
                const profitLoss = ((trade.current_price - trade.entry_price) / trade.entry_price) * 100;
                const isProfitable = profitLoss > 0;
                
                return (
                  <tr key={index}>
                    <td>{trade.symbol}</td>
                    <td>{trade.strategy}</td>
                    <td>{trade.side.toUpperCase()}</td>
                    <td>{trade.amount.toFixed(6)}</td>
                    <td>${trade.entry_price.toFixed(2)}</td>
                    <td>${trade.current_price.toFixed(2)}</td>
                    <td style={{ color: isProfitable ? 'var(--secondary-color)' : 'red' }}>
                      {isProfitable ? '+' : ''}{profitLoss.toFixed(2)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </PixelTable>
        )}
      </Card>
    </Container>
  );
};

export default Dashboard;
