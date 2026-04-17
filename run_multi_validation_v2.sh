#!/bin/bash

# Multi-run validation script using OMNeT++'s native repeat functionality
# This ensures proper seed handling and result file management

TOTAL_RUNS=${1:-30}
OUTPUT_DIR="results/multi-run"

echo "======================================"
echo "  UAV-WSN Multi-Run Validation"
echo "  Using OMNeT++ Native Repeat"
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

# Run all simulations using OMNeT++'s repeat functionality
# This properly handles seed-set for each repetition
echo "==========================================
"
echo "  Starting $TOTAL_RUNS Simulations"
echo "=========================================="
echo ""

./uav-wsn-bm -u Cmdenv -f omnetpp-multirun.ini \
    -c General \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=true \
    --cmdenv-status-frequency=100s \
    --num-rngs=10 \
    > "$OUTPUT_DIR/logs/all-runs.log" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All simulations completed successfully"
else
    echo "✗ Simulations failed (exit code: $EXIT_CODE)"
    echo "Check log: $OUTPUT_DIR/logs/all-runs.log"
    exit 1
fi

# Calculate elapsed time
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

# Extract metrics from each run
echo "Extracting metrics from each run..."
for run in $(seq 0 $((TOTAL_RUNS - 1))); do
    RUN_DIR="$OUTPUT_DIR/run-$run"
    if [ -d "$RUN_DIR" ] && [ -f "$RUN_DIR/network.csv" ]; then
        python3 extract_metrics.py --run-id $run \
                                    --input-dir "$RUN_DIR" \
                                    --output "$OUTPUT_DIR/run-$run-summary.csv"
        if [ $? -eq 0 ]; then
            echo "  ✓ Run $run metrics extracted"
        else
            echo "  ✗ Run $run metric extraction failed"
        fi
    else
        echo "  ✗ Run $run: No data found in $RUN_DIR"
    fi
done

echo ""
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
    echo "✗ Statistical analysis failed"
    exit 1
fi
