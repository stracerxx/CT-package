import React from 'react';
import styled, { createGlobalStyle } from 'styled-components';

// Global styles for the retro 80s theme
const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
  
  :root {
    --primary-color: #ff6b6b;
    --secondary-color: #00ff00;
    --dark-bg: #222;
    --darker-bg: #111;
    --light-text: #fff;
    --highlight: #ffdd59;
    --border-color: #4a6fa5;
  }
  
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    font-family: 'VT323', monospace;
    background-color: var(--darker-bg);
    color: var(--light-text);
    font-size: 16px;
    line-height: 1.5;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Press Start 2P', cursive;
    margin-bottom: 1rem;
    line-height: 1.3;
  }
  
  h1 {
    font-size: 1.8rem;
    color: var(--primary-color);
    text-shadow: 3px 3px 0 #000;
  }
  
  h2 {
    font-size: 1.4rem;
    color: var(--secondary-color);
    text-shadow: 2px 2px 0 #000;
  }
  
  h3 {
    font-size: 1.2rem;
    color: var(--highlight);
    text-shadow: 2px 2px 0 #000;
  }
  
  button {
    font-family: 'Press Start 2P', cursive;
    cursor: pointer;
  }
  
  input, select {
    font-family: 'VT323', monospace;
  }
`;

// Pixel border mixin
const pixelBorder = (color = 'var(--border-color)', size = '4px') => `
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -${size};
    left: -${size};
    right: -${size};
    bottom: -${size};
    background: transparent;
    border: ${size} solid ${color};
    pointer-events: none;
    image-rendering: pixelated;
    clip-path: polygon(
      0% 0%, ${size} 0%, ${size} ${size}, calc(100% - ${size}) ${size}, 
      calc(100% - ${size}) calc(100% - ${size}), ${size} calc(100% - ${size}), 
      ${size} 100%, 0% 100%,
      0% calc(100% - ${size}), 0% ${size}
    );
  }
`;

// Styled components for the retro UI
const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px;
  background-color: var(--dark-bg);
  ${pixelBorder('var(--primary-color)')}
  
  h1 {
    margin-bottom: 0;
  }
`;

const Button = styled.button`
  padding: 10px 15px;
  background-color: var(--primary-color);
  color: var(--light-text);
  border: none;
  font-size: 14px;
  text-transform: uppercase;
  transition: all 0.3s ease;
  position: relative;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 0 #000;
  }
  
  &:active {
    transform: translateY(2px);
    box-shadow: none;
  }
  
  ${props => props.secondary && `
    background-color: var(--dark-bg);
    border: 2px solid var(--primary-color);
  `}
  
  ${props => props.success && `
    background-color: var(--secondary-color);
    color: #000;
  `}
`;

const Card = styled.div`
  background-color: var(--dark-bg);
  padding: 20px;
  margin-bottom: 20px;
  ${pixelBorder()}
  
  ${props => props.highlight && `
    ${pixelBorder('var(--highlight)')}
  `}
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const PixelIcon = styled.div`
  width: 24px;
  height: 24px;
  background-color: ${props => props.color || 'var(--primary-color)'};
  mask-image: url(${props => props.icon});
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
`;

const ToggleSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 60px;
  height: 30px;

  input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  span {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #222;
    transition: 0.4s;
    border-radius: 30px;
    box-shadow: 0 2px 8px #000a;
  }

  span:before {
    position: absolute;
    content: "";
    height: 22px;
    width: 22px;
    left: 4px;
    bottom: 4px;
    background-color: #fff;
    transition: 0.4s;
    border-radius: 50%;
    box-shadow: 0 0 4px #000a;
  }

  input:checked + span {
    background-color: #00ff99;
}

input:checked + span:before {
  transform: translateX(30px);
  background-color: #fff;
}
`;
const ProgressBar = styled.div`
width: 100%;
height: 20px;
background-color: #444;
position: relative;

&::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: ${props => props.value || 0}%;
  background-color: ${props => {
    if (props.value < 30) return 'red';
    if (props.value < 70) return 'yellow';
    return 'var(--secondary-color)';
  }};
  transition: width 0.5s ease;
}
`;

const PixelTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 2px solid #444;
  }
  
  th {
    background-color: var(--dark-bg);
    color: var(--primary-color);
    font-family: 'Press Start 2P', cursive;
    font-size: 12px;
  }
  
  tr:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }
`;

// Export all components
export {
  GlobalStyle,
  Container,
  Header,
  Button,
  Card,
  Grid,
  PixelIcon,
  ToggleSwitch,
  ProgressBar,
  PixelTable
};
