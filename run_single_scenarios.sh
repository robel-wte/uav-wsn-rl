#!/bin/bash
#
# Single-Run Scenario Execution
# Runs each parametric scenario once with consistent seed=1 (matching baseline)
# Baseline multi-run validation already completed (30 runs)
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SEED=1  # Consistent seed matching baseline
RESULTS_BASE="results/scenarios"

echo "=========================================="
echo "Parametric Scenario Analysis (Single Run)"
echo "=========================================="
echo "Baseline: Already validated (30 runs)"
echo "Seed: $SEED (consistent across all scenarios)"
echo "Results: $RESULTS_BASE/"
echo ""

# Ensure results directory exists
mkdir -p "$RESULTS_BASE"

# Clean any previous single-run results
rm -f "$RESULTS_BASE"/*.csv "$RESULTS_BASE"/*.sca "$RESULTS_BASE"/*.log

echo -e "${BLUE}Scenario S1-A: CH Probability = 0.05${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.chProbability=0.05 \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S1-A-P005.log" 2>&1 || true

# Move results
mkdir -p "$RESULTS_BASE/S1-A-P005"
mv results/*.csv "$RESULTS_BASE/S1-A-P005/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S1-A-P005/" 2>/dev/null || true
echo -e "${GREEN}✓ S1-A Complete${NC}\n"

echo -e "${BLUE}Scenario S1-B: CH Probability = 0.2${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.chProbability=0.2 \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S1-B-P020.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S1-B-P020"
mv results/*.csv "$RESULTS_BASE/S1-B-P020/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S1-B-P020/" 2>/dev/null || true
echo -e "${GREEN}✓ S1-B Complete${NC}\n"

echo -e "${BLUE}Scenario S2-A: Nodes = 200${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.numNodes=200 \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S2-A-N200.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S2-A-N200"
mv results/*.csv "$RESULTS_BASE/S2-A-N200/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S2-A-N200/" 2>/dev/null || true
echo -e "${GREEN}✓ S2-A Complete${NC}\n"

echo -e "${BLUE}Scenario S2-B: Nodes = 300${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.numNodes=300 \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S2-B-N300.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S2-B-N300"
mv results/*.csv "$RESULTS_BASE/S2-B-N300/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S2-B-N300/" 2>/dev/null || true
echo -e "${GREEN}✓ S2-B Complete${NC}\n"

echo -e "${BLUE}Scenario S3-A: UAV Speed = 15 m/s${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.minSpeed=15mps \
    --**.maxSpeed=15mps \
    --**.searchSpeed=15mps \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S3-A-v15.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S3-A-v15"
mv results/*.csv "$RESULTS_BASE/S3-A-v15/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S3-A-v15/" 2>/dev/null || true
echo -e "${GREEN}✓ S3-A Complete${NC}\n"

echo -e "${BLUE}Scenario S3-B: UAV Speed = 20 m/s${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.minSpeed=20mps \
    --**.maxSpeed=20mps \
    --**.searchSpeed=20mps \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S3-B-v20.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S3-B-v20"
mv results/*.csv "$RESULTS_BASE/S3-B-v20/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S3-B-v20/" 2>/dev/null || true
echo -e "${GREEN}✓ S3-B Complete${NC}\n"

echo -e "${BLUE}Scenario S4-A: Initial Energy = 1.0 J${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.initialEnergy=1.0 \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S4-A-E10.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S4-A-E10"
mv results/*.csv "$RESULTS_BASE/S4-A-E10/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S4-A-E10/" 2>/dev/null || true
echo -e "${GREEN}✓ S4-A Complete${NC}\n"

echo -e "${BLUE}Scenario S4-B: Initial Energy = 2.0 J${NC}"
echo "Running simulation..."
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.initialEnergy=2.0 \
    --seed-set=$SEED \
    > "$RESULTS_BASE/S4-B-E20.log" 2>&1 || true

mkdir -p "$RESULTS_BASE/S4-B-E20"
mv results/*.csv "$RESULTS_BASE/S4-B-E20/" 2>/dev/null || true
mv results/*.sca "$RESULTS_BASE/S4-B-E20/" 2>/dev/null || true
echo -e "${GREEN}✓ S4-B Complete${NC}\n"

echo "=========================================="
echo "All scenarios completed!"
echo "=========================================="
echo "Generating comparison analysis..."

# Extract metrics from each scenario
python3 extract_metrics.py "$RESULTS_BASE/S1-A-P005"
python3 extract_metrics.py "$RESULTS_BASE/S1-B-P020"
python3 extract_metrics.py "$RESULTS_BASE/S2-A-N200"
python3 extract_metrics.py "$RESULTS_BASE/S2-B-N300"
python3 extract_metrics.py "$RESULTS_BASE/S3-A-v15"
python3 extract_metrics.py "$RESULTS_BASE/S3-B-v20"
python3 extract_metrics.py "$RESULTS_BASE/S4-A-E10"
python3 extract_metrics.py "$RESULTS_BASE/S4-B-E20"

# Generate comparison plots
python3 compare_scenarios.py

echo ""
echo "Results saved to: $RESULTS_BASE/"
echo "Comparison plots: plots/scenario_comparison_*.png"
echo ""
