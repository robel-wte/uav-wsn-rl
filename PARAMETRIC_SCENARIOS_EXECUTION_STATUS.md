# Parametric Scenarios S1-S5 Execution Summary

**Execution Date:** February 2, 2026  
**Status:** In Progress

## Overview

All parametric scenarios (S1-S5) are being executed with the updated baseline settings from S0-Baseline. Each scenario tests a specific parameter variation to analyze its impact on network performance.

## Scenario Definitions

### S1: CH Probability Variation
- **S1-A:** P = 0.05 (50% of baseline) ✓ COMPLETED
  - FND: 925 rounds, LND: 1621 rounds, PDR: 0.6648
- **S1-B:** P = 0.2 (200% of baseline) ✓ COMPLETED
  - FND: 374 rounds, LND: 463 rounds, PDR: 0.9750

### S2: Node Density Variation
- **S2-A:** N = 200 nodes (200% of baseline) ✓ COMPLETED
- **S2-B:** N = 300 nodes (300% of baseline) 🔄 IN PROGRESS

### S3: UAV Speed Variation
- **S3-A:** v = 15 m/s (150% of baseline) ⏳ PENDING
- **S3-B:** v = 20 m/s (200% of baseline) ⏳ PENDING

### S4: Initial Energy Variation
- **S4-A:** E₀ = 1.0 J (200% of baseline) ⏳ PENDING
- **S4-B:** E₀ = 2.0 J (400% of baseline) ⏳ PENDING

### S5: Data Packet Size Variation
- **S5-A:** Size = 500 bits (25% of baseline) ⏳ PENDING
- **S5-B:** Size = 4000 bits (200% of baseline) ⏳ PENDING

## Execution Configuration

### Common Settings (from S0-Baseline)
- **Seed:** 1 (consistent across all scenarios for reproducibility)
- **Simulation Time:** 1,161,000s (1500 rounds) for most scenarios
- **Extended Time:** 2,000,000s for S1-A, 2,500,000s for S4-A, 3,500,000s for S4-B
- **Network:** 100 nodes baseline, 500m × 500m area
- **Initial Energy:** 0.5 J baseline
- **CH Probability:** 0.1 baseline
- **UAV Speed:** 10 m/s baseline
- **Data Packet Size:** 2000 bits baseline

### Simulation Parameters (Updated)
- Round Duration: 774s
- UAV Height: 30m
- UAV Communication Radius: 192m
- Sensor Communication Radius: 100m
- Base Station Position: (-100, 250)

## Expected Execution Time

| Scenario | Node Count | Energy | Estimated Time | Status |
|----------|-----------|--------|----------------|--------|
| S1-A | 100 | 0.5J | ~15 min | ✓ Complete |
| S1-B | 100 | 0.5J | ~10 min | ✓ Complete |
| S2-A | 200 | 0.5J | ~20 min | ✓ Complete |
| S2-B | 300 | 0.5J | ~30 min | 🔄 Running |
| S3-A | 100 | 0.5J | ~12 min | ⏳ Pending |
| S3-B | 100 | 0.5J | ~10 min | ⏳ Pending |
| S4-A | 100 | 1.0J | ~25 min | ⏳ Pending |
| S4-B | 100 | 2.0J | ~40 min | ⏳ Pending |
| S5-A | 100 | 0.5J | ~10 min | ⏳ Pending |
| S5-B | 100 | 0.5J | ~12 min | ⏳ Pending |
| **Total** | - | - | **~3-4 hours** | - |

## Output Structure

### For Each Scenario
```
results/scenarios/{SCENARIO}/
├── simulation.log              # Simulation output
├── metrics_summary.csv         # Aggregate metrics (FND, LND, PDR, etc.)
├── stability.csv               # FND, HNA, LND per round
├── energy_consumption.csv      # Total and residual energy
├── pdr.csv                     # Packet delivery ratio
├── throughput.csv              # Network throughput
├── delay.csv                   # End-to-end delay
├── clustering_metrics.csv      # CH count, unclustered nodes
├── control_overhead.csv        # Control packet overhead
└── [additional CSV files]      # Contact, network, topology data
```

### Generated Plots
```
plots/scenarios/{SCENARIO}/
├── network_lifetime.png        # Alive + Dead nodes with FND/LND
├── energy_consumption.png      # Total + Average residual (2-panel)
├── pdr.png                     # Packet delivery ratio
├── throughput.png              # Raw + Moving average
├── delay_distribution.png      # Histogram with mean/median
├── average_delay_per_round.png # Delay + packet count (2-panel)
├── clustering_metrics.png      # CHs + Unclustered % (2-panel)
└── control_overhead.png        # Control overhead over time
```

## Key Observations (Preliminary)

### S1-A (P=0.05 - Low CH Density)
- **FND Extended:** 925 rounds (vs 584 baseline) → 58% improvement
- **LND Extended:** 1621 rounds (vs 900 baseline) → 80% improvement
- **PDR Reduced:** 0.6648 (vs 0.7993 baseline) → 17% reduction
- **Interpretation:** Fewer CHs → longer distances to CH → reduced PDR but better energy distribution → extended lifetime

### S1-B (P=0.2 - High CH Density)
- **FND Reduced:** 374 rounds (vs 584 baseline) → 36% reduction
- **LND Reduced:** 463 rounds (vs 900 baseline) → 49% reduction
- **PDR Improved:** 0.9750 (vs 0.7993 baseline) → 22% improvement
- **Interpretation:** More CHs → shorter member-to-CH distances → better PDR but faster CH energy depletion → reduced lifetime

### Trade-off Analysis
Lower CH probability (S1-A) extends network lifetime at the cost of PDR, while higher CH probability (S1-B) improves data delivery but reduces lifetime. This demonstrates the fundamental energy-performance trade-off in WSN clustering.

## Next Steps

Once all scenarios complete:

1. **Generate Plots:** Run `python3 generate_all_scenario_plots.py`
   - Creates 8 professional plots per scenario (80 total plots)
   - DPI 300, professional styling matching S0-Baseline

2. **Scenario Comparison:** Run `python3 generate_scenario_comparison_plots.py`
   - Cross-scenario FND/LND comparison
   - PDR vs Lifetime trade-off analysis
   - Energy efficiency comparison
   - Parameter sensitivity analysis

3. **Statistical Analysis:** Run `python3 analyze_cross_scenario.py`
   - Calculate relative performance metrics
   - Generate summary tables
   - Statistical significance testing

4. **Documentation:** Create comprehensive results markdown
   - Per-scenario detailed analysis
   - Cross-scenario comparison
   - Key findings and insights
   - Recommendations for parameter tuning

## Monitoring

**Execution Log:** `parametric_scenarios_execution.log`

**Check Progress:**
```bash
tail -50 parametric_scenarios_execution.log | grep -E "(Running Scenario|completed|Extracting)"
```

**Check Completed Scenarios:**
```bash
ls -lh results/scenarios/S*/*.csv | grep metrics_summary.csv
```

**Monitor Process:**
```bash
ps aux | grep run_all_parametric_scenarios
```

## Technical Notes

- Each scenario runs with seed=1 for reproducibility
- Segmentation faults (exit code 139) are expected post-LND cleanup issues
- All CSV files generate successfully despite segfaults
- Metrics extraction uses dynamic FND/HNA thresholds (10% and 50% node death)
- Plot generation matches S0-Baseline professional standards

---

**Last Updated:** In Progress - Check `parametric_scenarios_execution.log` for real-time status
