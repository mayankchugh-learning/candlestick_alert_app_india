# Code Walkthrough - Candlestick Alert System

This document provides a technical overview of the codebase for developers.

## Architecture Overview

The system is built using a modern Python web architecture:
- **Backend**: Flask REST API with SQLAlchemy ORM
- **Frontend**: Single-page application with vanilla JavaScript
- **Database**: SQLite (default) or PostgreSQL
- **Styling**: Tailwind CSS with custom dark theme
- **Charts**: Lightweight Charts (TradingView)

## Core Components

### 1. Stock Analyzer (`stock_analyzer.py`)

The heart of the application - handles all candlestick pattern analysis.

#### Key Classes

```python
class CandlestickAnalyzer:
    """Main analyzer class for candlestick pattern detection."""
    
    def __init__(self, use_mock_data=False):
        # Initialize with optional mock data mode
        
    def fetch_candlestick_data(self, symbol, start_date, end_date, interval):
        # Fetches OHLCV data from Yahoo Finance
        # Returns DataFrame with columns: date, open, high, low, close, volume
        
    def process_data(self, data):
        # Adds calculated fields:
        # - is_green, is_red: candle color
        # - price_change, price_change_pct
        # - prev_open, prev_close, prev_color: previous candle data
        
    def generate_signals(self, data):
        # Core signal logic:
        # BUY: current green AND prev red AND current_close > prev_open
        # SELL: current red AND prev green AND current_close < prev_open
        
    def analyze_stock(self, symbol):
        # Complete analysis for single stock
        # Returns: symbol, price, trend, signals, etc.
        
    def scan_all_stocks(self, stock_list):
        # Batch analysis for multiple stocks
        # Returns categorized results: buy_signals, sell_signals, etc.
```

#### Signal Generation Logic

```python
# Buy Signal
if (current['is_green'] and 
    previous['is_red'] and 
    current['close'] > previous['open']):
    signal = {'type': 'BUY', ...}

# Sell Signal
elif (current['is_red'] and 
      previous['is_green'] and 
      current['close'] < previous['open']):
    signal = {'type': 'SELL', ...}
```

### 2. Flask Application (`app.py`)

REST API server with SQLAlchemy models and APScheduler.

#### Database Models

```python
class Stock(db.Model):
    # Tracks stock information and latest analysis
    id, symbol, name, current_price, current_trend,
    last_signal_type, last_signal_date, price_change_pct, last_updated

class Alert(db.Model):
    # Stores generated buy/sell alerts
    id, symbol, alert_type, signal_date,
    current_close, current_open, prev_open, prev_close,
    strength, reason, is_notified, created_at

class Settings(db.Model):
    # Key-value store for application settings
    id, key, value, updated_at

class ScanHistory(db.Model):
    # Tracks scan operations
    id, scan_type, total_stocks, buy_signals, sell_signals,
    errors, duration_seconds, created_at
```

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard` | GET | Dashboard summary |
| `/api/stocks` | GET | List stocks with pagination |
| `/api/stocks/<symbol>` | GET | Stock details |
| `/api/alerts` | GET | List alerts with filtering |
| `/api/alerts/export` | GET | Export alerts to JSON |
| `/api/scan` | POST | Run manual scan |
| `/api/settings` | GET/POST | Manage settings |
| `/api/chart/<symbol>` | GET | Chart data |

#### Scheduled Tasks

```python
# Runs on 1st of month at 3:30 AM UTC (9:00 AM IST)
scheduler.add_job(
    scheduled_monthly_scan,
    'cron',
    day=1,
    hour=3,
    minute=30
)
```

### 3. Frontend (`index.html`)

Single-page application with four main tabs.

#### Tab Structure

1. **Dashboard Tab**
   - Summary cards (total stocks, buy/sell signals)
   - Top signals tables
   - Recent alerts table
   - Manual scan trigger

2. **Scanner Tab**
   - Filter controls (trend, signal type)
   - Progress bar for scanning
   - Results table with stock details

3. **Alerts Tab**
   - Advanced filtering (type, symbol, date)
   - Export functionality
   - Paginated alerts table

4. **Settings Tab**
   - EmailJS configuration
   - Scan settings display
   - Signal logic explanation

#### Key JavaScript Functions

```javascript
// Dashboard
async function refreshDashboard() { ... }
async function runManualScan() { ... }

// Scanner
async function scanAllStocks() { ... }
function applyFilters() { ... }

// Alerts
async function loadAlerts() { ... }
async function exportAlerts() { ... }

// Stock Modal
async function viewStock(symbol) { ... }
function renderCandlestickChart(data) { ... }

// Settings
async function saveEmailSettings() { ... }
async function testEmailNotification() { ... }
```

#### Chart Integration

Uses Lightweight Charts library for TradingView-style charts:

```javascript
const chart = LightweightCharts.createChart(container, {
    layout: { background: { color: '#1e293b' } },
    // ... configuration
});

const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10b981',   // Green
    downColor: '#ef4444', // Red
});

// Add signal markers
candlestickSeries.setMarkers(markers);
```

## Data Flow

```
1. User triggers scan (manual or scheduled)
         ↓
2. CandlestickAnalyzer fetches data from Yahoo Finance
         ↓
3. Data processed: candle colors, previous values calculated
         ↓
4. Signal logic applied: BUY/SELL signals generated
         ↓
5. Results saved to database (Stocks, Alerts tables)
         ↓
6. API returns summary to frontend
         ↓
7. Dashboard/tables updated with new data
```

## Error Handling

### Backend

```python
try:
    # Operation
except Exception as e:
    logger.error(f"Error: {str(e)}")
    db.session.rollback()
    return jsonify({'success': False, 'error': str(e)}), 500
```

### Frontend

```javascript
try {
    const response = await fetch(url);
    const data = await response.json();
    if (data.success) {
        // Handle success
    }
} catch (error) {
    console.error('Error:', error);
    showToast('Operation failed', 'error');
}
```

## Testing

### Run Stock Analyzer Tests

```bash
python stock_analyzer.py
```

### API Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Get dashboard
curl http://localhost:5000/api/dashboard

# Run scan
curl -X POST http://localhost:5000/api/scan
```

## Performance Considerations

1. **Database Indexing**: Indexes on frequently queried columns (symbol, alert_type, created_at)
2. **Pagination**: All list endpoints support pagination
3. **Caching**: Stock data cached in analyzer during scan
4. **Background Processing**: APScheduler for non-blocking scheduled tasks

## Security Notes

1. **CORS**: Configured for development; restrict in production
2. **Environment Variables**: Sensitive data in `.env` file
3. **Input Validation**: Basic validation on API inputs
4. **SQL Injection**: Protected by SQLAlchemy ORM

## Extending the System

### Adding New Stock Exchanges

1. Modify `NSE_STOCKS` list in `stock_analyzer.py`
2. Update ticker suffix (e.g., `.NS` for NSE, `.BO` for BSE)
3. Test data availability from Yahoo Finance

### Adding New Signal Types

1. Extend `generate_signals()` method
2. Add new signal type to Alert model
3. Update frontend to display new signal type

### Integrating Alternative Data Sources

1. Create new fetch method (e.g., `fetch_from_tradingview()`)
2. Implement data normalization to standard format
3. Add configuration for data source selection
