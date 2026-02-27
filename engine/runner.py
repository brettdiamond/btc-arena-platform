#!/usr/bin/env python3
"""
BTC Arena Engine runner

For now, this script simply delegates to the existing
/opt/btc-arena/runner.py so we can manage it via systemd
from this repo.

Later we can move all engine logic into this repo.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

EXISTING_RUNNER = Path("/opt/btc-arena/runner.py")

def main():
    if not EXISTING_RUNNER.exists():
        print("[btc-arena] ERROR: Existing engine runner not found at /opt/btc-arena/runner.py")
        sys.exit(1)

    print("[btc-arena] Starting engine via /opt/btc-arena/runner.py")

    # Simple loop: if the underlying runner exits, restart it after a short delay.
    while True:
        try:
            proc = subprocess.Popen(
                [sys.executable, str(EXISTING_RUNNER), "--interval", "30"],
                cwd="/opt/btc-arena",
            )
            return_code = proc.wait()
            print(f"[btc-arena] Underlying runner exited with code {return_code}, restarting in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[btc-arena] Exception while running engine: {e!r}")
            time.sleep(5)

if __name__ == "__main__":
    main()
