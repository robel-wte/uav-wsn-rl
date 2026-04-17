#!/bin/bash

################################################################################
# UAV-WSN Scenario Execution Script
################################################################################
# Usage: ./run_scenario.sh <scenario_id> <num_runs> <parameters>
# Example: ./run_scenario.sh s1a-p005 10 "chProbability=0.05"
################################################################################

set -e  # Exit on error

# Check arguments
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <scenario_id> <num_runs> <parameters>"
    echo "Example: $0 s1a-p005 10 \"chProbability=0.05\""
    exit 1
fi

SCENARIO_ID=$1
NUM_RUNS=$2
PARAMS=$3

# Determine scenario folder based on scenario_id
if [[ $SCENARIO_ID == s1* ]]; then
    SCENARIO_FOLDER="scenario-s1"
elif [[ $SCENARIO_ID == s2* ]]; then
    SCENARIO_FOLDER="scenario-s2"
elif [[ $SCENARIO_ID == s3* ]]; then
    SCENARIO_FOLDER="scenario-s3"
elif [[ $SCENARIO_ID == s4* ]]; then
    SCENARIO_FOLDER="scenario-s4"
else
    echo "Error: Unknown scenario ID: $SCENARIO_ID"
    exit 1
fi

# Setup directories
BASE_DIR="results/${SCENARIO_FOLDER}/${SCENARIO_ID}"
LOG_DIR="${BASE_DIR}/logs"
mkdir -p "$BASE_DIR" "$LOG_DIR"

# Save execution metadata
METADATA_FILE="${BASE_DIR}/execution_metadata.txt"
echo "Scenario Execution Metadata" > "$METADATA_FILE"
echo "===========================" >> "$METADATA_FILE"
echo "Scenario ID: $SCENARIO_ID" >> "$METADATA_FILE"
echo "Scenario Folder: $SCENARIO_FOLDER" >> "$METADATA_FILE"
echo "Number of Runs: $NUM_RUNS" >> "$METADATA_FILE"
echo "Parameters: $PARAMS" >> "$METADATA_FILE"
echo "Start Time: $(date)" >> "$METADATA_FILE"
echo "Hostname: $(hostname)" >> "$METADATA_FILE"
echo "OMNeT++ Version: $(opp_run --version | head -1)" >> "$METADATA_FILE"
echo "" >> "$METADATA_FILE"

# Build simulation if needed
echo "[$(date +%H:%M:%S)] Building simulation..."
make clean && make

# Parse parameters based on scenario type
EXTRA_ARGS=""
if [[ $PARAMS == *"chProbability"* ]]; then
    PROB=$(echo "$PARAMS" | sed -n 's/.*chProbability=\([0-9.]*\).*/\1/p')
    EXTRA_ARGS="--*.node[*].chProbability=$PROB"
    echo "CH Probability: $PROB" >> "$METADATA_FILE"
elif [[ $PARAMS == *"numNodes"* ]]; then
    NODES=$(echo "$PARAMS" | sed -n 's/.*numNodes=\([0-9]*\).*/\1/p')
    EXTRA_ARGS="--*.numNodes=$NODES"
    echo "Number of Nodes: $NODES" >> "$METADATA_FILE"
elif [[ $PARAMS == *"uavSpeed"* ]]; then
    SPEED=$(echo "$PARAMS" | sed -n 's/.*uavSpeed=\([0-9]*\).*/\1/p')
    EXTRA_ARGS="--*.uav.minSpeed=${SPEED}mps --*.uav.maxSpeed=${SPEED}mps --*.uav.searchSpeed=${SPEED}mps"
    echo "UAV Speed: ${SPEED} m/s" >> "$METADATA_FILE"
elif [[ $PARAMS == *"initialEnergy"* ]]; then
    ENERGY=$(echo "$PARAMS" | sed -n 's/.*initialEnergy=\([0-9.]*\).*/\1/p')
    EXTRA_ARGS="--*.node[*].initialEnergy=${ENERGY}J"
    echo "Initial Energy: ${ENERGY} J" >> "$METADATA_FILE"
fi

echo "" >> "$METADATA_FILE"
echo "Extra OMNeT++ Arguments: $EXTRA_ARGS" >> "$METADATA_FILE"
echo "" >> "$METADATA_FILE"

# Run simulations
echo "[$(date +%H:%M:%S)] Starting $NUM_RUNS runs for scenario $SCENARIO_ID..."
echo ""

