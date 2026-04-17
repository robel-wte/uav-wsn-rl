#!/bin/bash

# Multi-run validation script for statistical analysis
# Runs multiple independent simulations with different seeds

TOTAL_RUNS=${1:-5}  # Default to 5 runs, can pass number as argument
START_RUN=1
OUTPUT_DIR="results/multi-run"

echo "======================================"
echo "  UAV-WSN Multi-Run Validation"
echo "======================================"
echo "Total runs: $TOTAL_RUNS"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory structure
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/logs"

# Record start time
START_TIME=$(date +%s)
echo "Start time: $(date)"

# Compile if needed
if [ ! -f "./uav-wsn-bm" ]; then
    echo "Compiling simulation..."
    make MODE=release
    if [ $? -ne 0 ]; then
        echo "✗ Compilation failed"
        exit 1
    fi
fi

# Run simulations
for run in $(seq $START_RUN $TOTAL_RUNS); do
    echo ""
    echo "=========================================="
    echo "  Running Simulation $run/$TOTAL_RUNS"
    echo "=========================================="
    
    RUN_DIR="$OUTPUT_DIR/run-$run"
    mkdir -p "$RUN_DIR"
    
    # Clean up any previous results
    rm -f results/*.csv results/*.sca results/*.vec 2>/dev/null
    
    # Execute simulation with specific seed
    # Run from main directory with proper parameters
    ./uav-wsn-bm -u Cmdenv \
        --seed-set=$run \
        --cmdenv-express-mode=true \
        --cmdenv-performance-display=true \
        --cmdenv-status-frequency=100s \
        > "$OUTPUT_DIR/logs/run-$run.log" 2>&1
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✓ Run $run simulation completed"
        
        # Move result files to run directory
        if ls results/*.csv 1> /dev/null 2>&1; then
            mv results/*.csv "$RUN_DIR/"
        fi
        if ls results/*.sca 1> /dev/null 2>&1; then
            mv results/*.sca "$RUN_DIR/"
        fi
        if ls results/*.vec 1> /dev/null 2>&1; then
            mv results/*.vec "$RUN_DIR/"
        fi
        
        # Extract key metrics to summary file
        python3 extract_metrics.py --run-id $run \
                                    --input-dir "$RUN_DIR" \
                                    --output "$OUTPUT_DIR/run-$run-summary.csv"
        
        if [ $? -eq 0 ]; then
            echo "✓ Metrics extracted for run $run"
        else
            echo "✗ Metric extraction failed for run $run"
        fi
    else
        echo "✗ Run $run FAILED (exit code: $EXIT_CODE)"
        echo "Check log: $OUTPUT_DIR/logs/run-$run.log"
    fi
    
    # Progress indicator
    PROGRESS=$((run * 100 / TOTAL_RUNS))
    echo "Progress: $PROGRESS% ($run/$TOTAL_RUNS)"
done

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
echo "Results stored in: $OUTPUT_DIR"
echo ""

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
    echo "✗ Statistical analysis failed"
fi
