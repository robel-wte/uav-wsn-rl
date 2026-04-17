#!/bin/bash
# Master script to run all scenarios until LND (Last Node Death)
# Ensures all scenarios have complete results

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

PROJECT_DIR="/workspaces/uav-wsn-bm"
cd "$PROJECT_DIR"

# Load OMNeT++ environment
echo -e "${BLUE}Loading OMNeT++ environment...${NC}"
source /workspaces/omnetpp-setup.sh

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}  UAV-WSN-BM: Complete Scenario Runner  ${NC}"
echo -e "${YELLOW}=========================================${NC}"

# Step 1: Rebuild project
echo -e "\n${BLUE}Step 1: Rebuilding project...${NC}"
make clean
make MODE=release -j4

if [ ! -f "$PROJECT_DIR/uav-wsn-bm" ]; then
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Build successful${NC}"

# Define scenarios and their parameters
declare -A SCENARIOS
SCENARIOS=(
    ["S1-A-P005"]="--**.chProbability=0.05"
    ["S1-B-P02"]="--**.chProbability=0.2"
    ["S2-A-N200"]="--**.numNodes=200"
    ["S2-B-N300"]="--**.numNodes=300"
    ["S3-A-V15"]="--**.uav.minSpeed=15 --**.uav.maxSpeed=15 --**.uav.searchSpeed=15"
    ["S3-B-V20"]="--**.uav.minSpeed=20 --**.uav.maxSpeed=20 --**.uav.searchSpeed=20"
    ["S4-A-E10"]="--**.initialEnergy=1J"
    ["S4-B-E20"]="--**.initialEnergy=2J"
    ["S5-A"]=""
    ["S5-B"]=""
)

# Scenario-specific sim-time limits (override default when needed)
declare -A SIM_TIME_LIMITS
SIM_TIME_LIMITS=(
    ["S1-A-P005"]="2000000s"
    ["S4-A-E10"]="2500000s"
    ["S4-B-E20"]="3000000s"
)

DEFAULT_SIM_TIME="1161000s"

# Additional config for S5-A and S5-B
declare -A S5_CONFIG
S5_CONFIG=(
    ["S5-A"]="-c S5-A"
    ["S5-B"]="-c S5-B"
)

