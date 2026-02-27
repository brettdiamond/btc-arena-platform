#!/usr/bin/env python3
"""
BTC Arena Web Dashboard (DigitalOcean)

Multi-page app:
- "/"           -> Live Trading Dashboard
- "/optimizer"  -> Optimizer (stub for now)
- "/live-feed"  -> Live Feed (stub for now)
- "/reporting"  -> Reporting (stub for now)

Reads from /opt/btc-arena/arena.db used by the engine.
"""

from flask import Flask, render_template
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/opt/btc-arena/arena.db")

app = Flask(__name__)

def get_db():
    return sqlite3.connect(DB_PATH)

# ---------- Shared data helpers ----------

def get_overview(conn):
    cur = conn.cursor()

    # Equity & last price from equity_snapshots
    try:
        cur.execute(
            "SELECT equity, price, ts FROM equity_snapshots "
            "ORDER BY ts DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            equity, last_price, _ = row
        else:
            equity, last_price = 0.0, None
    except sqlite3.OperationalError:
        equity, last_price = 0.0, None

    # Total trade count from trades table
    try:
        cur.execute("SELECT COUNT(*) FROM trades")
        trade_count = cur.fetchone()[0]
    except sqlite3.OperationalError:
        trade_count = 0

    return equity, last_price, trade_count

def get_portfolios_snapshot(conn):
    """
    Basic info for all portfolios from the portfolios table.
    We will refine columns once we confirm the schema.
    """
    cur = conn.cursor()
    portfolios = []

    try:
        cur.execute("PRAGMA table_info(portfolios)")
        cols = [c[1] for c in cur.fetchall()]

        name_col = "name" if "name" in cols else cols[0]
        equity_col = "equity" if "equity" in cols else None
        roi_col = "roi" if "roi" in cols else None

        select_cols = [name_col]
        if equity_col:
            select_cols.append(equity_col)
        if roi_col:
            select_cols.append(roi_col)

        query = f"SELECT {', '.join(select_cols)} FROM portfolios"
        cur.execute(query)
        rows = cur.fetchall()

        for r in rows:
            data = {
                "name": r[0],
                "equity": r[1] if equity_col else None,
                "roi": r[2] if roi_col and len(r) > 2 else None,
            }
            portfolios.append(data)

    except sqlite3.OperationalError:
        pass

    return portfolios

# ---------- Routes ----------

@app.route("/")
def live_dashboard():
    """Live Trading Dashboard."""
    conn = get_db()
    try:
        equity, last_price, trade_count = get_overview(conn)
        portfolios = get_portfolios_snapshot(conn)
    finally:
        conn.close()

    return render_template(
        "live_dashboard.html",
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        equity=equity,
        last_price=last_price,
        trade_count=trade_count,
        portfolios=portfolios,
        active_tab="live",
    )

@app.route("/optimizer")
def optimizer_view():
    # Stub page for now
    return render_template(
        "optimizer.html",
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        active_tab="optimizer",
    )

@app.route("/live-feed")
def live_feed_view():
    # Stub page for now
    return render_template(
        "live_feed.html",
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        active_tab="live_feed",
    )

@app.route("/reporting")
def reporting_view():
    # Stub page for now
    return render_template(
        "reporting.html",
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        active_tab="reporting",
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
