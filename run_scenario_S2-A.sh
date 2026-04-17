#!/bin/bash
# Scenario S2-A: Node Density N=200 (30 runs)
# Tests network scalability with doubled nodes

SCENARIO="S2-A-N200"
RESULTS_DIR="results/S2-Node-Density/$SCENARIO"
SEED=1  # Consistent seed across all scenarios

echo "========================================="
echo "Running Scenario S2-A: N=200"
echo "Node Density: 200 nodes (200% of baseline)"
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
    --**.numNodes=200 \
    --seed-set=$SEED \
    > "$RESULTS_DIR/simulation.log" 2>&1

# Move CSV files
mv results/*.csv "$RESULTS_DIR/" 2>/dev/null || true
mv results/*.sca "$RESULTS_DIR/" 2>/dev/null || true

echo "[$SCENARIO] Completed!"

echo "========================================="
echo "Scenario S2-A: Single run completed!"
echo "Extracting metrics..."
echo "========================================="

# Extract metrics
python3 extract_metrics.py "$RESULTS_DIR"

echo "Results available in: $RESULTS_DIR"
echo "Plots available in: $RESULTS_DIR/validation_plots/"
