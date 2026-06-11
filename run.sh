#!/bin/bash

# Kill any existing processes running on ports 5001 and 8080
echo "Initializing NEXUS ports..."
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Activate virtual environment
source venv/bin/activate

# Start Flask Backend (Kimi AI server) on port 5001 in background
echo "Starting Kimi AI Backend Server on http://localhost:5001..."
python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Start HTTP server on port 8080 in background
echo "Starting ScribbleFlow static server on http://localhost:8080..."
python3 -m http.server 8080 > frontend.log 2>&1 &
FRONTEND_PID=$!

echo "ScribbleFlow has booted successfully in NEXUS Mode!"
echo "Open your browser to: http://localhost:8080"
echo "Press Ctrl+C to stop both servers."

# Handle shutdown gracefully
cleanup() {
    echo ""
    echo "Terminating NEXUS servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Keep script running to maintain processes
wait