for ((run=0; run<$NUM_RUNS; run++)); do
    RUN_DIR="${BASE_DIR}/run-${run}"
    mkdir -p "$RUN_DIR"
    
    RUN_LOG="${LOG_DIR}/run-${run}.log"
    
    echo "[$(date +%H:%M:%S)] Run $run/$((NUM_RUNS-1)) - Seed: $run"
    echo "Run $run - Start: $(date)" >> "$METADATA_FILE"
    
    START_TIME=$(date +%s)
    
    # Execute simulation
    ./UavWsnNetwork -u Cmdenv -c General \
        --cmdenv-express-mode=true \
        --cmdenv-performance-display=false \
        --seed-set=$run \
        --output-scalar-file="${RUN_DIR}/General-#0.sca" \
        --output-vector-file="${RUN_DIR}/General-#0.vec" \
        $EXTRA_ARGS \
        > "$RUN_LOG" 2>&1
    
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "  ✓ Completed in ${DURATION}s"
        echo "Run $run - Status: SUCCESS - Duration: ${DURATION}s" >> "$METADATA_FILE"
        
        # Extract metrics immediately
        python3 extract_metrics.py "$RUN_DIR" > "${RUN_DIR}/metrics_extraction.log" 2>&1
        
        # Verify CSV files were generated
        if [ ! -f "${RUN_DIR}/energy.csv" ]; then
            echo "  ⚠ Warning: Metrics extraction failed for run $run"
            echo "Run $run - Metrics: FAILED" >> "$METADATA_FILE"
        else
            echo "Run $run - Metrics: SUCCESS" >> "$METADATA_FILE"
        fi
    else
        echo "  ✗ Failed with exit code $EXIT_CODE"
        echo "Run $run - Status: FAILED - Exit Code: $EXIT_CODE" >> "$METADATA_FILE"
    fi
    echo ""
done

# Record completion
echo "" >> "$METADATA_FILE"
echo "End Time: $(date)" >> "$METADATA_FILE"
echo "" >> "$METADATA_FILE"

# Run statistical analysis
echo "[$(date +%H:%M:%S)] Running statistical analysis..."
python3 analyze_multi_run.py "$BASE_DIR" --output "${BASE_DIR}/statistical_summary.csv" > "${LOG_DIR}/analysis.log" 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Statistical analysis completed"
    echo "Analysis: SUCCESS" >> "$METADATA_FILE"
else
    echo "  ✗ Statistical analysis failed (see ${LOG_DIR}/analysis.log)"
    echo "Analysis: FAILED" >> "$METADATA_FILE"
fi

# Generate validation plots
echo "[$(date +%H:%M:%S)] Generating validation plots..."
mkdir -p "${BASE_DIR}/validation_plots"
python3 generate_plots.py "$BASE_DIR" --output "${BASE_DIR}/validation_plots" > "${LOG_DIR}/plots.log" 2>&1

if [ $? -eq 0 ]; then
    echo "  ✓ Validation plots generated"
    echo "Plots: SUCCESS" >> "$METADATA_FILE"
else
    echo "  ✗ Plot generation failed (see ${LOG_DIR}/plots.log)"
    echo "Plots: FAILED" >> "$METADATA_FILE"
fi

# Summary
echo ""
echo "============================================================"
echo "Scenario $SCENARIO_ID Execution Complete"
echo "============================================================"
echo "Total Runs: $NUM_RUNS"
echo "Results Directory: $BASE_DIR"
echo "Logs Directory: $LOG_DIR"
echo ""
echo "Next Steps:"
echo "  1. Review statistical summary: ${BASE_DIR}/statistical_summary.csv"
echo "  2. Check validation plots: ${BASE_DIR}/validation_plots/"
echo "  3. Compare with baseline: python3 compare_with_baseline.py $BASE_DIR"
echo "============================================================"

# Generate quick summary
SUMMARY_FILE="${BASE_DIR}/quick_summary.txt"
echo "Scenario $SCENARIO_ID - Quick Summary" > "$SUMMARY_FILE"
echo "=====================================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

if [ -f "${BASE_DIR}/statistical_summary.txt" ]; then
    echo "Key Metrics (Mean ± 95% CI):" >> "$SUMMARY_FILE"
    echo "-----------------------------" >> "$SUMMARY_FILE"
    grep -E "FND|LND|PDR|Delay|CHs" "${BASE_DIR}/statistical_summary.txt" >> "$SUMMARY_FILE" 2>/dev/null || echo "Metrics not available" >> "$SUMMARY_FILE"
fi

echo ""
echo "Summary saved to: $SUMMARY_FILE"
