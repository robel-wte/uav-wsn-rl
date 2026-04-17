#!/bin/bash
# Scenario S3-A: UAV Speed v=15 m/s (30 runs)
# Tests moderate mobility impact

SCENARIO="S3-A-v15"
RESULTS_DIR="results/S3-UAV-Speed/$SCENARIO"
SEED=1  # Consistent seed across all scenarios

echo "========================================="
echo "Running Scenario S3-A: v=15 m/s"
echo "UAV Speed: 15 m/s (150% of baseline)"
echo "Single run with seed=$SEED (consistent)"
echo "Results directory: $RESULTS_DIR"
echo "========================================="

# Clean previous results
rm -rf "$RESULTS_DIR"/*
mkdir -p "$RESULTS_DIR"

echo "[$SCENARIO] Starting single run with seed=$SEED..."

./uav-wsn-bm -u Cmdenv -c General \
    -n . \
    omnetpp.ini \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.minSpeed=15mps \
    --**.maxSpeed=15mps \
    --**.searchSpeed=15mps \
    --seed-set=$SEED \
    > "$RESULTS_DIR/simulation.log" 2>&1

# Move CSV files
mv results/*.csv "$RESULTS_DIR/" 2>/dev/null || true
mv results/*.sca "$RESULTS_DIR/" 2>/dev/null || true

echo "[$SCENARIO] Completed!"

echo "========================================="
echo "Scenario S3-A: Single run completed!"
echo "Extracting metrics..."
echo "========================================="

# Extract metrics
python3 extract_metrics.py "$RESULTS_DIR"

echo "Results available in: $RESULTS_DIR"
echo "Plots available in: $RESULTS_DIR/validation_plots/"
