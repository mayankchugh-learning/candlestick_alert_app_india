"""
Stock Analyzer Module
Handles candlestick pattern analysis and signal generation for Indian stocks.

Signal Logic:
- Compares the last 2 complete months (e.g., Nov 2025 vs Dec 2025)
- Buy Signal: Previous month RED, Current month GREEN, Current close > Previous open
- Sell Signal: Previous month GREEN, Current month RED, Current close < Previous open
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dateutil.relativedelta import relativedelta
import yfinance as yf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_last_two_complete_months() -> Tuple[datetime, datetime]:
    """
    Get the start dates of the last two complete months.
    For example, if today is Jan 29, 2026, returns (Nov 1, 2025, Dec 1, 2025)
    
    Returns:
        Tuple of (previous_month_start, current_month_start)
    """
    today = datetime.now()
    # Get first day of current month
    first_of_this_month = today.replace(day=1)
    # Last complete month
    last_complete_month = first_of_this_month - relativedelta(months=1)
    # Month before that
    previous_month = last_complete_month - relativedelta(months=1)
    
    return previous_month, last_complete_month


def get_month_name(date: datetime) -> str:
    """Get month name and year from date."""
    return date.strftime("%B %Y")


# List of major NSE stocks (can be expanded)
NSE_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "SBIN", "BHARTIARTL", "KOTAKBANK", "BAJFINANCE",
    "ITC", "LT", "AXISBANK", "ASIANPAINT", "MARUTI",
    "HCLTECH", "SUNPHARMA", "TITAN", "WIPRO", "ULTRACEMCO",
    "NTPC", "POWERGRID", "NESTLEIND", "TECHM", "TATAMOTORS",
    "ONGC", "COALINDIA", "JSWSTEEL", "ADANIENT", "ADANIPORTS",
    "TATASTEEL", "GRASIM", "BAJAJFINSV", "DIVISLAB", "BPCL",
    "DRREDDY", "CIPLA", "BRITANNIA", "EICHERMOT", "APOLLOHOSP",
    "HEROMOTOCO", "HINDALCO", "INDUSINDBK", "UPL", "SBILIFE",
    "BAJAJ-AUTO", "TATACONSUM", "M&M", "HDFC", "VEDL"
]


class CandlestickAnalyzer:
    """
    Analyzes monthly candlestick patterns for Indian stocks
    and generates buy/sell signals based on engulfing patterns.
    """
    
    def __init__(self, use_mock_data: bool = False):
        """
        Initialize the analyzer.
        
        Args:
            use_mock_data: If True, generates mock data instead of fetching real data
        """
        self.use_mock_data = use_mock_data
        self.stocks_data: Dict[str, pd.DataFrame] = {}
        
    def fetch_candlestick_data(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1mo"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch monthly candlestick data for a given stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            start_date: Start date for data fetch
            end_date: End date for data fetch
            interval: Data interval (default: 1mo for monthly)
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        if self.use_mock_data:
            return self._generate_mock_data(symbol, start_date, end_date)
        
        try:
            # Add .NS suffix for NSE stocks
            ticker = f"{symbol}.NS"
            
            if start_date is None:
                start_date = datetime.now() - timedelta(days=365 * 2)  # 2 years
            if end_date is None:
                end_date = datetime.now()
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None
                
            # Rename columns to standard format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            df['symbol'] = symbol
            df = df.reset_index()
            df = df.rename(columns={'Date': 'date'})
            
            self.stocks_data[symbol] = df
            logger.info(f"Successfully fetched data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def _generate_mock_data(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Generate mock candlestick data for testing.
        Ensures data includes the last 2 complete months (e.g., Nov 2025 and Dec 2025).
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with mock OHLCV data
        """
        # Ensure we have data for at least the last 2 complete months
        prev_month, last_month = get_last_two_complete_months()
        
        if start_date is None:
            # Start from 6 months before the previous month for context
            start_date = prev_month - relativedelta(months=6)
        if end_date is None:
            # End at the last day of the last complete month
            end_date = last_month + relativedelta(months=1) - timedelta(days=1)
        
        # Generate monthly dates (first of each month)
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        
        # Generate realistic-looking price data
        np.random.seed(hash(symbol) % 2**32)
        base_price = np.random.uniform(100, 3000)
        
        data = []
        current_price = base_price
        
        for date in dates:
            # Random price movement
            change_pct = np.random.normal(0, 0.08)  # 8% std deviation
            
            open_price = current_price
            close_price = current_price * (1 + change_pct)
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.02)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.02)))
            volume = int(np.random.uniform(1000000, 50000000))
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'symbol': symbol
            })
            
            current_price = close_price
        
        df = pd.DataFrame(data)
        self.stocks_data[symbol] = df
        return df
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw candlestick data and add calculated fields.
        
        Args:
            data: Raw OHLCV DataFrame
            
        Returns:
            Processed DataFrame with additional fields
        """
        df = data.copy()
        
        # Determine candle color (green = bullish, red = bearish)
        df['is_green'] = df['close'] > df['open']
        df['is_red'] = df['close'] < df['open']
        df['candle_color'] = df.apply(
            lambda x: 'green' if x['is_green'] else ('red' if x['is_red'] else 'neutral'),
            axis=1
        )
        
        # Calculate price change
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = ((df['close'] - df['open']) / df['open']) * 100
        
        # Calculate body size
        df['body_size'] = abs(df['close'] - df['open'])
        
        # Previous candle data
        df['prev_open'] = df['open'].shift(1)
        df['prev_close'] = df['close'].shift(1)
        df['prev_color'] = df['candle_color'].shift(1)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        Generate buy/sell signals based on candlestick patterns.
        
        Signal Logic:
        - Buy Signal: Current green candle closes above previous red candle's open
        - Sell Signal: Current red candle closes below previous green candle's open
        
        Args:
            data: Processed DataFrame with candlestick data
            
        Returns:
            List of signal dictionaries
        """
        df = self.process_data(data)
        signals = []
        
        for i in range(1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i - 1]
            
            signal = None
            
            # Buy Signal: Current is green AND closes above previous red's open
            if (current['is_green'] and 
                previous['is_red'] and 
                current['close'] > previous['open']):
                signal = {
                    'type': 'BUY',
                    'symbol': current['symbol'],
                    'date': current['date'].strftime('%Y-%m-%d') if hasattr(current['date'], 'strftime') else str(current['date']),
                    'current_close': round(current['close'], 2),
                    'current_open': round(current['open'], 2),
                    'prev_open': round(previous['open'], 2),
                    'prev_close': round(previous['close'], 2),
                    'strength': round(((current['close'] - previous['open']) / previous['open']) * 100, 2),
                    'reason': f"Green candle closed at ₹{current['close']:.2f}, above previous red candle's open of ₹{previous['open']:.2f}"
                }
                
            # Sell Signal: Current is red AND closes below previous green's open
            elif (current['is_red'] and 
                  previous['is_green'] and 
                  current['close'] < previous['open']):
                signal = {
                    'type': 'SELL',
                    'symbol': current['symbol'],
                    'date': current['date'].strftime('%Y-%m-%d') if hasattr(current['date'], 'strftime') else str(current['date']),
                    'current_close': round(current['close'], 2),
                    'current_open': round(current['open'], 2),
                    'prev_open': round(previous['open'], 2),
                    'prev_close': round(previous['close'], 2),
                    'strength': round(((previous['open'] - current['close']) / previous['open']) * 100, 2),
                    'reason': f"Red candle closed at ₹{current['close']:.2f}, below previous green candle's open of ₹{previous['open']:.2f}"
                }
            
            if signal:
                signals.append(signal)
        
        return signals
    
    def get_latest_signal(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        Get only the most recent signal for a stock.
        
        Args:
            data: Processed DataFrame with candlestick data
            
        Returns:
            Latest signal dict or None
        """
        signals = self.generate_signals(data)
        if signals:
            return signals[-1]
        return None
    
    def generate_signal_for_last_two_months(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate signal specifically by comparing the last 2 complete months.
        For example, compares Nov 2025 (previous) vs Dec 2025 (current).
        
        Signal Logic:
        - Buy Signal: Nov is RED, Dec is GREEN, Dec close > Nov open
        - Sell Signal: Nov is GREEN, Dec is RED, Dec close < Nov open
        
        Args:
            data: DataFrame with candlestick data
            
        Returns:
            Signal dict if conditions met, None otherwise
        """
        if data is None or len(data) < 2:
            return None
        
        # Get the last 2 complete months
        prev_month_start, curr_month_start = get_last_two_complete_months()
        
        df = self.process_data(data)
        
        # Convert date column to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        # Filter for the specific months we want to compare
        # Previous month (e.g., Nov 2025)
        prev_month_data = df[
            (df['date'].dt.year == prev_month_start.year) & 
            (df['date'].dt.month == prev_month_start.month)
        ]
        
        # Current month (e.g., Dec 2025)
        curr_month_data = df[
            (df['date'].dt.year == curr_month_start.year) & 
            (df['date'].dt.month == curr_month_start.month)
        ]
        
        # If we don't have data for both months, fall back to last 2 available months
        if prev_month_data.empty or curr_month_data.empty:
            logger.warning(f"Data not available for {get_month_name(prev_month_start)} or {get_month_name(curr_month_start)}, using last 2 available months")
            if len(df) < 2:
                return None
            prev_month_data = df.iloc[[-2]]  # Second to last row
            curr_month_data = df.iloc[[-1]]  # Last row
        
        previous = prev_month_data.iloc[0]
        current = curr_month_data.iloc[0]
        
        # Get symbol
        symbol = current.get('symbol', data.iloc[0].get('symbol', 'UNKNOWN'))
        
        # Format month names for display
        prev_month_name = get_month_name(pd.to_datetime(previous['date']))
        curr_month_name = get_month_name(pd.to_datetime(current['date']))
        
        signal = None
        
        # Buy Signal: Previous month RED, Current month GREEN, Current close > Previous open
        if (current['is_green'] and 
            previous['is_red'] and 
            current['close'] > previous['open']):
            signal = {
                'type': 'BUY',
                'symbol': symbol,
                'date': current['date'].strftime('%Y-%m-%d') if hasattr(current['date'], 'strftime') else str(current['date']),
                'current_month': curr_month_name,
                'previous_month': prev_month_name,
                'current_close': round(float(current['close']), 2),
                'current_open': round(float(current['open']), 2),
                'prev_open': round(float(previous['open']), 2),
                'prev_close': round(float(previous['close']), 2),
                'strength': round(((float(current['close']) - float(previous['open'])) / float(previous['open'])) * 100, 2),
                'reason': f"{curr_month_name} green candle closed at ₹{float(current['close']):.2f}, above {prev_month_name} red candle's open of ₹{float(previous['open']):.2f}"
            }
            
        # Sell Signal: Previous month GREEN, Current month RED, Current close < Previous open
        elif (current['is_red'] and 
              previous['is_green'] and 
              current['close'] < previous['open']):
            signal = {
                'type': 'SELL',
                'symbol': symbol,
                'date': current['date'].strftime('%Y-%m-%d') if hasattr(current['date'], 'strftime') else str(current['date']),
                'current_month': curr_month_name,
                'previous_month': prev_month_name,
                'current_close': round(float(current['close']), 2),
                'current_open': round(float(current['open']), 2),
                'prev_open': round(float(previous['open']), 2),
                'prev_close': round(float(previous['close']), 2),
                'strength': round(((float(previous['open']) - float(current['close'])) / float(previous['open'])) * 100, 2),
                'reason': f"{curr_month_name} red candle closed at ₹{float(current['close']):.2f}, below {prev_month_name} green candle's open of ₹{float(previous['open']):.2f}"
            }
        
        return signal
    
    def analyze_stock(self, symbol: str) -> Dict:
        """
        Complete analysis for a single stock.
        Compares the last 2 complete months (e.g., Nov 2025 vs Dec 2025).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Analysis result dictionary
        """
        data = self.fetch_candlestick_data(symbol)
        
        if data is None or data.empty:
            return {
                'symbol': symbol,
                'status': 'error',
                'message': 'Failed to fetch data'
            }
        
        processed = self.process_data(data)
        
        # Generate signal specifically for last 2 months (Nov vs Dec comparison)
        latest_signal = self.generate_signal_for_last_two_months(data)
        
        # Also get all historical signals for reference
        all_signals = self.generate_signals(data)
        
        # Get current status (last complete month)
        current = processed.iloc[-1]
        
        # Get the months being compared for display
        prev_month, curr_month = get_last_two_complete_months()
        
        return {
            'symbol': symbol,
            'status': 'success',
            'current_price': round(current['close'], 2),
            'current_trend': 'bullish' if current['is_green'] else 'bearish',
            'candle_color': current['candle_color'],
            'price_change_pct': round(current['price_change_pct'], 2),
            'latest_signal': latest_signal,
            'comparison_months': f"{get_month_name(prev_month)} vs {get_month_name(curr_month)}",
            'total_signals': len(all_signals),
            'last_updated': datetime.now().isoformat()
        }
    
    def scan_all_stocks(self, stock_list: Optional[List[str]] = None) -> Dict:
        """
        Scan all stocks and generate comprehensive report.
        
        Args:
            stock_list: Optional list of stocks to scan (defaults to NSE_STOCKS)
            
        Returns:
            Comprehensive scan results
        """
        stocks = stock_list or NSE_STOCKS
        results = {
            'scan_time': datetime.now().isoformat(),
            'total_stocks': len(stocks),
            'buy_signals': [],
            'sell_signals': [],
            'bullish_stocks': [],
            'bearish_stocks': [],
            'all_stocks': [],
            'errors': []
        }
        
        for symbol in stocks:
            try:
                analysis = self.analyze_stock(symbol)
                
                if analysis['status'] == 'error':
                    results['errors'].append({
                        'symbol': symbol,
                        'message': analysis.get('message', 'Unknown error')
                    })
                    continue
                
                results['all_stocks'].append(analysis)
                
                # Categorize by current trend
                if analysis['current_trend'] == 'bullish':
                    results['bullish_stocks'].append(analysis)
                else:
                    results['bearish_stocks'].append(analysis)
                
                # Categorize by latest signal
                if analysis['latest_signal']:
                    if analysis['latest_signal']['type'] == 'BUY':
                        results['buy_signals'].append(analysis)
                    else:
                        results['sell_signals'].append(analysis)
                        
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                results['errors'].append({
                    'symbol': symbol,
                    'message': str(e)
                })
        
        # Sort by signal strength
        results['buy_signals'].sort(
            key=lambda x: x['latest_signal']['strength'] if x['latest_signal'] else 0,
            reverse=True
        )
        results['sell_signals'].sort(
            key=lambda x: x['latest_signal']['strength'] if x['latest_signal'] else 0,
            reverse=True
        )
        
        # Summary stats
        results['summary'] = {
            'total_scanned': len(results['all_stocks']),
            'buy_signals_count': len(results['buy_signals']),
            'sell_signals_count': len(results['sell_signals']),
            'bullish_count': len(results['bullish_stocks']),
            'bearish_count': len(results['bearish_stocks']),
            'error_count': len(results['errors'])
        }
        
        return results
    
    def get_stock_chart_data(self, symbol: str) -> Optional[Dict]:
        """
        Get chart data for a specific stock suitable for frontend visualization.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Chart data dictionary
        """
        data = self.fetch_candlestick_data(symbol)
        
        if data is None or data.empty:
            return None
        
        processed = self.process_data(data)
        signals = self.generate_signals(data)
        
        chart_data = {
            'symbol': symbol,
            'candles': [],
            'signals': signals
        }
        
        for _, row in processed.iterrows():
            chart_data['candles'].append({
                'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                'open': round(row['open'], 2),
                'high': round(row['high'], 2),
                'low': round(row['low'], 2),
                'close': round(row['close'], 2),
                'volume': int(row['volume']),
                'color': row['candle_color']
            })
        
        return chart_data


def get_nse_stock_list() -> List[str]:
    """Get the list of NSE stocks being tracked."""
    return NSE_STOCKS.copy()


# CLI interface for testing
if __name__ == "__main__":
    print("Candlestick Analyzer - Test Run")
    print("=" * 50)
    
    # Show which months are being compared
    prev_month, curr_month = get_last_two_complete_months()
    print(f"\nComparing: {get_month_name(prev_month)} vs {get_month_name(curr_month)}")
    print("=" * 50)
    
    analyzer = CandlestickAnalyzer(use_mock_data=True)
    
    # Test single stock analysis
    print("\nAnalyzing RELIANCE...")
    result = analyzer.analyze_stock("RELIANCE")
    print(f"Symbol: {result['symbol']}")
    print(f"Current Price: ₹{result['current_price']}")
    print(f"Trend: {result['current_trend']}")
    print(f"Comparison: {result.get('comparison_months', 'N/A')}")
    if result['latest_signal']:
        print(f"Signal Type: {result['latest_signal']['type']}")
        print(f"Signal Reason: {result['latest_signal']['reason']}")
    else:
        print("No signal generated (conditions not met)")
    
    # Test full scan
    print("\n" + "=" * 50)
    print("Running full stock scan (first 5 stocks)...")
    scan_results = analyzer.scan_all_stocks(NSE_STOCKS[:5])
    print(f"\nScan Summary:")
    print(f"  Comparison Period: {get_month_name(prev_month)} vs {get_month_name(curr_month)}")
    print(f"  Total Scanned: {scan_results['summary']['total_scanned']}")
    print(f"  Buy Signals: {scan_results['summary']['buy_signals_count']}")
    print(f"  Sell Signals: {scan_results['summary']['sell_signals_count']}")
    print(f"  Bullish Stocks: {scan_results['summary']['bullish_count']}")
    print(f"  Bearish Stocks: {scan_results['summary']['bearish_count']}")
