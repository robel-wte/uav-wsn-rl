#!/bin/bash

# Monitor multi-run validation progress
# Usage: ./monitor_validation.sh [interval_seconds]

INTERVAL=${1:-60}  # Default: check every 60 seconds
LOG_FILE="results/multi-run/logs/all-runs.log"
RESULT_DIR="results/multi-run"

echo "======================================"
echo "  Multi-Run Validation Monitor"
echo "======================================"
echo "Monitoring interval: ${INTERVAL}s"
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    clear
    echo "======================================"
    echo "  Multi-Run Status - $(date)"
    echo "======================================"
    echo ""
    
    # Check if process is running
    if ps aux | grep -v grep | grep -q "uav-wsn-bm"; then
        echo "Status: 🟢 RUNNING"
        
        # Get current progress from log
        if [ -f "$LOG_FILE" ]; then
            # Extract latest simulation time
            LATEST_EVENT=$(grep -oP "Event #\K[0-9]+" "$LOG_FILE" | tail -1)
            LATEST_TIME=$(grep -oP "t=\K[0-9]+" "$LOG_FILE" | tail -1)
            
            if [ ! -z "$LATEST_TIME" ]; then
                PROGRESS=$((LATEST_TIME * 100 / 1161000))
                echo "Current simulation time: t=${LATEST_TIME}s / 1161000s (${PROGRESS}%)"
                echo "Events processed: $LATEST_EVENT"
            fi
            
            # Check which run we're on
            CURRENT_RUN=$(grep -oP "run #\K[0-9]+" "$LOG_FILE" | tail -1)
            if [ ! -z "$CURRENT_RUN" ]; then
                echo "Current run: #$CURRENT_RUN / 29 (0-indexed)"
            fi
        fi
    else
        echo "Status: 🔴 NOT RUNNING"
        
        # Check if completed
        if [ -f "$LOG_FILE" ]; then
            if grep -q "All Runs Completed" "$LOG_FILE" 2>/dev/null; then
                echo "✓ All runs completed!"
            elif grep -q "Simulation time limit reached" "$LOG_FILE" 2>/dev/null; then
                COMPLETED_RUNS=$(ls -d "$RESULT_DIR"/run-* 2>/dev/null | wc -l)
                echo "Completed runs: $COMPLETED_RUNS / 30"
            else
                echo "Status unclear - check logs"
            fi
        fi
    fi
    
    echo ""
    echo "Results:"
    # Count completed runs
    if [ -d "$RESULT_DIR" ]; then
        COMPLETED=$(ls -d "$RESULT_DIR"/run-* 2>/dev/null | wc -l)
        WITH_DATA=$(find "$RESULT_DIR" -name "network.csv" 2>/dev/null | wc -l)
        echo "  Directories created: $COMPLETED"
        echo "  Runs with data: $WITH_DATA"
    fi
    
    # Show recent log lines
    echo ""
    echo "Recent log output:"
    echo "----------------------------------------"
    if [ -f "$LOG_FILE" ]; then
        tail -5 "$LOG_FILE"
    else
        echo "  (no log file yet)"
    fi
    
    echo ""
    echo "Next update in ${INTERVAL}s..."
    sleep $INTERVAL
done
