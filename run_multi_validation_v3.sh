#!/bin/bash

# Multi-run validation - running each simulation separately
# This avoids memory issues from running 30 simulations in one process

TOTAL_RUNS=${1:-30}
OUTPUT_DIR="results/multi-run"

echo "======================================"
echo "  UAV-WSN Multi-Run Validation"
echo "  Sequential Independent Runs"
echo "======================================"
echo "Total runs: $TOTAL_RUNS"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Clean previous runs
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/logs"

# Record start time
START_TIME=$(date +%s)
echo "Start time: $(date)"
echo ""

# Compile if needed
if [ ! -f "./uav-wsn-bm" ]; then
    echo "Compiling simulation..."
    make MODE=release
    if [ $? -ne 0 ]; then
        echo "✗ Compilation failed"
        exit 1
    fi
fi

# Run each simulation separately
for run in $(seq 0 $((TOTAL_RUNS - 1))); do
    echo ""
    echo "=========================================="
    echo "  Running Simulation $((run + 1))/$TOTAL_RUNS (seed=$run)"
    echo "=========================================="
    
    RUN_DIR="$OUTPUT_DIR/run-$run"
    mkdir -p "$RUN_DIR"
    
    # Run simulation with specific seed
    ./uav-wsn-bm -u Cmdenv -n . \
        -c General \
        --seed-set=$run \
        --result-dir="$RUN_DIR" \
        --cmdenv-express-mode=true \
        --cmdenv-performance-display=true \
        --cmdenv-status-frequency=100s \
        > "$OUTPUT_DIR/logs/run-$run.log" 2>&1
    
    EXIT_CODE=$?
    
    # MetricsCollector writes to hardcoded results/ directory, so move files to run directory
    if [ -f "results/network.csv" ]; then
        mv results/*.csv "$RUN_DIR/" 2>/dev/null
        echo "  → Moved CSV files from results/ to $RUN_DIR/"
    fi
    
    # Check if simulation completed (allow exit code 139 if data was generated)
    if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 139 ]; then
        # Check if CSV files were generated
        if ls "$RUN_DIR"/*.csv 1> /dev/null 2>&1; then
            echo "✓ Run $run completed with data"
            
            # Extract metrics
            python3 extract_metrics.py --run-id $run \
                                        --input-dir "$RUN_DIR" \
                                        --output "$OUTPUT_DIR/run-$run-summary.csv" \
                                        2>&1 | grep -E "(✓|✗|Error)" || echo "  Metrics extracted"
        else
            echo "⚠ Run $run completed but no CSV files found"
        fi
    else
        echo "✗ Run $run FAILED (exit code: $EXIT_CODE)"
    fi
    
    # Progress
    PROGRESS=$(( (run + 1) * 100 / TOTAL_RUNS ))
    echo "Progress: $PROGRESS% ($((run + 1))/$TOTAL_RUNS)"
    
    # Show time elapsed and estimate
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    AVG_TIME=$((ELAPSED / (run + 1)))
    REMAINING=$((AVG_TIME * (TOTAL_RUNS - run - 1)))
    
    ELAPSED_H=$((ELAPSED / 3600))
    ELAPSED_M=$(((ELAPSED % 3600) / 60))
    REMAINING_H=$((REMAINING / 3600))
    REMAINING_M=$(((REMAINING % 3600) / 60))
    
    echo "Elapsed: ${ELAPSED_H}h ${ELAPSED_M}m | Est. remaining: ${REMAINING_H}h ${REMAINING_M}m"
done

# Calculate total elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "=========================================="
echo "  All Runs Completed"
echo "=========================================="
echo "Total time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo ""

# Count successful runs
SUCCESS_COUNT=$(ls "$OUTPUT_DIR"/run-*-summary.csv 2>/dev/null | wc -l)
echo "Successful runs: $SUCCESS_COUNT / $TOTAL_RUNS"
echo ""

if [ $SUCCESS_COUNT -lt 10 ]; then
    echo "⚠ Warning: Less than 10 successful runs. Statistical analysis may not be reliable."
fi

# Run statistical analysis
echo "Running statistical analysis..."
python3 analyze_multi_run.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  Analysis Complete"
    echo "=========================================="
    echo "Check the following files:"
    echo "  - $OUTPUT_DIR/statistical_summary.txt"
    echo "  - $OUTPUT_DIR/statistical_summary.csv"
    echo "  - $OUTPUT_DIR/variance_analysis.csv"
    echo "  - $OUTPUT_DIR/validation_plots/"
    echo "=========================================="
else
    echo "✗ Statistical analysis failed (may need more successful runs)"
fi
