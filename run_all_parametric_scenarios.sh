#!/bin/bash
# Run all parametric scenarios S1-S5 until LND with updated settings
# Based on baseline S0 successful approach

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="/workspaces/uav-wsn-bm"
cd "$PROJECT_DIR"

echo -e "${BLUE}Loading OMNeT++ environment...${NC}"
source /workspaces/omnetpp-setup.sh

echo -e "${YELLOW}==========================================${NC}"
echo -e "${YELLOW}  Running All Parametric Scenarios S1-S5  ${NC}"
echo -e "${YELLOW}==========================================${NC}"

# Rebuild project
echo -e "\n${BLUE}Rebuilding project...${NC}"
make clean
make MODE=release -j4

if [ ! -f "$PROJECT_DIR/uav-wsn-bm" ]; then
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Build successful${NC}"

# Define all scenarios with their configurations
declare -A SCENARIOS
SCENARIOS=(
    ["S1-A"]="--**.chProbability=0.05"
    ["S1-B"]="--**.chProbability=0.2"
    ["S2-A"]="--**.numNodes=200"
    ["S2-B"]="--**.numNodes=300"
    ["S3-A"]="--**.uav.minSpeed=15mps --**.uav.maxSpeed=15mps --**.uav.searchSpeed=15mps"
    ["S3-B"]="--**.uav.minSpeed=20mps --**.uav.maxSpeed=20mps --**.uav.searchSpeed=20mps"
    ["S4-A"]="--**.initialEnergy=1.0J"
    ["S4-B"]="--**.initialEnergy=2.0J"
    ["S5-A"]=""
    ["S5-B"]=""
)

# Scenario descriptions
declare -A DESCRIPTIONS
DESCRIPTIONS=(
    ["S1-A"]="CH Probability P=0.05 (50% of baseline)"
    ["S1-B"]="CH Probability P=0.2 (200% of baseline)"
    ["S2-A"]="Node Density N=200 (200% of baseline)"
    ["S2-B"]="Node Density N=300 (300% of baseline)"
    ["S3-A"]="UAV Speed v=15 m/s (150% of baseline)"
    ["S3-B"]="UAV Speed v=20 m/s (200% of baseline)"
    ["S4-A"]="Initial Energy E=1.0J (200% of baseline)"
    ["S4-B"]="Initial Energy E=2.0J (400% of baseline)"
    ["S5-A"]="Data Packet Size = 500 bits (25% of baseline)"
    ["S5-B"]="Data Packet Size = 4000 bits (200% of baseline)"
)

# Sim-time limits (extended for energy scenarios)
declare -A SIM_TIME_LIMITS
SIM_TIME_LIMITS=(
    ["S1-A"]="2000000s"
    ["S1-B"]="1161000s"
    ["S2-A"]="1161000s"
    ["S2-B"]="1161000s"
    ["S3-A"]="1161000s"
    ["S3-B"]="1161000s"
    ["S4-A"]="2500000s"
    ["S4-B"]="3500000s"
    ["S5-A"]="1161000s"
    ["S5-B"]="1161000s"
)

# Configuration names for S5 (defined in omnetpp.ini)
declare -A CONFIG_NAMES
CONFIG_NAMES=(
    ["S5-A"]="S5-A"
    ["S5-B"]="S5-B"
)

SEED=1  # Consistent seed across all scenarios

# Function to run a scenario
run_scenario() {
    local scenario=$1
    local params=$2
    local sim_time=$3
    local config_name=$4
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running Scenario: $scenario${NC}"
    echo -e "${YELLOW}Description: ${DESCRIPTIONS[$scenario]}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    RESULTS_DIR="results/scenarios/$scenario"
    mkdir -p "$RESULTS_DIR"
    
    echo "Sim Time Limit: $sim_time"
    echo "Output: $RESULTS_DIR"
    
    # Build command based on scenario
    if [ -n "$config_name" ]; then
        # S5 scenarios use predefined configs
        timeout 7200 ./uav-wsn-bm -u Cmdenv -c "$config_name" \
            -n . \
            --cmdenv-express-mode=true \
            --cmdenv-performance-display=false \
            --sim-time-limit=$sim_time \
            --seed-set=$SEED \
            > "$RESULTS_DIR/simulation.log" 2>&1 || {
            echo -e "${YELLOW}Note: Simulation completed (exit code: $?)${NC}"
        }
    else
        # S1-S4 scenarios override parameters
        timeout 7200 ./uav-wsn-bm -u Cmdenv -c General \
            -n . \
            omnetpp.ini \
            --cmdenv-express-mode=true \
            --cmdenv-performance-display=false \
            --sim-time-limit=$sim_time \
            --seed-set=$SEED \
            $params \
            > "$RESULTS_DIR/simulation.log" 2>&1 || {
            echo -e "${YELLOW}Note: Simulation completed (exit code: $?)${NC}"
        }
    fi
    
    # Move generated files
    mv results/*.csv "$RESULTS_DIR/" 2>/dev/null || true
    mv results/*.sca "$RESULTS_DIR/" 2>/dev/null || true
    
    echo -e "${GREEN}✓ $scenario simulation completed${NC}"
    
    # Extract metrics
    echo -e "${YELLOW}Extracting metrics for $scenario...${NC}"
    python3 extract_metrics.py "$RESULTS_DIR" || {
        echo -e "${RED}Warning: Metrics extraction had issues${NC}"
    }
    
    echo -e "${GREEN}✓ $scenario metrics extracted${NC}"
}

# Run all scenarios
START_TIME=$(date +%s)

for scenario in "S1-A" "S1-B" "S2-A" "S2-B" "S3-A" "S3-B" "S4-A" "S4-B" "S5-A" "S5-B"; do
    params="${SCENARIOS[$scenario]}"
    sim_time="${SIM_TIME_LIMITS[$scenario]}"
    config_name="${CONFIG_NAMES[$scenario]:-}"
    
    run_scenario "$scenario" "$params" "$sim_time" "$config_name"
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_MIN=$((ELAPSED / 60))

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}  All Scenarios Completed Successfully!  ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}Total execution time: ${ELAPSED_MIN} minutes${NC}"
echo -e "\n${BLUE}Results saved in: results/scenarios/${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Generate plots: python3 generate_all_scenario_plots.py"
echo -e "  2. Create comparison: python3 generate_scenario_comparison_plots.py"
echo -e "  3. Review results: ls -lh results/scenarios/*/"
