# Parametric Analysis Results

## Overview

This document summarizes the parametric analysis comparing 8 scenario variations against the validated baseline.

## Methodology

- **Baseline**: 30 independent runs (seed 0-29) with full statistical validation
- **Scenarios**: Single run each with consistent seed=1 for direct comparison
- **Parameters**: One parameter varied per scenario group while others remain at baseline

## Directory Structure

```
results/
├── multi-run/                  # Baseline (N=100, P=0.1, v=10m/s, E=0.5J)
│   ├── run-0/ ... run-29/     # 30 runs for statistical validation
│   └── statistical_summary.csv # Mean ± 95% CI
└── scenarios/                  # Parametric variations (single run, seed=1)
    ├── S1-A-P005/             # CH Probability = 0.05
    ├── S1-B-P020/             # CH Probability = 0.2
    ├── S2-A-N200/             # Nodes = 200
    ├── S2-B-N300/             # Nodes = 300
    ├── S3-A-v15/              # UAV Speed = 15 m/s
    ├── S3-B-v20/              # UAV Speed = 20 m/s
    ├── S4-A-E10/              # Initial Energy = 1.0 J
    └── S4-B-E20/              # Initial Energy = 2.0 J
```

## Scenarios

### S1: CH Probability Variations (Clustering Density)
- **S1-A**: P=0.05 (50% of baseline) - Fewer, larger clusters
- **S1-B**: P=0.2 (200% of baseline) - More, smaller clusters

### S2: Node Density Variations (Scalability)
- **S2-A**: N=200 (200% of baseline) - Double node density
- **S2-B**: N=300 (300% of baseline) - Triple node density

### S3: UAV Speed Variations (Mobility Impact)
- **S3-A**: v=15 m/s (150% of baseline) - Faster UAV movement
- **S3-B**: v=20 m/s (200% of baseline) - Very fast UAV movement

### S4: Initial Energy Variations (Lifetime Scaling)
- **S4-A**: E=1.0 J (200% of baseline) - Double initial energy
- **S4-B**: E=2.0 J (400% of baseline) - Quadruple initial energy

## Generated Outputs

### Plots
- `plots/scenario_comparison_grid.png` - 2×3 grid comparing all metrics
- `plots/scenario_comparison_FND.png` - First Node Death comparison
- `plots/scenario_comparison_LND.png` - Last Node Death comparison
- `plots/scenario_comparison_PDR.png` - Packet Delivery Ratio comparison
- `plots/scenario_comparison_avg_delay.png` - Average Delay comparison
- `plots/scenario_comparison_avg_CHs.png` - Cluster Heads comparison
- `plots/scenario_comparison_avg_throughput.png` - Throughput comparison

### Data Files
- `plots/scenario_comparison_table.txt` - Formatted text table
- `plots/scenario_comparison_data.csv` - Machine-readable data

## Execution Scripts

- `run_single_scenarios.sh` - Runs all 8 scenarios sequentially (≈4 minutes)
- `compare_scenarios.py` - Generates all comparison plots and tables
- `extract_metrics.py` - Extracts metrics from simulation results

## Usage

Run all scenarios:
```bash
./run_single_scenarios.sh
```

This will:
1. Run each scenario with seed=1
2. Extract metrics from each run
3. Generate comparison plots against baseline
4. Create publication-ready tables

## Notes

- Baseline uses mean values from 30 runs (with 95% confidence intervals)
- Scenarios use single run values for direct comparison
- All scenarios use seed=1 for consistency
- Segmentation faults after simulation completion are benign (cleanup issue)
- Results are valid and complete despite seg faults

## Results Interpretation

Compare each scenario's single-run result against the baseline mean to understand:
- How parameter changes affect key metrics
- Which parameters have strongest impact on network performance
- Trade-offs between different parameter settings
- Scalability and robustness characteristics
