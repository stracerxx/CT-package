# CT-5 Crypto Trading Bot - User Guide

## Introduction

Welcome to CT-5, your retro-styled crypto trading assistant with advanced AI capabilities! This user guide will help you navigate the features and functionality of your new crypto trading bot.

## Getting Started

After setting up CT-5 using the instructions in the setup guide, you can access the application at:
- Frontend: http://localhost:3000
- Default login: username=`admin`, password=`admin`

> **IMPORTANT**: For security, please change the admin password immediately after your first login.

## Main Dashboard

The dashboard is your command center for monitoring and controlling your trading activities.

### Market Condition Panel

This panel displays the current market condition score (0-100) which indicates the overall health of the crypto market:
- 0-30: Bearish (Red)
- 31-50: Neutral (Yellow)
- 51-70: Bullish (Light Green)
- 71-100: Very Bullish (Bright Green)

The Perpetual Earning Mode toggle allows you to enable/disable automatic trading based on market conditions.

### Trading Strategies

CT-5 offers five different trading strategies that you can enable or disable individually:

1. **Grid Trading**: Creates a grid of buy and sell orders at regular price intervals. Ideal for sideways markets with predictable ranges.

2. **Scalping**: Makes quick trades to capture small price movements. Works best in volatile markets with high liquidity.

3. **Swing Trading**: Aims to capture medium-term price movements over several days. Suitable for trending markets.

4. **DCA (Dollar Cost Averaging)**: Invests fixed amounts at regular intervals regardless of price. Great for long-term accumulation.

5. **Momentum Trading**: Trades based on continuation of existing price trends. Effective in strongly trending markets.

To enable a strategy, simply toggle the switch next to its name. The strategy will begin operating according to your configured parameters.

### Active Trades

This table displays all currently active trades with the following information:
- Symbol: The trading pair (e.g., BTC/USDT)
- Strategy: Which strategy initiated this trade
- Side: Buy (long) or Sell (short)
- Amount: Quantity of the asset
- Entry Price: Price at which the trade was opened
- Current Price: Latest price of the asset
- P/L %: Profit/Loss percentage

## RSS Feed Section

The RSS Feed section provides the latest crypto news from configured sources. You can:
- Switch between different news sources using the buttons at the top
- Click on article titles to read the full content
- Refresh the feed to get the latest news

Staying informed about market news is crucial for making good trading decisions, especially if you're manually adjusting strategy parameters.

## Chat Assistant

CT-5 includes an AI chat assistant that can help you understand trading concepts, explain market conditions, and provide insights about your trading activities.

To use the chat assistant:
1. Click the chat bubble icon in the bottom right corner
2. Type your question or request
3. The assistant will respond with helpful information

You can select different AI providers from the dropdown menu in the chat window:
- OpenAI
- Claude
- Gemini
- OpenRouter
- DeepSeek

The chat assistant has a retro 80s personality and will occasionally use period-appropriate slang while providing accurate trading information.

## Admin Panel

The Admin Panel allows you to configure various aspects of CT-5. To access it, click on "Admin" in the navigation menu.

### Users

The Users tab displays all registered users and their status. As an admin, you can see:
- Username
- Email
- Admin status
- Active status

### API Keys

The API Keys tab allows you to manage API keys for various services:
- OpenAI
- Claude
- Gemini
- OpenRouter
- DeepSeek

To add a new API key:
1. Select the service from the dropdown
2. Enter your API key
3. Click "ADD API KEY"

### System Prompts

The System Prompts tab allows you to customize the personality and behavior of the CT-5 chat assistant.

To add a new system prompt:
1. Enter a name for the prompt
2. Write or paste the prompt content
3. Optionally set it as active
4. Click "ADD SYSTEM PROMPT"

Only one system prompt can be active at a time. To change the active prompt, click "SET ACTIVE" next to the desired prompt.

### RSS Feeds

The RSS Feeds tab allows you to manage news sources for the RSS Feed section.

To add a new RSS feed:
1. Enter a name for the feed
2. Enter the URL of the RSS feed
3. Enter a category (e.g., "news", "bitcoin")
4. Click "ADD RSS FEED"

You can toggle feeds on/off using the switch in the Active column.

## Trading Strategies in Detail

### Grid Trading

Grid trading works by placing buy orders at regular intervals below the current price and sell orders above it. When the price moves up and down within the range, the bot automatically buys low and sells high.

