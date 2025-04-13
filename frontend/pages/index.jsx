import React from 'react';
import { GlobalStyle } from '../styles/RetroTheme';
import Dashboard from '../components/Dashboard';
import RssFeedSection from '../components/RssFeedSection';
import ChatBubble from '../components/ChatBubble';

const HomePage = () => {
  return (
    <>
      <GlobalStyle />
      <Dashboard />
      <RssFeedSection />
      <ChatBubble />
    </>
  );
};

export default HomePage;
