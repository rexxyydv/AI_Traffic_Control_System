#!/bin/bash

# AI Traffic Control System - Mac Launcher
# ─────────────────────────────────────────
# FIRST TIME ONLY: open Terminal and run:
#   chmod +x START_TRAFFIC.sh
# Then double-click this file to launch everything.

# Move to the folder where this script lives
cd "$(dirname "$0")"

echo ""
echo "=========================================="
echo "  AI Traffic Control System - Launcher"
echo "=========================================="
echo ""

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found."
    echo "Install from https://www.python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Install dependencies if missing
echo "[1/3] Checking Python dependencies..."
python3 -m pip install ultralytics flask flask-cors opencv-python -q --exists-action i
echo "[1/3] Dependencies OK"

# Start YOLO server in a new Terminal window
echo "[2/3] Starting YOLO backend server..."
osascript -e "tell application \"Terminal\"
    activate
    do script \"cd '$(pwd)' && python3 traffic_server.py\"
end tell"

# Wait for server to boot
echo "[2/3] Waiting for server to start (5 seconds)..."
sleep 5

# Open dashboard in browser
echo "[3/3] Opening dashboard in browser..."
open traffic_dashboard.html

echo ""
echo "=========================================="
echo "  All done! Keep the Terminal window open."
echo "=========================================="
sleep 3