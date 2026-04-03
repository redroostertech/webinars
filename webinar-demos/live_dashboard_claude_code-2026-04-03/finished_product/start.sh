#!/bin/bash
# ──────────────────────────────────────────────
# Live Dashboard — Quick Start
# Run this script to install deps, start the
# Flask app, and open the dashboard in a browser.
# ──────────────────────────────────────────────

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PORT=3456
URL="http://localhost:$PORT"

# ── Kill anything already on the port ──
echo "Checking port $PORT..."
EXISTING_PID=$(lsof -ti:$PORT 2>/dev/null)
if [ -n "$EXISTING_PID" ]; then
    echo "Port $PORT is in use (PID $EXISTING_PID). Killing it..."
    kill -9 $EXISTING_PID 2>/dev/null
    sleep 1
    echo "Cleared."
fi

# ── Check prerequisites ──
echo "Checking prerequisites..."

# Python 3.10+
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is not installed. Install Python 3.10+ and try again."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "ERROR: Python 3.10+ is required (found $PY_VERSION)."
    exit 1
fi
echo "  Python $PY_VERSION ✓"

# pip3
if ! command -v pip3 &>/dev/null; then
    echo "ERROR: pip3 is not installed. Install pip and try again."
    exit 1
fi
echo "  pip3 ✓"

# curl (used to check server readiness)
if ! command -v curl &>/dev/null; then
    echo "ERROR: curl is not installed. Install curl and try again."
    exit 1
fi
echo "  curl ✓"

# credentials.json for Google APIs
if [ ! -f credentials.json ]; then
    echo "WARNING: credentials.json not found — Google API features (Drive, Sheets, Gmail, Calendar) will not work."
    echo "         Download it from the Google Cloud Console and place it in this directory."
fi

# ── Install dependencies ──
echo "Installing dependencies..."
pip3 install -q -r requirements.txt 2>&1 | grep -v "^\[notice\]"

# ── Create .env from example if missing ──
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — update it with your API tokens."
fi

# ── Create data directory ──
mkdir -p data

# ── Trap Ctrl+C to clean up ──
cleanup() {
    echo ""
    echo "Shutting down dashboard..."
    kill $APP_PID 2>/dev/null
    wait $APP_PID 2>/dev/null
    echo "Done."
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── Parse flags ──
EXTRA_ARGS=""
for arg in "$@"; do
    case "$arg" in
        --watch) EXTRA_ARGS="$EXTRA_ARGS --watch" ;;
    esac
done

# ── Start Flask ──
echo "Starting dashboard on $URL ..."
python3 app.py $EXTRA_ARGS &
APP_PID=$!

# ── Wait for server to be ready ──
for i in $(seq 1 20); do
    if curl -s -o /dev/null http://127.0.0.1:$PORT/login 2>/dev/null; then
        break
    fi
    sleep 0.5
done

# ── Open in browser ──
open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null || echo "Open $URL in your browser."

echo ""
echo "============================================"
echo "  Dashboard is running on $URL"
echo "  Login:  admin / demo123"
echo ""
echo "  Press Ctrl+C to stop."
echo "============================================"
echo ""

# Keep script alive so Ctrl+C triggers cleanup
wait $APP_PID
