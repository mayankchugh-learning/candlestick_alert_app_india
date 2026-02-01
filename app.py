"""
Candlestick Alert System - Flask REST API Server
Provides API endpoints for stock analysis, alerts, and dashboard data.
"""

import os
import json
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, render_template_string


def utcnow():
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import logging

from stock_analyzer import CandlestickAnalyzer, get_nse_stock_list

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///candlestick_alerts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize analyzer
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
analyzer = CandlestickAnalyzer(use_mock_data=USE_MOCK_DATA)


# ==================== Database Models ====================

class Stock(db.Model):
    """Stock model for tracking analyzed stocks."""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    current_price = db.Column(db.Float)
    current_trend = db.Column(db.String(20))
    last_signal_type = db.Column(db.String(10))
    last_signal_date = db.Column(db.DateTime)
    price_change_pct = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price,
            'current_trend': self.current_trend,
            'last_signal_type': self.last_signal_type,
            'last_signal_date': self.last_signal_date.isoformat() if self.last_signal_date else None,
            'price_change_pct': self.price_change_pct,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class Alert(db.Model):
    """Alert model for storing generated signals."""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    alert_type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    signal_date = db.Column(db.DateTime, nullable=False)
    current_close = db.Column(db.Float)
    current_open = db.Column(db.Float)
    prev_open = db.Column(db.Float)
    prev_close = db.Column(db.Float)
    strength = db.Column(db.Float)
    reason = db.Column(db.Text)
    is_notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'alert_type': self.alert_type,
            'signal_date': self.signal_date.isoformat() if self.signal_date else None,
            'current_close': self.current_close,
            'current_open': self.current_open,
            'prev_open': self.prev_open,
            'prev_close': self.prev_close,
            'strength': self.strength,
            'reason': self.reason,
            'is_notified': self.is_notified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Settings(db.Model):
    """Application settings model."""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ScanHistory(db.Model):
    """Scan history for tracking scan operations."""
    id = db.Column(db.Integer, primary_key=True)
    scan_type = db.Column(db.String(20))  # 'manual' or 'scheduled'
    total_stocks = db.Column(db.Integer)
    buy_signals = db.Column(db.Integer)
    sell_signals = db.Column(db.Integer)
    errors = db.Column(db.Integer)
    duration_seconds = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_type': self.scan_type,
            'total_stocks': self.total_stocks,
            'buy_signals': self.buy_signals,
            'sell_signals': self.sell_signals,
            'errors': self.errors,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== API Routes ====================