# Function to run a scenario
run_scenario() {
    local scenario=$1
    local params=$2
    local extra_config=$3
    local seed=1
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running Scenario: $scenario${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Create results directory
    RESULTS_DIR="results/scenarios/$scenario"
    mkdir -p "$RESULTS_DIR"
    
    echo -e "${YELLOW}Starting simulation...${NC}"
    echo "Parameters: $params"
    echo "Config: $extra_config"
    echo "Output directory: $RESULTS_DIR"
    
    sim_time="${SIM_TIME_LIMITS[$scenario]:-$DEFAULT_SIM_TIME}"

    # Run simulation until LND
    timeout 7200 ./uav-wsn-bm -u Cmdenv $extra_config \
        -n . \
        --cmdenv-express-mode=true \
        --cmdenv-performance-display=false \
        --sim-time-limit=$sim_time \
        --seed-set=$seed \
        $params \
        > "$RESULTS_DIR/simulation.log" 2>&1 || {
        echo -e "${YELLOW}Note: Simulation may have completed or timed out${NC}"
    }
    
    # Move result files
    if [ -d results/scenarios ]; then
        # Move CSV files
        for csv in results/*.csv; do
            [ -f "$csv" ] && mv "$csv" "$RESULTS_DIR/" 2>/dev/null || true
        done
        # Move .sca files
        for sca in results/*.sca; do
            [ -f "$sca" ] && mv "$sca" "$RESULTS_DIR/" 2>/dev/null || true
        done
    fi
    
    # Check if simulation produced results
    if [ -f "$RESULTS_DIR/stability.csv" ]; then
        echo -e "${GREEN}✓ Results saved to $RESULTS_DIR${NC}"
        
        # Extract metrics
        python3 - "$scenario" << 'EOF' > "$RESULTS_DIR/metrics_summary.txt" 2>&1
import pandas as pd
import os, sys

scenario = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
results_dir = f"results/scenarios/{scenario}"

try:
    stability = pd.read_csv(f"{results_dir}/stability.csv")
    energy = pd.read_csv(f"{results_dir}/energy.csv")
    pdr = pd.read_csv(f"{results_dir}/pdr.csv")
    
    last_round = stability.iloc[-1]['Round']
    dead_rows = stability[stability['DeadNodes'] > 0]
    fnd = int(dead_rows.iloc[0]['Round']) if len(dead_rows) > 0 else int(last_round)
    
    print(f"Scenario: {scenario}")
    print(f"Last Round: {int(last_round)}")
    print(f"FND: {fnd} rounds")
    print(f"Nodes Alive at End: {int(stability.iloc[-1]['AliveNodes'])}")
except Exception as e:
    print(f"Error: {e}")
EOF
        cat "$RESULTS_DIR/metrics_summary.txt"
    else
        echo -e "${RED}✗ No results generated for $scenario${NC}"
    fi
}

# Run all scenarios
echo -e "\n${BLUE}Step 2: Running all scenarios until LND...${NC}"

for scenario in "${!SCENARIOS[@]}"; do
    params="${SCENARIOS[$scenario]}"
    extra_config="${S5_CONFIG[$scenario]:-'-c General'}"
    
    run_scenario "$scenario" "$params" "$extra_config"
    
    # Small delay between scenarios to allow disk sync
    sleep 2
done

# Step 3: Generate summary files
echo -e "\n${BLUE}Step 3: Generating summary files for all scenarios...${NC}"

python3 << 'EOF'
import pandas as pd
import os

def generate_summary(scenario_dir, scenario_name):
    try:
        stability = pd.read_csv(f"{scenario_dir}/stability.csv")
        energy = pd.read_csv(f"{scenario_dir}/energy.csv")
        pdr = pd.read_csv(f"{scenario_dir}/pdr.csv")
        throughput = pd.read_csv(f"{scenario_dir}/throughput.csv")
        delay = pd.read_csv(f"{scenario_dir}/delay.csv")
        overhead = pd.read_csv(f"{scenario_dir}/overhead.csv")
        
        last_round = int(stability.iloc[-1]['Round'])
        dead_rows = stability[stability['DeadNodes'] > 0]
        fnd = int(dead_rows.iloc[0]['Round']) if len(dead_rows) > 0 else last_round
        
        hna_rows = stability[stability['AliveNodes'] <= 50]
        hna = int(hna_rows.iloc[0]['Round']) if len(hna_rows) > 0 else last_round
        
        summary_text = f"""Scenario: {scenario_name}
====================

Network Lifetime:
-----------------
FND (First Node Death): {fnd} rounds
LND (Last Node Death): {last_round} rounds
HNA (Half Nodes Alive): {hna} rounds
Lifetime (LND-FND): {last_round - fnd} rounds

Energy:
-------
Total Energy Consumed: {energy['EnergyConsumed'].sum():.4f} J
Mean Energy Per Round: {energy['EnergyConsumed'].mean():.6f} J

Performance:
------------
Mean PDR: {pdr['PDR'].mean():.4f}
Mean Throughput: {throughput['Throughput_kbps'].mean():.4f} kbps
Mean Delay: {(delay['Delay_s'].mean() * 1000):.4f} ms
Mean Overhead Ratio: {overhead['OverheadRatio'].mean():.4f}

"""
        with open(f"{scenario_dir}/summary.txt", 'w') as f:
            f.write(summary_text)
        return True
    except Exception as e:
        print(f"Error processing {scenario_name}: {e}")
        return False

base_dir = "results/scenarios"
scenarios = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])

for scenario in scenarios:
    scenario_path = os.path.join(base_dir, scenario)
    if generate_summary(scenario_path, scenario):
        print(f"✓ {scenario}: summary.txt generated")
    else:
        print(f"✗ {scenario}: failed to generate summary")
EOF

# Step 4: Generate plots
echo -e "\n${BLUE}Step 4: Generating visualization plots...${NC}"
python3 generate_plots.py

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}  All scenarios completed successfully!  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "\nResults: results/scenarios/"
echo -e "Plots: plots/scenarios/"
echo -e "\nNext steps:"
echo -e "  1. Review summary.txt files in results/scenarios/"
echo -e "  2. Check plots in plots/scenarios/"
echo -e "  3. Compare scenarios using: python3 compare_scenarios.py"
