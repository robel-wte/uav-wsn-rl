#!/bin/bash

# Quick script to run remaining scenarios with error handling
set +e  # Don't exit on errors

RESULTS_BASE="results/scenarios"
SEED=1

echo "Running remaining scenarios (S1-B through S4-B)..."

# S1-B
echo "S1-B: CH Probability = 0.2"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.chProbability=0.2 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S1-B-P02"
mv results/*.csv "$RESULTS_BASE/S1-B-P02/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S1-B-P02/" 2>/dev/null
echo "✓ S1-B done"

# S2-A
echo "S2-A: Node Density = 200"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.numNodes=200 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S2-A-N200"
mv results/*.csv "$RESULTS_BASE/S2-A-N200/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S2-A-N200/" 2>/dev/null
echo "✓ S2-A done"

# S2-B
echo "S2-B: Node Density = 300"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.numNodes=300 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S2-B-N300"
mv results/*.csv "$RESULTS_BASE/S2-B-N300/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S2-B-N300/" 2>/dev/null
echo "✓ S2-B done"

# S3-A
echo "S3-A: UAV Speed = 15 m/s"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.minSpeed=15 --**.maxSpeed=15 --**.searchSpeed=15 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S3-A-V15"
mv results/*.csv "$RESULTS_BASE/S3-A-V15/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S3-A-V15/" 2>/dev/null
echo "✓ S3-A done"

# S3-B
echo "S3-B: UAV Speed = 20 m/s"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.minSpeed=20 --**.maxSpeed=20 --**.searchSpeed=20 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S3-B-V20"
mv results/*.csv "$RESULTS_BASE/S3-B-V20/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S3-B-V20/" 2>/dev/null
echo "✓ S3-B done"

# S4-A
echo "S4-A: Initial Energy = 1.0 J"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.initialEnergy=1.0 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S4-A-E10"
mv results/*.csv "$RESULTS_BASE/S4-A-E10/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S4-A-E10/" 2>/dev/null
echo "✓ S4-A done"

# S4-B
echo "S4-B: Initial Energy = 2.0 J"
./uav-wsn-bm -u Cmdenv -c General -n . --cmdenv-express-mode=true --cmdenv-performance-display=false --**.initialEnergy=2.0 --seed-set=$SEED > /dev/null 2>&1
mkdir -p "$RESULTS_BASE/S4-B-E20"
mv results/*.csv "$RESULTS_BASE/S4-B-E20/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S4-B-E20/" 2>/dev/null
echo "✓ S4-B done"

echo ""
echo "All scenarios completed!"
echo "Results in: $RESULTS_BASE/"
ls -d $RESULTS_BASE/*/
