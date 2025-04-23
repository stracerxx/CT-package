# CT-5 Retro 80s UI Style Guide

## Overview
This project uses a persistent retro 80s/arcade dashboard style. The look is defined by:
- Pixel/arcade fonts ("Press Start 2P", "VT323")
- Neon borders and colored headers (red, green, yellow)
- Boxed panels with dark backgrounds and glowing effects
- Custom retro toggle switches and buttons

## Critical Files
- `frontend/styles/RetroTheme.jsx`: All main UI styles and retro components.
- `frontend/pages/_document.js`: Loads Google Fonts for the retro look.

## Rules for Consistency
- **Do not overwrite or remove the Google Fonts link in `_document.js`.**
- **Do not change the font-family, border, or color styles in `RetroTheme.jsx` without updating this guide.**
- **All headers must use the retro font and color scheme.**
- **Panels must be boxed with neon borders and dark backgrounds.**
- **Toggles and buttons must use the retro style.**
- **Any UI changes must be reviewed for consistency with this style guide.**

## How to Update the UI
1. Make changes in a feature branch.
2. Update this style guide if you change the look.
3. Commit and push your changes.
4. The pre-commit hook will warn you if you change critical files.

## Example
![Retro UI Example](screenshot-retro-ui.png)

---
_Last updated: 2025-04-13_