**Best used when:**
- The market is moving sideways in a defined range
- Volatility is present but without a strong directional trend

**Key parameters:**
- Upper Price: The highest price in your grid
- Lower Price: The lowest price in your grid
- Grid Levels: Number of price points in your grid
- Investment Amount: Total amount to invest across all grid levels

### Scalping

Scalping aims to profit from small price movements by making many quick trades with small profit targets.

**Best used when:**
- Markets have high liquidity and tight spreads
- Short-term price movements are frequent

**Key parameters:**
- Take Profit %: The percentage gain at which to close a profitable trade
- Stop Loss %: The percentage loss at which to close a losing trade
- Max Trades: Maximum number of concurrent trades
- Trade Amount: Amount to use per trade

### Swing Trading

Swing trading captures medium-term price movements that typically last from a few days to a few weeks.

**Best used when:**
- Markets show clear trends or reversal patterns
- You want to capture larger price movements than scalping

**Key parameters:**
- Entry Condition: Technical indicator for entry (e.g., MACD crossover)
- Exit Condition: Condition to exit the trade
- Take Profit %: Target profit percentage
- Stop Loss %: Maximum acceptable loss percentage
- Trade Amount: Amount to use per trade

### DCA (Dollar Cost Averaging)

DCA involves investing a fixed amount at regular intervals regardless of price, reducing the impact of volatility.

**Best used when:**
- You want to accumulate assets long-term
- You want to reduce the impact of market volatility

**Key parameters:**
- Interval Days: How often to make purchases
- Investment Amount: Fixed amount to invest each time
- Total Periods: Number of investment periods

### Momentum Trading

Momentum trading capitalizes on the continuation of existing trends by entering in the direction of the trend.

**Best used when:**
- Markets show strong directional movement
- Volume supports the price movement

**Key parameters:**
- Lookback Period: Number of periods to analyze for momentum
- Threshold: Minimum momentum value to trigger a trade
- Take Profit %: Target profit percentage
- Stop Loss %: Maximum acceptable loss percentage
- Trade Amount: Amount to use per trade

## Perpetual Earning Mode

Perpetual Earning Mode is an advanced feature that automatically manages your trading based on market conditions:

- When market conditions are favorable (above your configured threshold), trading is enabled
- When conditions deteriorate below the threshold, trading is automatically suspended
- When conditions improve above the auto-resume threshold, trading resumes

This helps protect your capital during unfavorable market conditions while capitalizing on opportunities when conditions improve.

## Best Practices

1. **Start with Paper Trading**: Always begin with paper trading mode until you're comfortable with the system.

2. **Risk Management**: Never invest more than you can afford to lose. Start with small amounts.

3. **Strategy Selection**: Different strategies work better in different market conditions:
   - Sideways markets: Grid trading
   - Volatile markets: Scalping
   - Trending markets: Momentum or Swing trading
   - Uncertain markets: DCA

4. **Regular Monitoring**: While CT-5 can operate autonomously, regularly check its performance and adjust as needed.

5. **Stay Informed**: Use the RSS feed to stay updated on market news that might affect your trading.

6. **Backup Configuration**: Regularly backup your database to preserve your configuration and trading history.

## Troubleshooting

### Common Issues

1. **Chat assistant not responding**:
   - Check that you've configured API keys for at least one AI provider
   - Verify your internet connection
   - Check the provider's service status

2. **Trades not executing**:
   - Verify that Perpetual Earning Mode is enabled
   - Check that at least one strategy is enabled
   - Ensure market conditions are above the minimum threshold
   - Verify exchange API keys if using live trading

3. **RSS feeds not updating**:
   - Check that the feed URLs are valid and accessible
   - Try refreshing the feed manually
   - Verify your internet connection

4. **UI not displaying correctly**:
   - Clear your browser cache
   - Try a different browser
   - Check for console errors in browser developer tools

## Getting Help

If you encounter issues not covered in this guide:

1. Check the logs: `docker-compose logs`
2. Run the test scripts to identify specific issues
3. Refer to the API documentation for endpoint details

## Conclusion

CT-5 combines powerful trading capabilities with a fun, retro interface to make crypto trading more accessible and enjoyable. By understanding its features and following best practices, you can make the most of your crypto trading experience.

Happy trading with your new 80s-themed crypto assistant!
