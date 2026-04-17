# S0-Baseline Inconsistency Fix Report

## Date: February 2, 2026

### Summary of All Changes Made
This report documents all issues found and fixed in the S0-Baseline plots, including statistical inconsistencies, visual enhancements, and formatting updates.

## Issues Identified

### 1. FND/LND Inconsistency (CRITICAL)
**Problem:**
- Summary Statistics: FND=551 rounds, LND=876 rounds
- Previous Plot: FND=528 rounds, LND=908 rounds

**Root Cause:**
The plot was calculating FND/LND from the **mean curve** (aggregated data), not from the **mean of individual run values**. This is statistically incorrect because:
- Mean curve FND: First round where mean(alive_nodes) < initial_nodes
- Correct FND: Mean of individual FND values from each run

**Fix Applied:**
Modified `regenerate_baseline_plots.py` to:
1. Calculate FND/LND for each of the 30 runs individually
2. Take the mean of these 30 values
3. Display the correct mean FND=551 and LND=876 on the plot

### 2. PDR Plot Inconsistency
**Problem:**
- Summary Statistics: Mean PDR = 0.8382
- Previous Plot: Showed different value (mean of per-round means)

**Root Cause:**
Plot was calculating: `mean(mean_PDR_per_round)` instead of `mean(mean_PDR_per_run)`

**Fix Applied:**
Changed calculation to compute mean PDR per run first, then average across runs:
```python
mean_pdr_per_run = combined.groupby('run_id')['PDR'].mean()
true_mean_pdr = mean_pdr_per_run.mean()
```

**Verified Result:** Plot now shows Overall Mean=0.8382 (matches summary)

### 3. Delay Plot Inconsistency
**Problem:**
- Summary Statistics: Mean=1153.11s, Median=777.38s
- Previous Plot: Pooled all packets from all runs (slight difference)

**Root Cause:**
Plot was calculating pooled statistics instead of mean of per-run statistics

**Fix Applied:**
Changed to calculate per-run means and medians, then average:
```python
mean_delay_per_run = combined.groupby('run_id')['Delay_s'].mean()
true_mean_delay = mean_delay_per_run.mean()
```

**Verified Result:** Plot now shows Mean=1153.11s (matches summary)

### 4. Clustering Metrics Inconsistency
**Problem:**
- Summary Statistics: Mean CHs = 7.56
- Previous Plot: Showed different value (mean of per-round means)

**Root Cause:**
Plot calculated: `mean(mean_CHs_per_round)` instead of `mean(mean_CHs_per_run)`

**Fix Applied:**
Changed calculation to:
```python
mean_chs_per_run = ch_per_round.groupby('run_id')['ClusterID'].mean()
true_mean_chs = mean_chs_per_run.mean()
```

**Verified Result:** Plot now shows Overall Mean=7.56 (matches summary)

### 5. Control Overhead Inconsistency
**Problem:**
- Summary Statistics: Mean Control Ratio = 0.7393
- Previous Plot: Showed 0.739 (rounded from per-round mean)

**Root Cause:**
Plot calculated: `mean(mean_control_per_round)` instead of `mean(mean_control_per_run)`

**Fix Applied:**
Changed calculation to:
```python
mean_control_per_run = combined.groupby('run_id')['ControlRatio'].mean()
true_mean_control = mean_control_per_run.mean()
```

**Verified Result:** Plot now shows Overall Mean=0.7393 (matches summary)

## Summary of Changes

### Files Modified:
1. `regenerate_baseline_plots.py` (5 functions updated)

### Statistical Methodology:
**Before:** 
- FND/LND: Calculated from aggregated mean curve
- Other metrics: Mean of per-round means

**After:**
- FND/LND: Mean of individual run values
- Other metrics: Mean of per-run means

### Verification Results:
All plots now display values that **exactly match** the summary statistics in `summary_stat_new.txt` and `statistical_summary_new.csv`.

