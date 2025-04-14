import styled, { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  body { background: #000; color: #fff; }
  h1, h2, h3 {
    font-family: 'Press Start 2P', cursive;
    text-shadow: 2px 2px 0 #222;
    margin-bottom: 0.3rem;
  }
  h1 { color: #ff3333; font-size: 1.8rem; }
  h2 { color: #00ff00; font-size: 1.2rem; }
  h3 { color: #ffdd00; font-size: 1.05rem; }
`;

export const Container = styled.div`
  max-width: 1200px;
  margin: 30px auto 0 auto;
  padding: 24px 32px 32px 32px;
  background: #111;
  border: 4px double #00ffea;
  border-radius: 12px;
  box-shadow: 0 0 24px #00ffea44;
`;

export const Header = styled.header`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 18px;
  margin-bottom: 10px;
  padding: 10px 16px;
  background-color: #111;
  border: 2px solid #ff3333;
  border-radius: 8px;
  h1 {
    margin-bottom: 0;
    color: #ff3333;
    text-transform: uppercase;
    font-family: 'Press Start 2P', cursive;
  }
`;

export const Button = styled.button`
  padding: 8px 12px;
  background-color: #ff3333;
  color: #fff;
  border: none;
  font-size: 12px;
  text-transform: uppercase;
  font-family: 'Press Start 2P', cursive;
  border-radius: 4px;
  margin-right: 8px;
  box-shadow: 0 0 4px #ff3333;
  &:hover {
    filter: brightness(1.2);
  }
  &:active {
    filter: brightness(0.8);
  }
`;

export const Card = styled.div`
  background-color: #1a1a1a;
  padding: 14px 18px;
  margin-bottom: 10px;
  border: 2px solid #00ff00;
  border-radius: 8px;
  box-shadow: 0 0 8px #00ff0044;
`;

export const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 12px;
`;

export const PixelIcon = styled.div``;

// Retro toggle switch (styled label + input + span)
export const ToggleSwitchWrapper = styled.label`
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
  margin: 0 8px;
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
    border: 2px solid #00ff00;
    border-radius: 12px;
    transition: background 0.2s;
  }
  span:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 2px;
    bottom: 2px;
    background-color: #888;
    border-radius: 50%;
    transition: 0.2s;
    box-shadow: 0 0 2px #00ff00;
  }
  input:checked + span {
    background-color: #111;
    border-color: #00ff00;
  }
  input:checked + span:before {
    left: 22px;
    background-color: #00ff00;
  }
`;

export const ProgressBar = styled.div``;
export const PixelTable = styled.table``;

// Stubs for AI components
export const RetroPanel = styled.div`
  background: #222;
  border: 2px solid #00ffea;
  border-radius: 8px;
  padding: 14px 18px;
  margin: 10px 0;
  box-shadow: 0 0 8px #00ffea55;
`;

export const RetroText = styled.span`
  font-family: 'Press Start 2P', monospace;
  color: #00ffea;
  font-size: 1rem;
  margin: 0 4px;
`;

export const RetroButton = styled.button`
  background: #00ffea;
  color: #222;
  border: 2px solid #00ffea;
  border-radius: 4px;
  font-family: 'Press Start 2P', monospace;
  padding: 8px 16px;
  margin: 0 8px;
  cursor: pointer;
  transition: background 0.2s;
  &:hover {
    background: #222;
    color: #00ffea;
  }
`;

export const RetroToggle = styled.input.attrs({ type: 'checkbox' })`
  accent-color: #00ffea;
  width: 20px;
  height: 20px;
  margin-left: 8px;
`;
