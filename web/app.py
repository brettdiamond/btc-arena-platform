#!/usr/bin/env python3
"""
BTC Arena Web Dashboard (DigitalOcean)

Reads from the existing /opt/btc-arena/arena.db used by the engine.
"""

from flask import Flask, render_template
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/opt/btc-arena/arena.db")

app = Flask(__name__)

def get_db():
    return sqlite3.connect(DB_PATH)

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

def get_recent_trades(conn, limit=20):
    cur = conn.cursor()
    trades = []

    try:
        # Inspect columns of trades table
        cur.execute("PRAGMA table_info(trades)")
        cols = [c[1] for c in cur.fetchall()]

        ts_col = "ts" if "ts" in cols else "timestamp"
        port_col = "portfolio" if "portfolio" in cols else "portfolio_name"
        side_col = "side" if "side" in cols else "direction"
        size_col = "size" if "size" in cols else "qty"
        price_col = "price"

        query = (
            f"SELECT {ts_col}, {port_col}, {side_col}, {size_col}, {price_col} "
            f"FROM trades ORDER BY {ts_col} DESC LIMIT ?"
        )
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        for r in rows:
            trades.append({
                "time": r[0],
                "portfolio": r[1],
                "side": r[2],
                "size": r[3],
                "price": r[4],
            })
    except sqlite3.OperationalError:
        pass

    return trades

def get_optimizer_snapshot(conn):
    cur = conn.cursor()

    # Placeholder: we can wire this to performance_metrics or tuning_log later
    try:
        cur.execute(
            "SELECT best_roi, iterations, milestones "
            "FROM performance_metrics ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            return {
                "elite_roi": row[0],
                "iterations": row[1],
                "milestones": row[2],
            }
    except sqlite3.OperationalError:
        pass

    return None

@app.route("/")
def index():
    conn = get_db()
    try:
        equity, last_price, trade_count = get_overview(conn)
        trades = get_recent_trades(conn)
        optimizer = get_optimizer_snapshot(conn)
    finally:
        conn.close()

    return render_template(
        "dashboard.html",
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        equity=equity,
        last_price=last_price,
        trade_count=trade_count,
        trades=trades,
        optimizer=optimizer,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
