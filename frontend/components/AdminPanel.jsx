import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Header, 
  Button, 
  Card, 
  Grid, 
  PixelTable,
  ToggleSwitch
} from '../styles/RetroTheme';
import axios from 'axios';

const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [systemPrompts, setSystemPrompts] = useState([]);
  const [rssFeeds, setRssFeeds] = useState([]);
  const [activeTab, setActiveTab] = useState('users');
  // Wallet management state
  const [wallets, setWallets] = useState({});
  const [balances, setBalances] = useState({});
  const [profits, setProfits] = useState({});
  const [selectedChain, setSelectedChain] = useState('ethereum');
  const [newWalletAddress, setNewWalletAddress] = useState('');
  const [profitAmount, setProfitAmount] = useState('');
  const supportedChains = ['ethereum', 'bsc', 'polygon'];
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Form states
  const [newApiKey, setNewApiKey] = useState({ service: '', api_key: '' });
  const [newPrompt, setNewPrompt] = useState({ name: '', content: '', is_active: false });
  const [newFeed, setNewFeed] = useState({ name: '', url: '', category: '' });

  // useEffect(() => {
  //   // Load data based on active tab
  //   fetchTabData(activeTab);
  //   if (activeTab === 'wallets') {
  //     fetchWallets();
  //   }
  // }, [activeTab]);

  const fetchTabData = async (tab) => {
    setIsLoading(true);
    try {
      switch(tab) {
        case 'users':
          await fetchUsers();
          break;
        case 'apiKeys':
          await fetchApiKeys();
          break;
        case 'systemPrompts':
          await fetchSystemPrompts();
          break;
        case 'rssFeeds':
          await fetchRssFeeds();
          break;
      }
      setError(null);
    } catch (err) {
      console.error(`Error fetching ${tab} data:`, err);
      setError(`Failed to load ${tab} data. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  // Wallet management handlers
  const fetchWallets = async () => {
    try {
      let w = {};
      let b = {};
      let p = {};
      for (const chain of supportedChains) {
        // Get wallet address
        const addrRes = await axios.get(`/api/wallet/address?chain=${chain}`);
        w[chain] = addrRes.data.address;
        // Get balance
        const balRes = await axios.get(`/api/wallet/balance?chain=${chain}`);
        b[chain] = balRes.data.balance;
        // Get profit
        const profRes = await axios.get(`/api/wallet/profit?chain=${chain}`);
        p[chain] = profRes.data.profit;
      }
      setWallets(w);
      setBalances(b);
      setProfits(p);
    } catch (err) {
      setError('Failed to load wallet data. Please try again.');
    }
  };

  const handleCreateWallet = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`/api/wallet/create?chain=${selectedChain}`);
      setNewWalletAddress(res.data.address);
      fetchWallets();
    } catch (err) {
      setError('Failed to create wallet. Please try again.');
    }
  };

  const handleAddProfit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/wallet/profit/add?chain=${selectedChain}&amount=${profitAmount}`);
      setProfitAmount('');
      fetchWallets();
    } catch (err) {
      setError('Failed to add profit. Please try again.');
    }
  };

  const handleWithdrawProfit = async (toAddress, amount) => {
    try {
      await axios.post(`/api/wallet/profit/withdraw?chain=${selectedChain}&to_address=${toAddress}&amount=${amount}`);
      fetchWallets();
    } catch (err) {
      setError('Failed to withdraw profit. Please try again.');
    }
  };

  const fetchUsers = async () => {
    const response = await axios.get('/api/auth/users');
    setUsers(response.data);
  };

  const fetchApiKeys = async () => {
    const response = await axios.get('/api/keys');
    setApiKeys(response.data);
  };

  const fetchSystemPrompts = async () => {
    const response = await axios.get('/api/system');
    setSystemPrompts(response.data);
  };

  const fetchRssFeeds = async () => {
    const response = await axios.get('/api/rss');
    setRssFeeds(response.data);
  };

  const handleAddApiKey = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/keys', newApiKey);
      setNewApiKey({ service: '', api_key: '' });
      fetchApiKeys();
    } catch (err) {
      setError('Failed to add API key. Please try again.');
    }
  };

  const handleAddSystemPrompt = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/system', newPrompt);
      setNewPrompt({ name: '', content: '', is_active: false });
      fetchSystemPrompts();
    } catch (err) {
      setError('Failed to add system prompt. Please try again.');
    }
  };

  const handleAddRssFeed = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/rss', newFeed);
      setNewFeed({ name: '', url: '', category: '' });
      fetchRssFeeds();
    } catch (err) {
      setError('Failed to add RSS feed. Please try again.');
    }
  };

  const setActiveSystemPrompt = async (id) => {
    try {
      await axios.put(`/api/system/${id}`, { is_active: true });
      fetchSystemPrompts();
    } catch (err) {
      setError('Failed to set active system prompt. Please try again.');
    }
  };

  const deleteApiKey = async (service) => {
    try {
      await axios.delete(`/api/keys/${service}`);
      fetchApiKeys();
    } catch (err) {
      setError('Failed to delete API key. Please try again.');
    }
  };

  const deleteSystemPrompt = async (id) => {
    try {
      await axios.delete(`/api/system/${id}`);
      fetchSystemPrompts();
    } catch (err) {
      setError('Failed to delete system prompt. Please try again.');
    }
  };

  const deleteRssFeed = async (id) => {
    try {
      await axios.delete(`/api/rss/${id}`);
      fetchRssFeeds();
    } catch (err) {
      setError('Failed to delete RSS feed. Please try again.');
    }
  };

  const toggleRssFeedStatus = async (id, isActive) => {
    try {
      await axios.put(`/api/rss/${id}`, { is_active: !isActive });
      fetchRssFeeds();
    } catch (err) {
      setError('Failed to toggle RSS feed status. Please try again.');
    }
  };

  return (
    <Container>
      <Header>
        <h1>CT-5 ADMIN PANEL</h1>
      </Header>

      {error && (
        <Card highlight>
          <h3>ERROR</h3>
          <p>{error}</p>
        </Card>
      )}

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <Button
          onClick={() => setActiveTab('users')}
          secondary={activeTab !== 'users'}
        >
          USERS
        </Button>
        <Button
          onClick={() => setActiveTab('apiKeys')}
          secondary={activeTab !== 'apiKeys'}
        >
          API KEYS
        </Button>
        <Button
          onClick={() => setActiveTab('systemPrompts')}
          secondary={activeTab !== 'systemPrompts'}
        >
          SYSTEM PROMPTS
        </Button>
        <Button
          onClick={() => setActiveTab('rssFeeds')}
          secondary={activeTab !== 'rssFeeds'}
        >
          RSS FEEDS
        </Button>
        <Button
          onClick={() => setActiveTab('wallets')}
          secondary={activeTab !== 'wallets'}
        >
          WALLETS
        </Button>
        <Button
          onClick={() => setActiveTab('wallets')}
          secondary={activeTab !== 'wallets'}
        >
          WALLETS
        </Button>
      </div>
      <Button
        onClick={() => setActiveTab('wallets')}
        secondary={activeTab !== 'wallets'}
      >
        WALLETS
      </Button>

      {isLoading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <h3>LOADING...</h3>
          </div>
        </Card>
      ) : (
        <>
          {/* Users Tab */}
          {activeTab === 'users' && (
            <Card>
              <h2>USERS</h2>
              <PixelTable>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>USERNAME</th>
                    <th>EMAIL</th>
                    <th>ADMIN</th>
                    <th>ACTIVE</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{user.is_admin ? 'Yes' : 'No'}</td>
                      <td>{user.is_active ? 'Yes' : 'No'}</td>
                    </tr>
                  ))}
                </tbody>
              </PixelTable>
            </Card>
          )}

          {/* API Keys Tab */}
          {activeTab === 'apiKeys' && (
            <>
              <Card>
                <h2>API KEYS</h2>
                <PixelTable>
                  <thead>
                    <tr>
                      <th>SERVICE</th>
                      <th>API KEY</th>
                      <th>ACTIVE</th>
                      <th>ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {apiKeys.map(key => (
                      <tr key={key.id}>
                        <td>{key.service}</td>
                        <td>{key.api_key.substring(0, 8)}...</td>
                        <td>{key.is_active ? 'Yes' : 'No'}</td>
                        <td>
                          <Button onClick={() => deleteApiKey(key.service)}>DELETE</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </PixelTable>
              </Card>

              <Card>
                <h2>ADD NEW API KEY</h2>
                <form onSubmit={handleAddApiKey}>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Service:</label>
                    <select 
                      value={newApiKey.service}
                      onChange={(e) => setNewApiKey({...newApiKey, service: e.target.value})}
                      style={{ 
                        width: '100%', 
                        padding: '8px', 
                        backgroundColor: '#333',
                        color: 'white',
                        border: '2px solid var(--primary-color)'
                      }}
                      required
                    >
                      <option value="">Select Service</option>
                      <option value="openai">OpenAI</option>
                    </select>
                  </div>
                  
                  <Button type="submit">ADD API KEY</Button>
                </form>
              </Card>
            </>
          )}

          {/* System Prompts Tab */}
          {activeTab === 'systemPrompts' && (
            <>
              <Card>
                <h2>SYSTEM PROMPTS</h2>
                <PixelTable>
                  <thead>
                    <tr>
                      <th>NAME</th>
                      <th>ACTIVE</th>
                      <th>ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {systemPrompts.map(prompt => (
                      <tr key={prompt.id}>
                        <td>{prompt.name}</td>
                        <td>{prompt.is_active ? 'Yes' : 'No'}</td>
                        <td style={{ display: 'flex', gap: '5px' }}>
                          {!prompt.is_active && (
                            <Button onClick={() => setActiveSystemPrompt(prompt.id)}>SET ACTIVE</Button>
                          )}
                          <Button onClick={() => deleteSystemPrompt(prompt.id)}>DELETE</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </PixelTable>
              </Card>

              <Card>
                <h2>ADD NEW SYSTEM PROMPT</h2>
                <form onSubmit={handleAddSystemPrompt}>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
                    <input 
                      type="text"
                      value={newPrompt.name}
                      onChange={(e) => setNewPrompt({...newPrompt, name: e.target.value})}
                      style={{ 
                        width: '100%', 
                        padding: '8px', 
                        backgroundColor: '#333',
                        color: 'white',
                        border: '2px solid var(--primary-color)'
                      }}
                      required
                    />
                  </div>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Content:</label>
                    <textarea 
                      value={newPrompt.content}
                      onChange={(e) => setNewPrompt({...newPrompt, content: e.target.value})}
                      style={{ 
                        width: '100%', 
                        height: '200px',
                        padding: '8px', 
                        backgroundColor: '#333',
                        color: 'white',
                        border: '2px solid var(--primary-color)'
                      }}
                      required
                    />
                  </div>
                  
                  <div style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <label>Set as Active:</label>
                    <ToggleSwitch>
                      <input 
                        type="checkbox" 
                        checked={newPrompt.is_active} 
                        onChange={(e) => setNewPrompt({...newPrompt, is_active: e.target.checked})} 
                      />
                      <span></span>
                    </ToggleSwitch>
                  </div>
                  
                  <Button type="submit">ADD SYSTEM PROMPT</Button>
                </form>
              </Card>
            </>
          )}

          {/* RSS Feeds Tab */}
          {activeTab === 'rssFeeds' && (
            <>
              <Card>
                <h2>RSS FEEDS</h2>
                <PixelTable>
                  <thead>
                    <tr>
                      <th>NAME</th>
                      <th>CATEGORY</th>
                      <th>URL</th>
                      <th>ACTIVE</th>
                      <th>ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rssFeeds.map(feed => (
                      <tr key={feed.id}>
                        <td>{feed.name}</td>
                        <td>{feed.category}</td>
                        <td>{feed.url.substring(0, 30)}...</td>
                        <td>
                          <ToggleSwitch>
                            <input 
                              type="checkbox" 
                              checked={feed.is_active} 
                              onChange={() => toggleRssFeedStatus(feed.id, feed.is_active)} 
                            />
                            <span></span>
                          </ToggleSwitch>
                        </td>
                        <td>
                          <Button onClick={() => deleteRssFeed(feed.id)}>DELETE</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </PixelTable>
              </Card>

              <Card>
                <h2>ADD NEW RSS FEED</h2>
                <form onSubmit={handleAddRssFeed}>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
                    <input 
                      type="text"
                      value={newFeed.name}
                      onChange={(e) => setNewFeed({...newFeed, name: e.target.value})}
                      style={{ 
                        width: '100%', 
                        padding: '8px', 
                        backgroundColor: '#333',
                        color: 'white',
                        border: '2px solid var(--primary-color)'
                      }}
                      required
                    />
                  </div>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>URL:</label>
                    <input 
                      type="url"
                      value={newFeed.url}
                      onChange={(e) => setNewFeed({...newFeed, url: e.target.value})}
                      style={{ 
                        width: '100%', 
                        padding: '8px', 
                        backgroundColor: '#333',
                        color: 'white',
                        border: '2px solid var(--primary-color)'
                      }}
                      required
                    />
                  </div>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Category:</label>
                    <input 
                      type="text"
                      value={newFeed.category}
                      onChange={(e) => setNewFeed({...newFeed, category: e.target.value})}
                      style={{ 
                        width: '100%', 
                        padding: '8px', 
                        backgroundColor: '#333',
                        color: 'white',
                        border: '2px solid var(--primary-color)'
                      }}
                      required
                    />
                  </div>
                  
                  <Button type="submit">ADD RSS FEED</Button>
                </form>
              </Card>
            </>
          )}

          {/* Wallets Tab */}
          {activeTab === 'wallets' && (
            <Card>
              <h2>WALLET MANAGEMENT</h2>
              <form onSubmit={handleCreateWallet} style={{ marginBottom: '20px' }}>
                <label>Chain:</label>
                <select value={selectedChain} onChange={e => setSelectedChain(e.target.value)}>
                  {supportedChains.map(chain => (
                    <option key={chain} value={chain}>{chain.toUpperCase()}</option>
                  ))}
                </select>
                <Button type="submit" style={{ marginLeft: 10 }}>Create Wallet</Button>
              </form>
              {newWalletAddress && (
                <div style={{ marginBottom: '20px' }}>
                  <b>New Wallet Address:</b> {newWalletAddress}
                </div>
              )}
              <h3>Wallets & Balances</h3>
              <PixelTable>
                <thead>
                  <tr>
                    <th>CHAIN</th>
                    <th>ADDRESS</th>
                    <th>BALANCE</th>
                    <th>PROFIT</th>
                  </tr>
                </thead>
                <tbody>
                  {supportedChains.map(chain => (
                    <tr key={chain}>
                      <td>{chain.toUpperCase()}</td>
                      <td>{wallets[chain] || '-'}</td>
                      <td>{balances[chain] || '-'}</td>
                      <td>{profits[chain] || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </PixelTable>
              <form onSubmit={handleAddProfit} style={{ marginTop: '20px' }}>
                <label>Add Profit to {selectedChain.toUpperCase()}:</label>
                <input
                  type="number"
                  value={profitAmount}
                  onChange={e => setProfitAmount(e.target.value)}
                  placeholder="Amount"
                  style={{ marginLeft: 10, marginRight: 10 }}
                />
                <Button type="submit">Add Profit</Button>
              </form>
            </Card>
          )}
        </>
      )}
    </Container>
  );
};

export default AdminPanel;
