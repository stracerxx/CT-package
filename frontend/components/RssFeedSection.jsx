import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Card, 
  Grid, 
  PixelTable,
  Button
} from '../styles/RetroTheme';
import axios from 'axios';

const RssFeedSection = () => {
  const [feeds, setFeeds] = useState([]);
  const [feedItems, setFeedItems] = useState([]);
  const [selectedFeed, setSelectedFeed] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch feeds on component mount
  useEffect(() => {
    fetchFeeds();
  }, []);

  // Fetch feed items when a feed is selected
  useEffect(() => {
    if (selectedFeed) {
      fetchFeedItems(selectedFeed);
    }
  }, [selectedFeed]);

  const fetchFeeds = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/rss');
      setFeeds(response.data);
      
      // Select the first feed by default if available
      if (response.data.length > 0 && !selectedFeed) {
        setSelectedFeed(response.data[0].id);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching RSS feeds:', err);
      setError('Failed to load RSS feeds. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchFeedItems = async (feedId) => {
    setIsLoading(true);
    try {
      const response = await axios.get(`/api/rss/${feedId}/items`);
      setFeedItems(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching RSS feed items:', err);
      setError('Failed to load RSS feed items. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshFeed = async () => {
    if (!selectedFeed) return;
    
    setIsLoading(true);
    try {
      await axios.post(`/api/rss/${selectedFeed}/refresh`);
      fetchFeedItems(selectedFeed);
      setError(null);
    } catch (err) {
      console.error('Error refreshing RSS feed:', err);
      setError('Failed to refresh RSS feed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <Container>
      <h2>CRYPTO NEWS FEED</h2>
      
      {error && (
        <Card highlight>
          <h3>ERROR</h3>
          <p>{error}</p>
        </Card>
      )}

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        {feeds.map(feed => (
          <Button 
            key={feed.id}
            onClick={() => setSelectedFeed(feed.id)}
            secondary={selectedFeed !== feed.id}
          >
            {feed.name}
          </Button>
        ))}
        <Button onClick={refreshFeed}>
          REFRESH
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <h3>LOADING...</h3>
            <div style={{ 
              display: 'inline-block', 
              width: '20px', 
              height: '20px', 
              border: '4px solid var(--primary-color)', 
              borderRadius: '50%', 
              borderTopColor: 'transparent', 
              animation: 'spin 1s linear infinite' 
            }}></div>
            <style jsx>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        ) : feedItems.length === 0 ? (
          <p>No items found in this feed.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {feedItems.map((item, index) => (
              <div key={index} style={{ 
                padding: '10px', 
                backgroundColor: 'var(--darker-bg)',
                border: '2px solid #444'
              }}>
                <h3 style={{ fontSize: '16px', marginBottom: '5px' }}>
                  <a href={item.link} target="_blank" rel="noopener noreferrer" style={{ 
                    color: 'var(--primary-color)', 
                    textDecoration: 'none' 
                  }}>
                    {item.title}
                  </a>
                </h3>
                <p style={{ fontSize: '14px', marginBottom: '5px' }}>{item.description}</p>
                <p style={{ fontSize: '12px', color: '#888' }}>
                  Published: {formatDate(item.published_date)}
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </Container>
  );
};

export default RssFeedSection;
