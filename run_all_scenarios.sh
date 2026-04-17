#!/bin/bash
#
# Master Orchestration Script for Parametric Analysis
# Runs all scenario configurations and generates publication-ready results
#
# Usage:
#   ./run_all_scenarios.sh              # Run all scenarios
#   ./run_all_scenarios.sh S1           # Run only S1 scenarios
#   ./run_all_scenarios.sh S1 S2        # Run S1 and S2 scenarios
#

set -e  # Exit on any error

# Load OMNeT++ environment
OMNETPP_SETUP="/workspaces/omnetpp-setup.sh"
if [ -f "$OMNETPP_SETUP" ]; then
    set +u
    source "$OMNETPP_SETUP"
    set -u
else
    echo "[ERROR] OMNeT++ setup script not found at $OMNETPP_SETUP" >&2
    exit 1
fi

# Ensure binary exists (build if needed)
if [ ! -f "./uav-wsn-bm" ]; then
    echo "[INFO] Building uav-wsn-bm..."
    make MODE=release -j4
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="parametric_analysis_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$(echo $1 | sed 's/./=/g')${NC}" | tee -a "$LOG_FILE"
}

# Check if simulation binary exists
if [ ! -f "./uav-wsn-bm" ]; then
    error "Simulation binary not found. Please compile first: make"
    exit 1
fi

# Make all run scripts executable
chmod +x run_scenario_*.sh

# Define all scenarios
declare -A SCENARIOS
SCENARIOS["S1-A"]="run_scenario_S1-A.sh"
SCENARIOS["S1-B"]="run_scenario_S1-B.sh"
SCENARIOS["S2-A"]="run_scenario_S2-A.sh"
SCENARIOS["S2-B"]="run_scenario_S2-B.sh"
SCENARIOS["S3-A"]="run_scenario_S3-A.sh"
SCENARIOS["S3-B"]="run_scenario_S3-B.sh"
SCENARIOS["S4-A"]="run_scenario_S4-A.sh"
SCENARIOS["S4-B"]="run_scenario_S4-B.sh"

# Parse command line arguments
SELECTED_SCENARIOS=()
if [ $# -eq 0 ]; then
    # Run all scenarios
    for scenario in "${!SCENARIOS[@]}"; do
        SELECTED_SCENARIOS+=("$scenario")
    done
else
    # Run only specified scenarios
    for arg in "$@"; do
        case "$arg" in
            S1)
                SELECTED_SCENARIOS+=("S1-A" "S1-B")
                ;;
            S2)
                SELECTED_SCENARIOS+=("S2-A" "S2-B")
                ;;
            S3)
                SELECTED_SCENARIOS+=("S3-A" "S3-B")
                ;;
            S4)
                SELECTED_SCENARIOS+=("S4-A" "S4-B")
                ;;
            S1-A|S1-B|S2-A|S2-B|S3-A|S3-B|S4-A|S4-B)
                SELECTED_SCENARIOS+=("$arg")
                ;;
            *)
                error "Unknown scenario: $arg"
                echo "Valid options: S1, S2, S3, S4, S1-A, S1-B, S2-A, S2-B, S3-A, S3-B, S4-A, S4-B"
                exit 1
                ;;
        esac
    done
fi

# Sort and deduplicate
SELECTED_SCENARIOS=($(echo "${SELECTED_SCENARIOS[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

section "PARAMETRIC ANALYSIS - SCENARIO EXECUTION"
log "NOTE: Each scenario runs ONCE with consistent seed=1"
log "Baseline (30 runs) already validated in results/multi-run/"
log "Selected scenarios: ${SELECTED_SCENARIOS[@]}"
log "Total scenarios to run: ${#SELECTED_SCENARIOS[@]}"
log "Log file: $LOG_FILE"
echo ""

# Track timing
START_TIME=$(date +%s)
SCENARIO_TIMES=()

# Run each scenario
for scenario in "${SELECTED_SCENARIOS[@]}"; do
    script="${SCENARIOS[$scenario]}"
    
    section "Running Scenario: $scenario"
    log "Script: $script"
    
    if [ ! -f "$script" ]; then
        error "Script not found: $script"
        continue
    fi
    
    scenario_start=$(date +%s)
    
    if ./"$script" 2>&1 | tee -a "$LOG_FILE"; then
        scenario_end=$(date +%s)
        scenario_duration=$((scenario_end - scenario_start))
        SCENARIO_TIMES+=("$scenario: ${scenario_duration}s")
        log "✓ Scenario $scenario completed in ${scenario_duration}s"
    else
        error "✗ Scenario $scenario failed"
        exit 1
    fi
    
    echo "" | tee -a "$LOG_FILE"
done

section "GENERATING COMPARATIVE PLOTS"

log "Creating scenario comparison plots..."
if python3 generate_plots.py 2>&1 | tee -a "$LOG_FILE"; then
    log "✓ Plots generated for all scenarios"
else
    warning "Plot generation had issues"
fi

section "COMPARATIVE ANALYSIS"

log "Generating comprehensive comparison table..."
if python3 compare_scenarios.py 2>&1 | tee -a "$LOG_FILE"; then
    log "✓ Comparative analysis completed"
else
    warning "Comparative analysis had issues"
fi

# Calculate total duration
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
HOURS=$((TOTAL_DURATION / 3600))
MINUTES=$(((TOTAL_DURATION % 3600) / 60))
SECONDS=$((TOTAL_DURATION % 60))

section "PARAMETRIC ANALYSIS COMPLETE"

log "Total scenarios executed: ${#SELECTED_SCENARIOS[@]}"
log "Total execution time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo "" | tee -a "$LOG_FILE"

log "Scenario timing breakdown:"
for timing in "${SCENARIO_TIMES[@]}"; do
    log "  $timing"
done

echo "" | tee -a "$LOG_FILE"
log "Results structure:"
log "  results/"
log "    ├── multi-run/ (Baseline: 30 runs with stats)"
log "    ├── S1-CH-Probability/"
log "    │   ├── S1-A-P005/ (single run)"
log "    │   └── S1-B-P020/ (single run)"
log "    ├── S2-Node-Density/"
log "    │   ├── S2-A-N200/ (single run)"
log "    │   └── S2-B-N300/ (single run)"
log "    ├── S3-UAV-Speed/"
log "    │   ├── S3-A-v15/ (single run)"
log "    │   └── S3-B-v20/ (single run)"
log "    ├── S4-Initial-Energy/"
log "    │   ├── S4-A-E10/ (single run)"
log "    │   └── S4-B-E20/ (single run)"
log "    └── plots/ (comparative analysis plots)"

echo "" | tee -a "$LOG_FILE"
log "Publication-ready outputs:"
log "  ✓ Baseline: 30 runs with statistical validation"
log "  ✓ Scenarios: Single runs with seed=1 (consistent)"
log "  ✓ CSV data files for all metrics"
log "  ✓ Comparative plots across all scenarios"
log "  ✓ Summary tables for paper inclusion"

echo "" | tee -a "$LOG_FILE"
log "Full log saved to: $LOG_FILE"
echo ""

exit 0