@app.route('/')
def index():
    """Serve the main dashboard page."""
    return send_from_directory('.', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard summary data."""
    try:
        total_stocks = Stock.query.count()
        buy_alerts = Alert.query.filter_by(alert_type='BUY').count()
        sell_alerts = Alert.query.filter_by(alert_type='SELL').count()
        
        # Recent alerts
        recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(10).all()
        
        # Top affected stocks (by signal strength)
        top_buy = Alert.query.filter_by(alert_type='BUY').order_by(Alert.strength.desc()).limit(5).all()
        top_sell = Alert.query.filter_by(alert_type='SELL').order_by(Alert.strength.desc()).limit(5).all()
        
        # Last scan info
        last_scan = ScanHistory.query.order_by(ScanHistory.created_at.desc()).first()
        
        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_stocks': total_stocks or len(get_nse_stock_list()),
                    'buy_signals': buy_alerts,
                    'sell_signals': sell_alerts,
                    'total_alerts': buy_alerts + sell_alerts
                },
                'recent_alerts': [a.to_dict() for a in recent_alerts],
                'top_buy_signals': [a.to_dict() for a in top_buy],
                'top_sell_signals': [a.to_dict() for a in top_sell],
                'last_scan': last_scan.to_dict() if last_scan else None
            }
        })
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get all tracked stocks."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        trend_filter = request.args.get('trend')
        signal_filter = request.args.get('signal')
        
        query = Stock.query
        
        if trend_filter:
            query = query.filter_by(current_trend=trend_filter)
        if signal_filter:
            query = query.filter_by(last_signal_type=signal_filter)
            
        stocks = query.order_by(Stock.last_updated.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'stocks': [s.to_dict() for s in stocks.items],
                'total': stocks.total,
                'pages': stocks.pages,
                'current_page': page
            }
        })
    except Exception as e:
        logger.error(f"Get stocks error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock(symbol):
    """Get detailed analysis for a specific stock."""
    try:
        analysis = analyzer.analyze_stock(symbol.upper())
        chart_data = analyzer.get_stock_chart_data(symbol.upper())
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis,
                'chart_data': chart_data
            }
        })
    except Exception as e:
        logger.error(f"Get stock error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts with optional filtering."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        alert_type = request.args.get('type')
        symbol = request.args.get('symbol')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Alert.query
        
        if alert_type:
            query = query.filter_by(alert_type=alert_type.upper())
        if symbol:
            query = query.filter_by(symbol=symbol.upper())
        if start_date:
            query = query.filter(Alert.signal_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Alert.signal_date <= datetime.fromisoformat(end_date))
            
        alerts = query.order_by(Alert.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': [a.to_dict() for a in alerts.items],
                'total': alerts.total,
                'pages': alerts.pages,
                'current_page': page
            }
        })
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/export', methods=['GET'])
def export_alerts():
    """Export alerts to JSON format."""
    try:
        alert_type = request.args.get('type')
        query = Alert.query
        
        if alert_type:
            query = query.filter_by(alert_type=alert_type.upper())
            
        alerts = query.order_by(Alert.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': [a.to_dict() for a in alerts],
                'exported_at': utcnow().isoformat(),
                'total': len(alerts)
            }
        })
    except Exception as e:
        logger.error(f"Export alerts error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan', methods=['POST'])
def run_scan():
    """Run a manual stock scan."""
    try:
        start_time = utcnow()
        
        # Get optional stock list from request (silent=True to handle empty body)
        data = request.get_json(silent=True) or {}
        stock_list = data.get('stocks')
        
        # Run the scan
        results = analyzer.scan_all_stocks(stock_list)
        
        # Calculate duration
        duration = (utcnow() - start_time).total_seconds()
        
        # Save scan history
        scan_record = ScanHistory(
            scan_type='manual',
            total_stocks=results['summary']['total_scanned'],
            buy_signals=results['summary']['buy_signals_count'],
            sell_signals=results['summary']['sell_signals_count'],
            errors=results['summary']['error_count'],
            duration_seconds=duration
        )
        db.session.add(scan_record)
        
        # Save/update stocks and alerts
        for stock_data in results['all_stocks']:
            stock = Stock.query.filter_by(symbol=stock_data['symbol']).first()
            if not stock:
                stock = Stock(symbol=stock_data['symbol'])
                
            stock.current_price = stock_data['current_price']
            stock.current_trend = stock_data['current_trend']
            stock.price_change_pct = stock_data['price_change_pct']
            stock.last_updated = utcnow()
            
            if stock_data['latest_signal']:
                signal = stock_data['latest_signal']
                stock.last_signal_type = signal['type']
                stock.last_signal_date = datetime.fromisoformat(signal['date'])
                
                # Create alert
                alert = Alert(
                    symbol=signal['symbol'],
                    alert_type=signal['type'],
                    signal_date=datetime.fromisoformat(signal['date']),
                    current_close=signal['current_close'],
                    current_open=signal['current_open'],
                    prev_open=signal['prev_open'],
                    prev_close=signal['prev_close'],
                    strength=signal['strength'],
                    reason=signal['reason']
                )
                db.session.add(alert)
            
            db.session.add(stock)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'summary': results['summary'],
                'duration_seconds': duration,
                'buy_signals': results['buy_signals'][:10],  # Top 10
                'sell_signals': results['sell_signals'][:10]  # Top 10
            }
        })
    except Exception as e:
        logger.error(f"Scan error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan/progress', methods=['GET'])
def get_scan_progress():
    """Get the current scan progress (for real-time updates)."""
    # This would be implemented with WebSockets or SSE for real-time updates
    # For now, return the last scan status
    last_scan = ScanHistory.query.order_by(ScanHistory.created_at.desc()).first()
    return jsonify({
        'success': True,
        'data': last_scan.to_dict() if last_scan else None
    })


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all application settings."""
    try:
        settings = Settings.query.all()
        return jsonify({
            'success': True,
            'data': {s.key: s.value for s in settings}
        })
    except Exception as e:
        logger.error(f"Get settings error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update application settings."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        for key, value in data.items():
            setting = Settings.query.filter_by(key=key).first()
            if not setting:
                setting = Settings(key=key)
            setting.value = value if isinstance(value, str) else json.dumps(value)
            setting.updated_at = utcnow()
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings/email/test', methods=['POST'])
def test_email():
    """Test email notification setup."""
    try:
        data = request.get_json(silent=True) or {}
        test_email = data.get('email')
        
        if not test_email:
            return jsonify({'success': False, 'error': 'Email address required'}), 400
        
        # In a real implementation, this would send a test email
        # For now, we'll just validate the configuration
        return jsonify({
            'success': True,
            'message': f'Test email would be sent to {test_email}',
            'note': 'Email sending is handled by EmailJS on the frontend'
        })
    except Exception as e:
        logger.error(f"Test email error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stock-list', methods=['GET'])
def get_stock_list():
    """Get the list of available NSE stocks."""
    return jsonify({
        'success': True,
        'data': get_nse_stock_list()
    })


@app.route('/api/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    """Get chart data for a specific stock."""
    try:
        chart_data = analyzer.get_stock_chart_data(symbol.upper())
        
        if not chart_data:
            return jsonify({
                'success': False,
                'error': f'No data available for {symbol}'
            }), 404
            
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        logger.error(f"Chart data error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== Scheduled Tasks ====================

def scheduled_monthly_scan():
    """Run automated monthly scan on the 1st of each month."""
    logger.info("Running scheduled monthly scan...")
    with app.app_context():
        try:
            start_time = utcnow()
            results = analyzer.scan_all_stocks()
            duration = (utcnow() - start_time).total_seconds()
            
            # Save scan history
            scan_record = ScanHistory(
                scan_type='scheduled',
                total_stocks=results['summary']['total_scanned'],
                buy_signals=results['summary']['buy_signals_count'],
                sell_signals=results['summary']['sell_signals_count'],
                errors=results['summary']['error_count'],
                duration_seconds=duration
            )
            db.session.add(scan_record)
            
            # Process results (similar to manual scan)
            for stock_data in results['all_stocks']:
                stock = Stock.query.filter_by(symbol=stock_data['symbol']).first()
                if not stock:
                    stock = Stock(symbol=stock_data['symbol'])
                    
                stock.current_price = stock_data['current_price']
                stock.current_trend = stock_data['current_trend']
                stock.price_change_pct = stock_data['price_change_pct']
                stock.last_updated = utcnow()
                
                if stock_data['latest_signal']:
                    signal = stock_data['latest_signal']
                    stock.last_signal_type = signal['type']
                    stock.last_signal_date = datetime.fromisoformat(signal['date'])
                    
                    alert = Alert(
                        symbol=signal['symbol'],
                        alert_type=signal['type'],
                        signal_date=datetime.fromisoformat(signal['date']),
                        current_close=signal['current_close'],
                        current_open=signal['current_open'],
                        prev_open=signal['prev_open'],
                        prev_close=signal['prev_close'],
                        strength=signal['strength'],
                        reason=signal['reason']
                    )
                    db.session.add(alert)
                
                db.session.add(stock)
            
            db.session.commit()
            logger.info(f"Scheduled scan completed. {results['summary']['total_scanned']} stocks processed.")
            
        except Exception as e:
            logger.error(f"Scheduled scan error: {str(e)}")
            db.session.rollback()


# Initialize scheduler
scheduler = BackgroundScheduler()
# Run on the 1st of every month at 9:00 AM IST (3:30 AM UTC)
scheduler.add_job(
    scheduled_monthly_scan,
    'cron',
    day=1,
    hour=3,
    minute=30,
    id='monthly_scan',
    replace_existing=True
)


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ==================== Application Startup ====================

def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized successfully")


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started. Monthly scan scheduled for 1st of each month at 9:00 AM IST")
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
