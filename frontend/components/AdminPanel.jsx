import React, { useState, useEffect } from 'react';
import FullscreenGifBackground from './FullscreenGifBackground';
import ScanlineOverlay from './ScanlineOverlay';
import SparkOverlay from './SparkOverlay';
import ErrorBoundary from './ErrorBoundary';
import { 
  Container, 
  Header, 
  Button, 
  Card, 
  PixelTable
} from '../styles/RetroTheme';

const AdminPanel = () => {
  const [layoutVariant, setLayoutVariant] = useState(null);
  useEffect(() => {
    setLayoutVariant(Math.floor(Math.random() * 3));
  }, []);
  const [users, setUsers] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [systemPrompts, setSystemPrompts] = useState([]);
  const [rssFeeds, setRssFeeds] = useState([]);
  const [activeTab, setActiveTab] = useState('users');
  const [wallets, setWallets] = useState({});
  const [selectedChain, setSelectedChain] = useState('ethereum');
  const [newWalletAddress, setNewWalletAddress] = useState('');
  const [error, setError] = useState(null);
  const [newApiKey, setNewApiKey] = useState({ service: '', api_key: '' });
  const [newPrompt, setNewPrompt] = useState({ name: '', content: '' });
  const [newFeed, setNewFeed] = useState({ name: '', url: '', category: '' });

  if (layoutVariant === null) return null;

  const renderAdminContent = () => (
    <>
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
        <Button onClick={() => setActiveTab('users')} secondary={activeTab !== 'users'}>USERS</Button>
        <Button onClick={() => setActiveTab('apiKeys')} secondary={activeTab !== 'apiKeys'}>API KEYS</Button>
        <Button onClick={() => setActiveTab('systemPrompts')} secondary={activeTab !== 'systemPrompts'}>SYSTEM PROMPTS</Button>
        <Button onClick={() => setActiveTab('rssFeeds')} secondary={activeTab !== 'rssFeeds'}>RSS FEEDS</Button>
        <Button onClick={() => setActiveTab('wallets')} secondary={activeTab !== 'wallets'}>WALLETS</Button>
      </div>
      {activeTab === 'users' && (
        <Card>
          <h2>Users</h2>
          <form
            onSubmit={e => {
              e.preventDefault();
              setUsers(prev => [...prev, { username: newPrompt.name, email: newPrompt.content }]);
              setNewPrompt({ ...newPrompt, name: '', content: '' });
              setError('Backend unavailable, using local state for demo.');
            }}
            style={{ marginBottom: '16px' }}
          >
            <input
              type="text"
              placeholder="Username"
              value={newPrompt.name}
              onChange={e => setNewPrompt({ ...newPrompt, name: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <input
              type="email"
              placeholder="Email"
              value={newPrompt.content}
              onChange={e => setNewPrompt({ ...newPrompt, content: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <Button type="submit">Add User</Button>
          </form>
          {users.length === 0 ? <p>No users found.</p> : (
            <PixelTable>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, idx) => (
                  <tr key={idx}>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>
                      <Button onClick={() => {
                        setUsers(prev => prev.filter((_, i) => i !== idx));
                        setError('Backend unavailable, using local state for demo.');
                      }}>Delete</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </PixelTable>
          )}
        </Card>
      )}
      {activeTab === 'apiKeys' && (
        <Card>
          <h2>API Keys</h2>
          <form
            onSubmit={e => {
              e.preventDefault();
              setApiKeys(prev => [...prev, { ...newApiKey }]);
              setNewApiKey({ service: '', api_key: '' });
              setError('Backend unavailable, using local state for demo.');
            }}
            style={{ marginBottom: '16px' }}
          >
            <input
              type="text"
              placeholder="Service"
              value={newApiKey.service}
              onChange={e => setNewApiKey({ ...newApiKey, service: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <input
              type="text"
              placeholder="API Key"
              value={newApiKey.api_key}
              onChange={e => setNewApiKey({ ...newApiKey, api_key: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <Button type="submit">Add API Key</Button>
          </form>
          {apiKeys.length === 0 ? <p>No API keys found.</p> : (
            <PixelTable>
              <thead>
                <tr>
                  <th>Service</th>
                  <th>API Key</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {apiKeys.map((key, idx) => (
                  <tr key={idx}>
                    <td>{key.service}</td>
                    <td>{key.api_key}</td>
                    <td>
                      <Button onClick={() => {
                        setApiKeys(prev => prev.filter((_, i) => i !== idx));
                        setError('Backend unavailable, using local state for demo.');
                      }}>Delete</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </PixelTable>
          )}
        </Card>
      )}
      {activeTab === 'systemPrompts' && (
        <Card>
          <h2>System Prompts</h2>
          <form
            onSubmit={e => {
              e.preventDefault();
              setSystemPrompts(prev => [...prev, { name: newPrompt.name, content: newPrompt.content }]);
              setNewPrompt({ ...newPrompt, name: '', content: '' });
              setError('Backend unavailable, using local state for demo.');
            }}
            style={{ marginBottom: '16px' }}
          >
            <input
              type="text"
              placeholder="Prompt Name"
              value={newPrompt.name}
              onChange={e => setNewPrompt({ ...newPrompt, name: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <input
              type="text"
              placeholder="Prompt Content"
              value={newPrompt.content}
              onChange={e => setNewPrompt({ ...newPrompt, content: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <Button type="submit">Add Prompt</Button>
          </form>
          {systemPrompts.length === 0 ? <p>No prompts found.</p> : (
            <PixelTable>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Content</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {systemPrompts.map((prompt, idx) => (
                  <tr key={idx}>
                    <td>{prompt.name}</td>
                    <td>{prompt.content}</td>
                    <td>
                      <Button onClick={() => {
                        setSystemPrompts(prev => prev.filter((_, i) => i !== idx));
                        setError('Backend unavailable, using local state for demo.');
                      }}>Delete</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </PixelTable>
          )}
        </Card>
      )}
      {activeTab === 'rssFeeds' && (
        <Card>
          <h2>RSS Feeds</h2>
          <form
            onSubmit={e => {
              e.preventDefault();
              setRssFeeds(prev => [...prev, { name: newFeed.name, url: newFeed.url, category: newFeed.category }]);
              setNewFeed({ name: '', url: '', category: '' });
              setError('Backend unavailable, using local state for demo.');
            }}
            style={{ marginBottom: '16px' }}
          >
            <input
              type="text"
              placeholder="Feed Name"
              value={newFeed.name}
              onChange={e => setNewFeed({ ...newFeed, name: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <input
              type="text"
              placeholder="Feed URL"
              value={newFeed.url}
              onChange={e => setNewFeed({ ...newFeed, url: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <input
              type="text"
              placeholder="Category"
              value={newFeed.category}
              onChange={e => setNewFeed({ ...newFeed, category: e.target.value })}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <Button type="submit">Add Feed</Button>
          </form>
          {rssFeeds.length === 0 ? <p>No RSS feeds found.</p> : (
            <PixelTable>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>URL</th>
                  <th>Category</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rssFeeds.map((feed, idx) => (
                  <tr key={idx}>
                    <td>{feed.name}</td>
                    <td>{feed.url}</td>
                    <td>{feed.category}</td>
                    <td>
                      <Button onClick={() => {
                        setRssFeeds(prev => prev.filter((_, i) => i !== idx));
                        setError('Backend unavailable, using local state for demo.');
                      }}>Delete</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </PixelTable>
          )}
        </Card>
      )}
      {activeTab === 'wallets' && (
        <Card>
          <h2>Wallets</h2>
          <form
            onSubmit={e => {
              e.preventDefault();
              setWallets(prev => ({
                ...prev,
                [selectedChain]: newWalletAddress
              }));
              setNewWalletAddress('');
              setError('Backend unavailable, using local state for demo.');
            }}
            style={{ marginBottom: '16px' }}
          >
            <select
              value={selectedChain}
              onChange={e => setSelectedChain(e.target.value)}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
            >
              <option value="ethereum">Ethereum</option>
              <option value="bsc">BSC</option>
              <option value="polygon">Polygon</option>
            </select>
            <input
              type="text"
              placeholder="Wallet Address"
              value={newWalletAddress}
              onChange={e => setNewWalletAddress(e.target.value)}
              style={{ marginRight: 8, padding: 4, fontFamily: "'VT323', monospace" }}
              required
            />
            <Button type="submit">Add Wallet</Button>
          </form>
          {Object.keys(wallets).length === 0 ? <p>No wallets found.</p> : (
            <PixelTable>
              <thead>
                <tr>
                  <th>Chain</th>
                  <th>Address</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(wallets).map(([chain, address], idx) => (
                  <tr key={idx}>
                    <td>{chain}</td>
                    <td>{address}</td>
                    <td>
                      <Button onClick={() => {
                        setWallets(prev => {
                          const copy = { ...prev };
                          delete copy[chain];
                          return copy;
                        });
                        setError('Backend unavailable, using local state for demo.');
                      }}>Delete</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </PixelTable>
          )}
        </Card>
      )}
    </>
  );

  return (
    <ErrorBoundary>
      <FullscreenGifBackground gifUrl="https://media.tenor.com/1bSue8.gif" show={false} />
      <ScanlineOverlay />
      <SparkOverlay color="green" />
      <Container>
        {layoutVariant === 0 && (
          <div>
            {renderAdminContent()}
          </div>
        )}
        {layoutVariant === 1 && (
          <div>
            {renderAdminContent()}
          </div>
        )}
        {layoutVariant === 2 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px' }}>
            {renderAdminContent()}
          </div>
        )}
      </Container>
    </ErrorBoundary>
  );
};

export default AdminPanel;
