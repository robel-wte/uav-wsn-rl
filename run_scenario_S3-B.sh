#!/bin/bash
# Scenario S3-B: UAV Speed v=20 m/s (30 runs)
# Tests high mobility impact

SCENARIO="S3-B-v20"
RESULTS_DIR="results/S3-UAV-Speed/$SCENARIO"
SEED=1  # Consistent seed across all scenarios

echo "========================================="
echo "Running Scenario S3-B: v=20 m/s"
echo "UAV Speed: 20 m/s (200% of baseline)"
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
    --**.minSpeed=20mps \
    --**.maxSpeed=20mps \
    --**.searchSpeed=20mps \
    --seed-set=$SEED \
    > "$RESULTS_DIR/simulation.log" 2>&1

# Move CSV files
mv results/*.csv "$RESULTS_DIR/" 2>/dev/null || true
mv results/*.sca "$RESULTS_DIR/" 2>/dev/null || true

echo "[$SCENARIO] Completed!"

echo "========================================="
echo "Scenario S3-B: Single run completed!"
echo "Extracting metrics..."
echo "========================================="

# Extract metrics
python3 extract_metrics.py "$RESULTS_DIR"

echo "Results available in: $RESULTS_DIR"
echo "Plots available in: $RESULTS_DIR/validation_plots/"
