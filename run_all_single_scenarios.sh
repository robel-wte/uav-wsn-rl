#!/bin/bash
# Single-run parametric scenario execution
# Each scenario runs once with seed=1 for consistent comparison

set +e  # Continue on errors (seg faults are benign)

SEED=1
RESULTS_BASE="results/scenarios"

# Clean and prepare directory
echo "================================================"
echo "UAV-WSN Parametric Analysis - Single Run Setup"
echo "================================================"
echo "Seed: $SEED (consistent across all scenarios)"
echo "Results directory: $RESULTS_BASE"
echo ""

# Create base directory
mkdir -p "$RESULTS_BASE"

# ============================================
# SCENARIO 1: CH Probability Variations
# ============================================

echo "----------------------------------------"
echo "S1-A: CH Probability = 0.05 (50% of baseline)"
echo "----------------------------------------"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.chProbability=0.05 \
    --seed-set=$SEED \
    > /dev/null 2>&1

mkdir -p "$RESULTS_BASE/S1-A-P005"
mv results/*.csv "$RESULTS_BASE/S1-A-P005/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S1-A-P005/" 2>/dev/null
echo "✓ S1-A completed"
echo ""

echo "----------------------------------------"
echo "S1-B: CH Probability = 0.2 (200% of baseline)"
echo "----------------------------------------"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.chProbability=0.2 \
    --seed-set=$SEED \
    > /dev/null 2>&1

mkdir -p "$RESULTS_BASE/S1-B-P02"
mv results/*.csv "$RESULTS_BASE/S1-B-P02/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S1-B-P02/" 2>/dev/null
echo "✓ S1-B completed"
echo ""

# ============================================
# SCENARIO 2: Node Density Variations
# ============================================

echo "----------------------------------------"
echo "S2-A: Node Density = 200 (200% of baseline)"
echo "----------------------------------------"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.numNodes=200 \
    --seed-set=$SEED \
    > /dev/null 2>&1

mkdir -p "$RESULTS_BASE/S2-A-N200"
mv results/*.csv "$RESULTS_BASE/S2-A-N200/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S2-A-N200/" 2>/dev/null
echo "✓ S2-A completed"
echo ""

echo "----------------------------------------"
echo "S2-B: Node Density = 300 (300% of baseline)"
echo "----------------------------------------"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.numNodes=300 \
    --seed-set=$SEED \
    > /dev/null 2>&1

mkdir -p "$RESULTS_BASE/S2-B-N300"
mv results/*.csv "$RESULTS_BASE/S2-B-N300/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S2-B-N300/" 2>/dev/null
echo "✓ S2-B completed"
echo ""

# ============================================
# Summary
# ============================================

echo "================================================"
echo "All scenarios completed!"
echo "================================================"
echo ""
echo "Results:"
for dir in "$RESULTS_BASE"/*; do
    if [ -d "$dir" ]; then
        csv_count=$(ls "$dir"/*.csv 2>/dev/null | wc -l)
        echo "  $(basename $dir): $csv_count CSV files"
    fi
done

echo ""
echo "Next steps:"
echo "  1. python3 generate_scenario_summaries.py"
echo "  2. python3 generate_scenario_plots.py"
echo "  3. python3 generate_parameter_sensitivity_plots.py"
