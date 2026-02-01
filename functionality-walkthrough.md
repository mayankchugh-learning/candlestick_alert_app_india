# User Guide - Candlestick Alert System

This guide explains how to use the Candlestick Alert System effectively.

## Getting Started

### 1. Access the Application

1. Open your web browser
2. Navigate to `http://localhost:5000` (or your deployed URL)
3. The dashboard will load automatically

### 2. Dashboard Overview

The dashboard provides a quick overview of your stock analysis:

- **Total Stocks**: Number of NSE stocks being tracked (50 by default)
- **Buy Signals**: Count of stocks with active buy signals
- **Sell Signals**: Count of stocks with active sell signals
- **Total Alerts**: Combined count of all generated alerts

## Understanding Signals

### Green (Bullish) Signal - BUY

A buy signal is generated when:
1. The previous month's candle was **red** (stock closed lower than it opened)
2. The current month's candle is **green** (stock closed higher than it opened)
3. The current closing price is **above** the previous red candle's opening price

**What this means**: The stock has reversed from a bearish trend and the current bullish move has overcome the previous month's starting point, indicating strong buying momentum.

**Example**:
- November 2025: Red candle, opened at ₹500, closed at ₹450
- December 2025: Green candle, opened at ₹460, closed at ₹520
- Since ₹520 > ₹500 (previous open), a **BUY** signal is generated

### Red (Bearish) Signal - SELL

A sell signal is generated when:
1. The previous month's candle was **green** (stock closed higher than it opened)
2. The current month's candle is **red** (stock closed lower than it opened)
3. The current closing price is **below** the previous green candle's opening price

**What this means**: The stock has reversed from a bullish trend and the current bearish move has broken below the previous month's starting point, indicating strong selling pressure.

**Example**:
- June 2025: Green candle, opened at ₹400, closed at ₹450
- July 2025: Red candle, opened at ₹440, closed at ₹380
- Since ₹380 < ₹400 (previous open), a **SELL** signal is generated

### Signal Strength

Each signal includes a **strength percentage** indicating how significant the move was:
- Higher strength = More significant price movement
- Use strength to prioritize which signals to act on

## Using the Features

### Running a Manual Scan

1. Click **"Run Manual Scan"** button on the dashboard
2. Wait for the scan to complete (usually 1-2 minutes)
3. View updated signals in the tables below

### Stock Scanner Tab

The Scanner tab allows you to:

1. **Scan All Stocks**: Click "Scan All NSE Stocks" to analyze all tracked stocks
2. **Filter by Trend**: Show only bullish or bearish stocks
3. **Filter by Signal**: Show only stocks with BUY or SELL signals
4. **View Details**: Click "View" on any stock to see its chart

### Viewing Stock Charts

1. Click "View" on any stock row
2. A modal opens with:
   - Interactive candlestick chart
   - Signal markers (green arrows for BUY, red arrows for SELL)
   - Current price details
   - Signal explanation if applicable
3. Press **Escape** or click outside to close

### Managing Alerts

In the **Alerts** tab:

1. **Filter Alerts**:
   - By type (BUY/SELL)
   - By symbol (e.g., "RELIANCE")
   - By date range

2. **Export Alerts**:
   - Click the download button
   - Alerts are exported as JSON file
   - Use for record-keeping or analysis

### Email Notifications

Set up email alerts in the **Settings** tab:

1. **Create EmailJS Account**:
   - Go to [emailjs.com](https://www.emailjs.com/)
   - Sign up for a free account

2. **Add Email Service**:
   - Add Gmail, Outlook, or other email service
   - Note your Service ID

3. **Create Template**:
   - Create a new email template
   - Use these variables:
     - `{{to_email}}` - Recipient
     - `{{subject}}` - Subject line
     - `{{message}}` - Alert content

4. **Configure in App**:
   - Enter your EmailJS User ID
   - Enter Service ID
   - Enter Template ID
   - Add recipient email
   - Enable automatic alerts

5. **Test**:
   - Click "Send Test" to verify setup
   - Check your inbox for test email

## Automated Alerts

The system automatically:

1. **Monthly Scan**: Runs on the 1st of every month at 9:00 AM IST
2. **Alert Generation**: Creates alerts based on last 2 months of data
3. **Email Notifications**: Sends emails if enabled in settings

## Tips for Best Results

### 1. Focus on High-Strength Signals
- Signals with strength > 5% are more significant
- Top 10 signals are shown on the dashboard

### 2. Combine with Other Analysis
- Use signals as one input, not the only decision factor
- Consider fundamental analysis alongside
- Check news and events for context

### 3. Monitor Regularly
- Check dashboard weekly for new signals
- Don't rely solely on automated alerts

### 4. Track Your Trades
- Export alerts for record-keeping
- Review past signals to refine strategy

## Troubleshooting

### No Data Showing
- Ensure the app is connected to the internet
- Try running a manual scan
- Check if mock data mode is enabled

### Scan Taking Too Long
- Each stock takes ~1-2 seconds to analyze
- 50 stocks = ~2 minutes total
- Be patient during full scans

### Email Not Working
- Verify all EmailJS credentials
- Check spam folder
- Use "Send Test" to diagnose
- Ensure email service is connected in EmailJS

### Chart Not Loading
- Check browser console for errors
- Ensure JavaScript is enabled
- Try refreshing the page

## Frequently Asked Questions

**Q: How often should I run scans?**
A: The automated monthly scan is sufficient for most users. Run manual scans if you need real-time updates.

**Q: Can I add more stocks?**
A: Yes, modify the `NSE_STOCKS` list in `stock_analyzer.py` and restart the app.

**Q: Is the data real-time?**
A: No, the system uses monthly candlestick data. Real-time data is not applicable for this strategy.

**Q: What's the success rate of signals?**
A: This depends on market conditions. Always do your own research and never rely solely on automated signals.

**Q: Can I use this for intraday trading?**
A: No, this system is designed for monthly candlestick analysis only. It's suited for position/swing trading.

## Support

For technical issues or feature requests, please create an issue on GitHub or contact support.