| Metric | Summary | Plot | Status |
|--------|---------|------|--------|
| FND | 551 rounds | 551 rounds | ✅ Fixed |
| LND | 876 rounds | 876 rounds | ✅ Fixed |
| Mean PDR | 0.8382 | 0.8382 | ✅ Fixed |
| Mean Delay | 1153.11s | 1153.11s | ✅ Fixed |
| Median Delay | 777.38s | 777.38s | ✅ Fixed |
| Mean CHs | 7.56 | 7.56 | ✅ Fixed |
| Mean Control Ratio | 0.7393 | 0.7393 | ✅ Fixed |

## Impact:
- All 9 plots in `plots/scenarios/S0-Baseline/` have been regenerated
- Plots now accurately reflect the multi-run statistical analysis
- Results are now publication-ready with correct statistical representation

---

## Additional Enhancements Applied Same Day

### 6. Visual Enhancement: Dead Nodes Curve Added
**network_lifetime.png** now displays:
- **Mean Alive Nodes**: Blue curve showing declining alive nodes
- **Mean Dead Nodes**: Red curve showing increasing dead nodes
- **FND/LND Markers**: Orange (551) and black (876) vertical lines
- **Dual Confidence Visualization**: Both curves displayed for complete network status picture

### 7. Formatting Standardization
Applied professional publication-quality formatting to all 9 plots:
- **Style**: seaborn-v0_8-whitegrid
- **Font Sizes Increased**:
  - Base: 16pt (from 12pt)
  - Axis labels: 18pt (from 12pt)
  - Titles: 20pt (from 14pt)
  - Tick labels: 16pt (from 10pt)
  - Legend: 14pt (from 9-10pt)
- **Grid Enhancement**: 1.2pt lines, 50% alpha, #d0d0d0 color
- **Axes**: 1.8pt borders for definition
- **Background**: White (publication-ready)

### 8. X-Axis Standardization
Consistent axis ranges for better comparison:

**Round-Based Plots** (7 plots): xlim=[0, 1200] rounds
- network_lifetime.png
- energy_consumption.png
- total_energy_consumption_per_round.png
- pdr.png
- average_delay_per_round.png
- clustering_metrics.png
- control_overhead.png

**Delay-Based Plot** (1 plot): xlim=[0, 5000] seconds
- delay_distribution.png

**Benefits**:
- Visual alignment for cross-plot analysis
- Easy identification of temporal patterns
- Extra space accommodates future extensions

### 9. Confidence Band Removal
Removed ±1 Std Dev shaded areas from all curve plots:
- Cleaner, less cluttered visualization
- Focus on mean curves and reference lines
- File size reduction: 45-52% average per plot
- Before: 368-609 KB → After: 185-239 KB

## Final Verification Results:

| Metric | Summary | Plot | Status |
|--------|---------|------|--------|
| FND | 551 rounds | 551 rounds | ✅ Fixed |
| LND | 876 rounds | 876 rounds | ✅ Fixed |
| Mean PDR | 0.8382 | 0.8382 | ✅ Fixed |
| Mean Delay | 1153.11s | 1153.11s | ✅ Fixed |
| Median Delay | 777.38s | 777.38s | ✅ Fixed |
| Mean CHs | 7.56 | 7.56 | ✅ Fixed |
| Mean Control Ratio | 0.7393 | 0.7393 | ✅ Fixed |

## Summary of Changes:

### Files Modified
1. `regenerate_baseline_plots.py` - All 9 plotting functions updated

### Plots Regenerated
- ✅ network_lifetime.png (with dead nodes curve)
- ✅ energy_consumption.png
- ✅ total_energy_consumption_per_round.png
- ✅ pdr.png
- ✅ throughput.png
- ✅ delay_distribution.png
- ✅ average_delay_per_round.png
- ✅ clustering_metrics.png
- ✅ control_overhead.png

### Final Status
- All 9 plots are statistically accurate
- All plots follow standard professional formatting
- All plots have consistent x-axis ranges
- All plots are optimized for publication
- All plots have cleaner appearance without confidence bands
- Total regeneration time: February 2, 2026, 08:49 UTC
