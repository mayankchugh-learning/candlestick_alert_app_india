# CandleAlert - Indian Stock Candlestick Alert System

A Python-based application that analyzes monthly candlestick patterns for Indian stocks (NSE) and generates buy/sell alerts based on engulfing pattern strategies.

## Features

- **Dashboard**: Overview of all tracked Indian stocks with summary statistics
- **Stock Scanner**: Scan all NSE stocks with real-time progress tracking
- **Signal Generation**: Automated buy/sell signals based on candlestick patterns
- **Alerts Management**: View, filter, and export generated alerts
- **Email Notifications**: Configure SMTP for automated alert notifications
- **Automated Monthly Scans**: Scheduled scans on the 1st of every month
- **Interactive Charts**: TradingView-style candlestick charts with signal markers

## Signal Logic

### Buy Signal (Bullish Engulfing)
- Previous month's candle is **red** (bearish: close < open)
- Current month's candle is **green** (bullish: close > open)
- Current close price > Previous red candle's open price

### Sell Signal (Bearish Engulfing)
- Previous month's candle is **green** (bullish)
- Current month's candle is **red** (bearish)
- Current close price < Previous green candle's open price

## Project Structure

```
candlestick_alert_app_india/
├── app.py                  # Flask REST API server
├── stock_analyzer.py       # Candlestick analysis logic
├── index.html              # Frontend dashboard (single-page app)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .env.example            # Environment variables template
├── .dockerignore           # Docker ignore file
├── README.md               # This file
├── codewalkthrough.md      # Technical documentation
└── functionality-walkthrough.md  # User guide
```

## Quick Start

### Prerequisites
- Python 3.9+ (recommended: 3.11)
- pip (Python package manager)
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd candlestick_alert_app_india
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env   # Windows
   cp .env.example .env     # Linux/Mac
   
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:5000`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   # Build the image
   docker-compose build
   
   # Start the container
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f app
   ```

3. **Stop the application**
   ```bash
   docker-compose down
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `DATABASE_URL` | Database connection string | `sqlite:///candlestick_alerts.db` |
| `USE_MOCK_DATA` | Use mock data instead of live API | `true` |
| `EMAILJS_USER_ID` | EmailJS user ID | - |
| `EMAILJS_SERVICE_ID` | EmailJS service ID | - |
| `EMAILJS_TEMPLATE_ID` | EmailJS template ID | - |

## API Endpoints

### Dashboard
- `GET /api/dashboard` - Get dashboard summary and recent alerts
- `GET /api/health` - Health check endpoint

### Stocks
- `GET /api/stocks` - List all tracked stocks (with pagination)
- `GET /api/stocks/<symbol>` - Get detailed analysis for a stock
- `GET /api/stock-list` - Get list of available NSE stocks
- `GET /api/chart/<symbol>` - Get chart data for a stock

### Scanning
- `POST /api/scan` - Run a manual stock scan
- `GET /api/scan/progress` - Get current scan progress

### Alerts
- `GET /api/alerts` - List all alerts (with filtering)
- `GET /api/alerts/export` - Export alerts to JSON

### Settings
- `GET /api/settings` - Get application settings
- `POST /api/settings` - Update application settings
- `POST /api/settings/email/test` - Test email configuration

## Email Setup (SMTP)

1. **For Gmail:**
   - Enable 2-Factor Authentication on your Google account
   - Generate an App Password: https://myaccount.google.com/apppasswords
   - Use the 16-character app password in `MAIL_PASSWORD`

2. **Configure in .env file:**
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

3. **For other email providers:**
   - Outlook: `smtp.office365.com` (Port 587)
   - Yahoo: `smtp.mail.yahoo.com` (Port 587)
   - Custom SMTP: Use your provider's settings

4. **Test email in Settings tab** of the dashboard

## Data Sources

The application supports multiple data sources:

1. **Yahoo Finance** (Default): Free API for NSE stock data
2. **Mock Data**: For testing without API calls (set `USE_MOCK_DATA=true`)

## Automated Scans

The system automatically runs a full stock scan on the **1st of every month at 9:00 AM IST** (3:30 AM UTC). This can be configured in `app.py`.

## Tracked Stocks

The application tracks 50 major NSE stocks including:
- RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK
- HINDUNILVR, SBIN, BHARTIARTL, KOTAKBANK, BAJFINANCE
- And 40 more...

The stock list can be modified in `stock_analyzer.py`.

## Production Deployment

### Using Gunicorn (Recommended)

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 app:app
```

### Using Docker

```bash
# Production build
docker build -t candlestick-alert .

# Run container
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-production-secret \
  -e USE_MOCK_DATA=false \
  --name candlestick-app \
  candlestick-alert
```

### Cloud Deployment (Heroku/Railway/Render)

1. Ensure `requirements.txt` is complete
2. Add a `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Set environment variables in your cloud platform
4. Deploy using your platform's CLI or GitHub integration

## Troubleshooting

### Common Issues

1. **No data for stocks**: Ensure `USE_MOCK_DATA=false` and check internet connectivity
2. **Database errors**: Delete `candlestick_alerts.db` and restart the app
3. **Email not sending**: Verify EmailJS credentials and template variables
4. **Chart not rendering**: Check browser console for JavaScript errors

### Logs

Application logs are printed to stdout. In Docker:
```bash
docker-compose logs -f app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please create a GitHub issue.
