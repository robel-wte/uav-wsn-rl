#!/bin/bash

# Monitor the multi-run validation progress every minute

echo "======================================"
echo "  UAV-WSN Multi-Run Monitor"
echo "======================================"
echo ""

while true; do
    clear
    echo "======================================"
    echo "  Multi-Run Validation Progress"
    echo "  $(date)"
    echo "======================================"
    echo ""
    
    # Check if script is still running
    if ps aux | grep -v grep | grep "run_multi_validation_v3.sh" > /dev/null; then
        echo "Status: ✓ RUNNING"
    else
        echo "Status: ✗ STOPPED"
        echo ""
        echo "Final status:"
        tail -30 multi-run-progress.log
        break
    fi
    
    echo ""
    echo "--- Latest Progress ---"
    tail -20 multi-run-progress.log
    
    echo ""
    echo "--- File Count ---"
    RUN_DIRS=$(ls -d results/multi-run/run-* 2>/dev/null | wc -l)
    CSV_FILES=$(find results/multi-run/run-* -name "*.csv" 2>/dev/null | wc -l)
    SUMMARY_FILES=$(ls results/multi-run/run-*-summary.csv 2>/dev/null | wc -l)
    
    echo "Run directories: $RUN_DIRS"
    echo "CSV files: $CSV_FILES"
    echo "Summary files: $SUMMARY_FILES"
    
    echo ""
    echo "Refreshing in 60 seconds... (Ctrl+C to stop monitoring)"
    sleep 60
done
