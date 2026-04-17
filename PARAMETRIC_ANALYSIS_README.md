# Parametric Analysis - Quick Reference

## Directory Structure
```
results/
├── multi-run/                        # Baseline: N=100, P=0.1, v=10, E=0.5J (✓ Done)
├── S1-CH-Probability/               # Clustering density variations
│   ├── S1-A-P005/    (P=0.05)      # Low clustering
│   ├── S1-B-P020/    (P=0.2)       # High clustering
│   └── S1-summary/                  # Comparative analysis
├── S2-Node-Density/                 # Network scalability
│   ├── S2-A-N200/    (N=200)       # Medium density
│   ├── S2-B-N300/    (N=300)       # High density
│   └── S2-summary/
├── S3-UAV-Speed/                    # UAV mobility impact
│   ├── S3-A-v15/     (v=15 m/s)    # Moderate speed
│   ├── S3-B-v20/     (v=20 m/s)    # High speed
│   └── S3-summary/
├── S4-Initial-Energy/               # Network lifetime scaling
│   ├── S4-A-E10/     (E=1.0J)      # Double energy
│   ├── S4-B-E20/     (E=2.0J)      # Quadruple energy
│   └── S4-summary/
└── cross-scenario-analysis/         # All scenarios compared
```

## Quick Start Commands

### Run All Scenarios (≈2 hours)
```bash
./run_all_scenarios.sh
```

### Run Specific Scenarios
```bash
./run_all_scenarios.sh S1        # Only clustering scenarios (≈30 min)
./run_all_scenarios.sh S1 S3     # Clustering + UAV speed (≈1 hour)
```

### Run Single Configuration
```bash
./run_scenario_S1-A.sh           # CH Probability P=0.05 (≈14 min)
./run_scenario_S2-A.sh           # Node Density N=200 (≈14 min)
```

### Manual Analysis
```bash
# Analyze single configuration
python3 analyze_multi_run.py results/S1-CH-Probability/S1-A-P005 30

# Scenario-level comparison
python3 analyze_scenario_summary.py S1

# Cross-scenario analysis
python3 analyze_cross_scenario.py
```

## Scenario Configurations

| Scenario | Config | Parameter | Value | Baseline | Change |
|----------|--------|-----------|-------|----------|--------|
| **S1-A** | Low CH | P (CH prob) | 0.05 | 0.1 | 50% |
| **S1-B** | High CH | P (CH prob) | 0.2 | 0.1 | 200% |
| **S2-A** | Med Density | N (nodes) | 200 | 100 | 200% |
| **S2-B** | High Density | N (nodes) | 300 | 100 | 300% |
| **S3-A** | Mod Speed | v (UAV m/s) | 15 | 10 | 150% |
| **S3-B** | High Speed | v (UAV m/s) | 20 | 10 | 200% |
| **S4-A** | Double Energy | E₀ (Joules) | 1.0 | 0.5 | 200% |
| **S4-B** | Quad Energy | E₀ (Joules) | 2.0 | 0.5 | 400% |

## Expected Outputs Per Configuration

Each configuration generates:
- ✓ 30 complete simulation runs (run_1/ ... run_30/)
- ✓ 8 validation plots (FND, LND, PDR, delay, CHs, throughput, cluster size, energy)
- ✓ Statistical summary with 95% confidence intervals
- ✓ Variance analysis (reproducibility check)

## Publication-Ready Outputs

### Scenario Summaries (4 scenarios)
- Comparative bar plots (Baseline vs A vs B)
- Statistical comparison tables
- CSV + formatted text tables

### Cross-Scenario Analysis
- Individual metric comparisons (6 plots)
- 2×3 grid comparison (compact view)
- Sensitivity analysis (parameter trends)
- LaTeX tables for paper inclusion

### Total Generated
- 97 publication-ready figures (300 DPI)
- 13 statistical tables
- 240 complete simulation runs
- All with 95% confidence intervals

## Execution Time Estimates

| Task | Duration |
|------|----------|
| Single configuration (30 runs) | ≈14 min |
| Single scenario (2 configs) | ≈28 min |
| All scenarios (8 configs) | ≈2 hours |
| Analysis scripts | <5 min |

## Files Created

**Run Scripts:**
- [run_scenario_S1-A.sh](run_scenario_S1-A.sh) - CH Probability 0.05
- [run_scenario_S1-B.sh](run_scenario_S1-B.sh) - CH Probability 0.2
- [run_scenario_S2-A.sh](run_scenario_S2-A.sh) - 200 nodes
- [run_scenario_S2-B.sh](run_scenario_S2-B.sh) - 300 nodes
- [run_scenario_S3-A.sh](run_scenario_S3-A.sh) - UAV 15 m/s
- [run_scenario_S3-B.sh](run_scenario_S3-B.sh) - UAV 20 m/s
- [run_scenario_S4-A.sh](run_scenario_S4-A.sh) - Energy 1.0J
- [run_scenario_S4-B.sh](run_scenario_S4-B.sh) - Energy 2.0J

**Analysis Scripts:**
- [analyze_multi_run.py](analyze_multi_run.py) - Per-configuration analysis
- [analyze_scenario_summary.py](analyze_scenario_summary.py) - Scenario-level comparison
- [analyze_cross_scenario.py](analyze_cross_scenario.py) - Cross-scenario analysis

**Master Script:**
- [run_all_scenarios.sh](run_all_scenarios.sh) - Orchestrates everything

**Documentation:**
- [sim-settings/PARAMETRIC_ANALYSIS_GUIDE.txt](sim-settings/PARAMETRIC_ANALYSIS_GUIDE.txt) - Comprehensive guide
- [sim-settings/scenarios.txt](sim-settings/scenarios.txt) - Original scenario definitions

## Next Steps

1. **Verify baseline exists:**
   ```bash
   ls results/multi-run/statistical_summary.csv
   ```

2. **Choose execution strategy:**
   - Quick test: `./run_scenario_S1-A.sh` (one config)
   - Single scenario: `./run_all_scenarios.sh S1` (2 configs)
   - Full study: `./run_all_scenarios.sh` (all 8 configs)

3. **Monitor progress:**
   - Watch terminal output
   - Check log file: `parametric_analysis_*.log`

4. **Review results:**
   - Individual plots: `results/S*/S*-*/validation_plots/`
   - Scenario summaries: `results/S*/*-summary/`
   - Cross-scenario: `results/cross-scenario-analysis/`

5. **Publication preparation:**
   - All plots are 300 DPI PNG format
   - LaTeX tables ready in cross-scenario-analysis/
   - Statistical summaries include 95% CI for all metrics
