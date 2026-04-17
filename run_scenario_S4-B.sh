#!/bin/bash
# Scenario S4-B: Initial Energy E=2.0J (30 runs)
# Tests 4× energy lifetime scaling

SCENARIO="S4-B-E20"
RESULTS_DIR="results/S4-Initial-Energy/$SCENARIO"
SEED=1  # Consistent seed across all scenarios

echo "========================================="
echo "Running Scenario S4-B: E₀=2.0J"
echo "Initial Energy: 2.0 J (400% of baseline)"
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
    --**.initialEnergy=2.0 \
    --seed-set=$SEED \
    > "$RESULTS_DIR/simulation.log" 2>&1

# Move CSV files
mv results/*.csv "$RESULTS_DIR/" 2>/dev/null || true
mv results/*.sca "$RESULTS_DIR/" 2>/dev/null || true

echo "[$SCENARIO] Completed!"

echo "========================================="
echo "Scenario S4-B: Single run completed!"
echo "Extracting metrics..."
echo "========================================="

# Extract metrics
python3 extract_metrics.py "$RESULTS_DIR"

echo "Results available in: $RESULTS_DIR"
echo "Plots available in: $RESULTS_DIR/validation_plots/"
