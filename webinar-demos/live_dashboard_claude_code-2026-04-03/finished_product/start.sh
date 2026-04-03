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

# ── Start Flask ──
echo "Starting dashboard on $URL ..."
python3 app.py &
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
