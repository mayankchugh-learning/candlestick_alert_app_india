# Copilot Instructions — CandleAlert (candlestick_alert_app_india)

**Purpose:** Help AI coding agents become productive quickly by highlighting the app's architecture, key files, developer workflows, conventions, and high‑value edit points.

## 1) Big Picture (what this repo does) 🔧
- Flask REST API that scans monthly NSE candlestick data and generates BUY/SELL alerts based on bullish/bearish engulfing rules.
- Core components:
  - `app.py` — API server, DB models (Stock, Alert, Settings, ScanHistory), scheduler (monthly scan), and routes.
  - `stock_analyzer.py` — signal generation, data fetching (Yahoo Finance via `yfinance`), and mock data mode.
  - `index.html` — single‑page frontend (vanilla JS) that calls the API and uses Lightweight Charts for charts.
  - `Dockerfile` / `docker-compose.yml` — containerization and optional PostgreSQL setup.

## 2) Key files & symbols to inspect first 🔎
- `stock_analyzer.py`:
  - Class: `CandlestickAnalyzer` (methods: `fetch_candlestick_data`, `process_data`, `generate_signals`, `generate_signal_for_last_two_months`, `scan_all_stocks`)
  - Data list: `NSE_STOCKS` — add/remove tracked symbols here.
  - Helper: `get_last_two_complete_months()` — determines comparison months.
- `app.py`:
  - Endpoints: `/api/scan`, `/api/dashboard`, `/api/stocks/<symbol>`, `/api/alerts`, `/api/chart/<symbol>`, `/api/settings`.
  - Scheduled task: `scheduled_monthly_scan()` — cron job added with APScheduler (runs 1st of month at 03:30 UTC / 09:00 IST).
  - DB: uses SQLAlchemy and `init_db()` calls `db.create_all()` (no migration framework included).
- `index.html`: front-end uses EmailJS for email sending (EmailJS credentials are client-side), and triggers scans and charts.

## 3) Dev & run workflows (practical commands) ✅
- Local dev (quick):
  - Create venv, install: `pip install -r requirements.txt`
  - Start: `python app.py` (starts Flask, DB init, and APScheduler)
- Quick analyzer test: `python stock_analyzer.py` (runs sample analysis and a small scan)
- Docker (production-like):
  - Build & run: `docker-compose build && docker-compose up -d`
  - Logs: `docker-compose logs -f app`
  - Production server (non-container): `gunicorn --bind 0.0.0.0:5000 --workers 2 app:app`
- API testing examples:
  - Health: `curl http://localhost:5000/api/health`
  - Manual scan: `curl -X POST http://localhost:5000/api/scan`

## 4) Important configuration / environment variables ⚙️
- `.env` (copy from `.env.example`) controls: `FLASK_ENV`, `FLASK_DEBUG`, `SECRET_KEY`, `DATABASE_URL`, `USE_MOCK_DATA`, `EMAILJS_*`.
- Notes:
  - `USE_MOCK_DATA` defaults to `true` (app.py) and can be set `false` to enable live YFinance fetches.
  - `DATABASE_URL` defaults to SQLite: `sqlite:///candlestick_alerts.db`. Docker compose shows how to add PostgreSQL.

## 5) Signal logic & patterns (concrete examples) 💡
- Primary rule (implemented in `generate_signal_for_last_two_months`):
  - BUY: previous month is RED, current month is GREEN, and current close > previous open.
  - SELL: previous month is GREEN, current month is RED, and current close < previous open.
- `generate_signals` runs over historical months and also computes `strength` (%). Use that sorting in `scan_all_stocks`.
- Edge cases: If the last two complete months' data is missing, the analyzer falls back to the last two available rows — keep this in mind when modifying logic.

## 6) Integration points & external dependencies 🔗
- Stock data: `yfinance` (ticker format: `SYMBOL.NS` for NSE).
- Email notifications: handled on the frontend via EmailJS (backend `test_email` endpoint only validates input).
- Scheduler: APScheduler (monthly cron job). Scheduler is started only when `app.py` runs as `__main__`.

## 7) Debugging & common gotchas ⚠️
- Scheduler does not start when running via gunicorn unless the process triggers startup code — be mindful of process model if deploying with workers.
- No DB migrations — `db.create_all()` used; changes to models require database handling (drop/recreate or add migrations manually).
- Time handling: UTC is used server-side (`utcnow()` helper). Monthly comparisons are based on server local date/time — verify when running in different timezones.
- Mock mode is useful for offline development: set `USE_MOCK_DATA=true` in `.env`.

## 8) Where to make the most impactful changes 🛠️
- Add new signals: update `generate_signals()` and `generate_signal_for_last_two_months()` in `stock_analyzer.py` and ensure `Alert` model accounts for any new fields.
- Change stock universe: edit `NSE_STOCKS` in `stock_analyzer.py`.
- Emailing flow: integrate server-side email sending if you want mail logic on backend (currently client-driven via EmailJS).

## 9) Tests & verification (current state) ✅
- No automated unit tests included. Quick checks:
  - `python stock_analyzer.py` (example run)
  - Use the API endpoints via `curl` / Postman and inspect DB `candlestick_alerts.db`.
- Recommended immediate test targets (for engineers): unit tests for `generate_signals()` and `generate_signal_for_last_two_months()` using deterministic mock data.

---
If anything above is unclear or you want more detail (examples, concrete tests to add, or a short checklist for code changes), tell me which section to expand and I will iterate. ✅
