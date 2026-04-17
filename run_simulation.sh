#!/bin/bash
# UAV-WSN Simulation Runner with Automated Metrics Collection
# Usage: ./run_simulation.sh
# 
# This script requires OMNeT++ to be installed persistently at /workspaces/omnetpp-6.0.3
# Source /workspaces/omnetpp-setup.sh to configure environment

set -euo pipefail

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "UAV-WSN-BM Simulation Runner"
echo "S_Ideal Scenario: 400 nodes, 500x500m"
echo "=========================================="
echo ""

# Load OMNeT++ environment
OMNETPP_SETUP="/workspaces/omnetpp-setup.sh"
if [ ! -f "$OMNETPP_SETUP" ]; then
    echo "❌ Error: OMNeT++ setup script not found"
    echo "Please ensure OMNeT++ is installed to /workspaces/omnetpp-6.0.3"
    exit 1
fi

echo "Loading OMNeT++ environment..."
set +u
source "$OMNETPP_SETUP"
set -u
echo ""

# Check binary exists
if [ ! -f "out/clang-release/uav-wsn-bm" ]; then
    echo "❌ Binary not found at out/clang-release/uav-wsn-bm"
    echo "Rebuilding project..."
    make MODE=release -j4 || exit 1
fi

# Create/clean results directory
mkdir -p results plots
rm -f results/*.csv results/*.txt

echo "🚀 Starting simulation..."
echo "   Target: Run until LND + 100 rounds"
echo "   Expected: ~1900-2000 rounds"
echo "   Estimated time: 30-90 minutes"
echo ""
echo "⏳ Simulation running... (press Ctrl+C to stop)"
echo ""

# Run simulation
./out/clang-release/uav-wsn-bm -u Cmdenv -c General -n . omnetpp.ini 2>&1 | tee simulation.log
sim_status=${PIPESTATUS[0]}

# Check if simulation completed
if [ "$sim_status" -eq 0 ]; then
    echo ""
    echo "✅ Simulation completed successfully!"
    echo ""
    
    # Generate plots
    if [ -f "results/stability.csv" ]; then
        echo "📊 Generating plots from CSV data..."
        if python3 generate_plots.py; then
            echo ""
            echo "=========================================="
            echo "✅ ALL TASKS COMPLETED SUCCESSFULLY!"
            echo "=========================================="
            echo ""
            echo "Output files:"
            echo "  📄 CSV data:    results/*.csv"
            echo "  📊 Plots:       plots/*.png"
            echo "  📝 Summary:     plots/summary_statistics.txt"
            echo "  📋 Log:         simulation.log"
            echo ""
        else
            echo "⚠️  Simulation completed but plot generation failed"
            echo "   Check results/*.csv files manually"
        fi
    else
        echo "⚠️  Simulation finished but results/stability.csv is missing"
        echo "   Check simulation.log for errors"
        exit 1
    fi
else
    echo ""
    echo "❌ Simulation failed or was interrupted"
    echo "   Check simulation.log for details"
    exit 1
fi
