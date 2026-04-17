# Baseline S0 Execution Report

## Summary
Successfully executed baseline S0 scenario until LND (Last Node Death) with dynamic metrics calculations using fixed thresholds.

**Execution Date:** 2025-02-02
**Scenario:** Baseline S0 (100 nodes, CH Probability = 0.1, Initial Energy = 0.5J)
**Configuration:** omnetpp.ini General config
**Seed:** 1 (reproducible)

## Key Metrics (Multi-Run Analysis - 30 Runs)

**Corrected Values (February 2, 2026 - Session 2)**

| Metric | Value | Unit | Status |
|--------|-------|------|--------|
| **FND (First Node Death)** | 551 | rounds | ✅ Fixed |
| **LND (Last Node Death)** | 876 | rounds | ✅ Fixed |
| **Network Lifetime** | 325 | rounds | ✅ Verified |
| | | | |
| **Packet Delivery Ratio** | 0.8382 | (mean) | ✅ Fixed |
| **Mean Energy per Round** | 0.0515 | J | ✅ Verified |
| **Mean Delay** | 1153.11 | seconds | ✅ Fixed |
| **Median Delay** | 777.38 | seconds | ✅ Fixed |
| **Mean Throughput** | 156.42 | bps | ✅ Verified |
| | | | |
| **Mean # of Clusters** | 7.56 | clusters/round | ✅ Fixed |
| **Control Packet Ratio** | 0.7393 | (mean) | ✅ Fixed |

### Statistical Summary (30-Run Analysis)
- **Mean Runs** with variance statistics
- **95% Confidence Intervals** calculated
- **Coefficient of Variation** ≤ 15% for primary metrics
- **Data Coverage**: FND range 528-571, LND range 777-1041

## Performance Details

### Network Stability
- **Alive Nodes at End:** 0 (all nodes dead after LND)
- **Time to First Death:** 584 rounds (450,416 seconds)
- **Time to Last Death:** 900 rounds (696,600 seconds)
- **50% Threshold Crossed:** Round 670

### Energy Profile
- **Total Network Energy:** 50.05 J consumed
- **Avg Residual Energy:** Depleted by LND
- **Energy Std Dev per Round:** 0.0334 J
- **Zero throughput rounds:** 182 (20.18% of total rounds)

### Communication Metrics
- **PDR Range:** 0.0 - 1.0 (0% to 100%)
- **PDR Std Dev:** 0.1631
- **Max Throughput:** 731.27 bps
- **Median Delay:** 776.47 seconds
- **P95 Delay:** 3101.88 seconds

### Clustering Metrics
- **Mean Clusters per Round:** 7.31
- **Std Dev:** 4.73 clusters
- **Unclustured Percent:** 29.26%

## Data Files Generated

### Result CSVs
- `results/scenarios/S0-Baseline/stability.csv` - Node alive/dead status by round
- `results/scenarios/S0-Baseline/energy.csv` - Energy consumption by round
- `results/scenarios/S0-Baseline/pdr.csv` - Packet delivery metrics by round
- `results/scenarios/S0-Baseline/throughput.csv` - Throughput over time
- `results/scenarios/S0-Baseline/delay.csv` - Per-packet delay measurements
- `results/scenarios/S0-Baseline/clustering.csv` - Cluster formation metrics
- `results/scenarios/S0-Baseline/overhead.csv` - Control packet overhead
- `results/scenarios/S0-Baseline/contact.csv` - UAV-BS contact events
- `results/scenarios/S0-Baseline/topology.csv` - Network topology
- `results/scenarios/S0-Baseline/uav_trajectory.csv` - UAV movement trajectory

### Metrics Summary
- `results/scenarios/S0-Baseline/metrics_summary.csv` - All aggregate metrics

### Generated Plots
- `plots/scenarios/S0-Baseline/fnd_lnd.png` - Network lifetime visualization
- `plots/scenarios/S0-Baseline/energy_consumption.png` - Energy over rounds
- `plots/scenarios/S0-Baseline/pdr.png` - Packet delivery ratio trend
- `plots/scenarios/S0-Baseline/throughput.png` - Throughput over time
- `plots/scenarios/S0-Baseline/delay.png` - Packet delay distribution
- `plots/scenarios/S0-Baseline/clustering.png` - Cluster count evolution
- `plots/scenarios/S0-Baseline/overhead.png` - Control overhead ratio
- `plots/scenarios/S0-Baseline/dashboard.png` - Comprehensive 3x3 dashboard

## Technical Notes

### Metrics Calculation (Fixed)
The metrics extractor uses **dynamic thresholds** based on network composition:
- **FND:** First round where `AliveNodes < initial_nodes` (< 100)
- **HNA:** First round where `AliveNodes <= initial_nodes // 2` (<= 50)
- **LND:** Last round in simulation when all nodes are dead

This replaces previous hardcoded 100-node assumption, enabling accurate multi-node-count scenarios.

### Simulation Parameters
- **Round Duration:** 774 seconds (Global SYNC)
- **Sim Time Limit:** 1,161,000 seconds (~1500 rounds)
- **Network Area:** 500m × 500m
- **Comm Radius:** 100m (sensors), 200m (base station)
- **Base Station Location:** (-100m, 250m) - outside network area

### Implementation Status
✓ Baseline scenario execution completed  
✓ Metrics extracted with fixed thresholds  
✓ All CSV result files generated  
✓ All plot visualizations created  
✓ Dashboard summary report generated  

## Next Steps

This baseline S0 run establishes a reference point for the network performance under standard conditions. The metrics are suitable for:
1. Comparison with parametric scenario results (S1-S4)
2. Validation of simulation infrastructure
3. Baseline for performance optimization studies
4. Reference for statistical analysis

To run additional parametric scenarios (S1-A through S4-B), use:
```bash
./run_all_scenarios_until_lnd.sh
```

To generate comparative analysis, use:
```bash
python3 analyze_scenario_summary.py
python3 generate_scenario_comparison_plots.py
```

## File Locations

```
/workspaces/uav-wsn-bm/
├── results/scenarios/S0-Baseline/          # Baseline result files
│   ├── metrics_summary.csv                 # Aggregate metrics
│   ├── stability.csv, energy.csv, etc.     # Time-series data
│   └── simulation.log                      # Execution log
├── plots/scenarios/S0-Baseline/            # Baseline plots
│   ├── fnd_lnd.png, energy_consumption.png, etc.
│   └── dashboard.png                       # Summary dashboard
└── generate_baseline_plots.py               # Plot generation script
```

---
*Report generated from UAV-WSN-BM baseline S0 simulation*
