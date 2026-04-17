#!/bin/bash
# Re-run S3 and S4 scenarios

set +e
SEED=1
RESULTS_BASE="results/scenarios"

echo "Re-running S3-A: UAV Speed = 15 m/s"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.minSpeed=15mps \
    --**.maxSpeed=15mps \
    --**.searchSpeed=15mps \
    --seed-set=$SEED \
    > s3a.log 2>&1
mkdir -p "$RESULTS_BASE/S3-A-V15"
mv results/*.csv "$RESULTS_BASE/S3-A-V15/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S3-A-V15/" 2>/dev/null
echo "S3-A done - check s3a.log for details"
ls -lh "$RESULTS_BASE/S3-A-V15/"

echo ""
echo "Re-running S3-B: UAV Speed = 20 m/s"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.minSpeed=20mps \
    --**.maxSpeed=20mps \
    --**.searchSpeed=20mps \
    --seed-set=$SEED \
    > s3b.log 2>&1
mkdir -p "$RESULTS_BASE/S3-B-V20"
mv results/*.csv "$RESULTS_BASE/S3-B-V20/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S3-B-V20/" 2>/dev/null
echo "S3-B done - check s3b.log for details"
ls -lh "$RESULTS_BASE/S3-B-V20/"

echo ""
echo "Re-running S4-A: Initial Energy = 1.0 J"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.initialEnergy=1.0J \
    --seed-set=$SEED \
    > s4a.log 2>&1
mkdir -p "$RESULTS_BASE/S4-A-E10"
mv results/*.csv "$RESULTS_BASE/S4-A-E10/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S4-A-E10/" 2>/dev/null
echo "S4-A done - check s4a.log for details"
ls -lh "$RESULTS_BASE/S4-A-E10/"

echo ""
echo "Re-running S4-B: Initial Energy = 2.0 J"
./uav-wsn-bm -u Cmdenv -c General -n . \
    --cmdenv-express-mode=true \
    --cmdenv-performance-display=false \
    --**.initialEnergy=2.0J \
    --seed-set=$SEED \
    > s4b.log 2>&1
mkdir -p "$RESULTS_BASE/S4-B-E20"
mv results/*.csv "$RESULTS_BASE/S4-B-E20/" 2>/dev/null
mv results/*.sca "$RESULTS_BASE/S4-B-E20/" 2>/dev/null
echo "S4-B done - check s4b.log for details"
ls -lh "$RESULTS_BASE/S4-B-E20/"

echo ""
echo "All S3 and S4 scenarios complete!"
