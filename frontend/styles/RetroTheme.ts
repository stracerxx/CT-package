import styled from 'styled-components';

export const RetroText = styled.p`
  font-family: 'VT323', monospace;
  color: #00ff00;
  text-shadow: 0 0 10px #00ff00;
`;

export const RetroButton = styled.button`
  background: transparent;
  border: 2px solid #00ff00;
  color: #00ff00;
  padding: 10px 20px;
  font-family: 'VT323', monospace;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #00ff00;
    color: #000;
    box-shadow: 0 0 10px #00ff00;
  }
`;