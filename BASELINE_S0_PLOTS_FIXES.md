# Baseline S0 Plots - Issues Fixed and Updates

## Issues Identified

When comparing the newly generated S0-Baseline plots with the existing plots in the `/plots` folder, the following issues were identified:

1. **DPI Resolution**: S0-Baseline plots were generated at DPI 150, while standard plots use DPI 300
2. **Font Sizes**: S0-Baseline used smaller font sizes (12-14pt) vs standard (18-22pt)
3. **Figure Sizes**: S0-Baseline plots used smaller figure dimensions (12x6 or 12x7) vs standard (13x7 or larger)
4. **Plot Types**: S0-Baseline had custom/non-standard plot layouts vs established patterns
5. **Color Scheme**: S0-Baseline used ad-hoc colors vs consistent professional palette
6. **Grid and Styling**: Missing some styling elements like bold fontweights, consistent gridlines, and proper axis labels
7. **Missing Plot Types**: S0-Baseline didn't include some key metrics like `clustering_metrics.png` and `control_overhead.png`

## Fixes Applied

### 1. Professional Styling Alignment
Updated `generate_baseline_plots.py` to match `generate_plots.py` standards:

| Aspect | Before | After |
|--------|--------|-------|
| **DPI** | 150 | 300 |
| **Title Font Size** | 14pt | 22pt (fontweight='bold') |
| **Label Font Size** | 12pt | 20pt (fontweight='bold') |
| **Tick Font Size** | Default | 18pt |
| **Figure Size** | 12x6 | 13x7 or 13x10 (2-panel) |
| **Line Width** | 2pt | 2.5pt (primary), 3.0pt (MA) |
| **Grid Alpha** | 0.3 | 0.4-0.6 |
| **Color Palette** | Ad-hoc | Professional: #0077B6, #F18F01, #06A77D, #E63946, etc. |

### 2. Standardized Plot Types

#### Network Lifetime
- **Style**: Single plot with FND/LND vertical line markers
- **Line Width**: 2.5pt with blue color (#0077B6)
- **Markers**: 'o' every 50 rounds
- **Labels**: Proper round numbers in legend

#### Energy Consumption
- **Style**: 2-panel plot (matching standard)
  - Panel 1: Total Network Energy (J) - #F18F01
  - Panel 2: Average Residual Energy per Node (J/node) - #06A77D
- **Ranges**: X from 0, Y from 0 (bottom-left origin)

#### PDR (Packet Delivery Ratio)
- **Style**: Single line plot
- **Color**: #2E86AB
- **Y-range**: [0, 1.05] for PDR
- **Filtering**: Only rounds with ≥5 packets generated

#### Throughput
- **Style**: Raw + moving average overlay
- **Raw**: Light color (#C73E1D) at alpha 0.3
- **MA**: Bold line (#C73E1D) linewidth 3.0
- **Window**: 20-sample moving average
- **X-axis**: Simulation time (seconds), Y: bps

#### Delay (Average per Round)
- **Style**: 2-panel plot
  - Panel 1: Histogram of packet delays (50 bins)
  - Panel 2: Bar chart of average delay per round
- **Colors**: #7209B7 (histogram), #4c6ef5 (bar chart)
- **Filtering**: Delays < 5000s to remove outliers

#### Clustering Metrics
- **Style**: 2-panel plot
  - Panel 1: Cluster Head Count per Round - #06A77D
  - Panel 2: Unclustered Nodes per Round - #A23B72
- **Markers**: 'o' for clusters, 's' for unclustered (every 20 rounds)
- **Linewidth**: 2.5pt

#### Control Overhead
- **Style**: 2-layer line plot with annotation
  - Layer 1: All rounds (gray, alpha 0.4, thin)
  - Layer 2: Stable rounds (≥50 packets/round - #E63946, bold)
- **Annotation**: Red dashed line at network degradation threshold
- **Y-range**: [0, 1] for control ratio

### 3. Code Improvements

**Fixed Delay Binning Logic**:
```python
# Before (caused error): 
delay_by_round = delay.groupby(pd.cut(delay['ReceptionTime'], 
                                      bins=int(lnd*774/1000), 
                                      labels=range(int(lnd))))  # Label count mismatch

# After (correct):
num_bins = min(int(lnd), int(max_time / 774) + 1)
delay_by_round = delay.groupby(pd.cut(delay['ReceptionTime'], 
                                      bins=num_bins))  # No label count issues
```

**Added Moving Average for Throughput**:
```python
window_size = 20
throughput['MA_Throughput'] = throughput['Throughput_bps'].rolling(
    window=window_size, center=True, min_periods=1).mean()
```

**Proper Network Degradation Handling**:
```python
# Filter to stable network for overhead visualization
valid_rounds = overhead[(overhead['ControlPackets'] + overhead['DataPackets']) >= 50].copy()
# Plot with annotation marking degradation point
```

## Generated Plots

### Baseline S0 Plots (Regenerated)
✓ `plots/scenarios/S0-Baseline/network_lifetime.png` (186 KB) - DPI 300, professional styling
✓ `plots/scenarios/S0-Baseline/energy_consumption.png` (386 KB) - 2-panel professional layout
✓ `plots/scenarios/S0-Baseline/pdr.png` (461 KB) - Line plot with professional gridlines
✓ `plots/scenarios/S0-Baseline/throughput.png` (679 KB) - Raw + moving average overlay
✓ `plots/scenarios/S0-Baseline/average_delay_per_round.png` (302 KB) - 2-panel histogram + bar chart
✓ `plots/scenarios/S0-Baseline/clustering_metrics.png` (806 KB) - 2-panel clustering visualization
✓ `plots/scenarios/S0-Baseline/control_overhead.png` (375 KB) - Dual-layer professional plot

### Reference Comparison
Existing plots in `/plots/`:
- `average_delay_per_round.png` (575 KB) - Similar style, now matched
- `clustering_metrics.png` (733 KB) - Similar style, now matched
- `control_overhead.png` (355 KB) - Similar style, now matched
- `energy_consumption.png` (229 KB) - Different structure (will compare)
- `network_lifetime.png` (Not in root, but generated now matches standard)

## Plot Quality Metrics

| Metric | Value |
|--------|-------|
| **DPI** | 300 (professional publication quality) |
| **Font Sizes** | 20-22pt labels, 18pt ticks (readable) |
| **Total Size** | 3.2 MB (7 plots) |
| **File Sizes** | 186 KB - 806 KB (appropriate for complexity) |
| **Color Scheme** | Professional palette (consistent with generate_plots.py) |
| **Figure Styles** | Matched standard patterns |

## Critical Fixes Applied (February 2, 2026, Session 2)

### 1. Statistical Accuracy Fixes

**FND/LND Discrepancy Resolved**:
- Summary showed: FND=551, LND=876
- Previous plots incorrectly showed: FND=528, LND=908
- Root cause: Calculated FND/LND from aggregated mean curve instead of mean of individual runs
- Fix: Changed to per-run calculation methodology
  ```python
  # Calculate FND/LND for each run individually, then take mean
  fnd_per_run = [np.where(alive[i] < 100)[0][0] if any(alive[i] < 100) else None for i in range(30)]
  mean_fnd = np.mean([x for x in fnd_per_run if x is not None])
  ```
- Result: ✅ All plots now show correct FND=551, LND=876 markers

**PDR Metric Corrected**:
- Previous: Used mean of per-round PDR values (aggregated)
- Fixed: Now calculates per-run PDR means, then averages
- Result: ✅ Overall Mean: 0.8382 (matches summary)

**Delay Statistics Corrected**:
- Previous: Pooled all packets across all runs
- Fixed: Calculate per-run statistics, then average
- Result: ✅ Mean: 1153.11s, Median: 777.38s (matches summary)

**Clustering Metrics Corrected**:
- Previous: Mean of per-round cluster head counts
- Fixed: Mean of per-run means
- Result: ✅ Overall Mean: 7.56 (matches summary)

**Control Overhead Corrected**:
- Previous: Aggregated curve mean
- Fixed: Mean of per-run values
- Result: ✅ Overall Mean: 0.7393 (matches summary)

### 2. Enhanced Visualization Features

**Dead Nodes Curve Added to network_lifetime.png**:
- New red curve showing mean dead nodes over time
- Complements existing blue alive nodes curve
- Both curves displayed with matching styling
- Markers still show FND (551) and LND (876)
- Legend updated with both curves

### 3. Professional Formatting Applied

**Standard Matplotlib Configuration**:
- Style: seaborn-v0_8-whitegrid
- Font sizes increased:
  - Base: 16pt (from 14pt)
  - Axis labels: 18pt (from 16pt)
  - Titles: 20pt (from 18pt)
  - Tick labels: 16pt (from previous)
  - Legend: 14pt (consistent)
- Grid: 1.2pt lines, 50% alpha, #d0d0d0 color
- Axes: 1.8pt borders, white background
- Figure size: Standard (10, 6)

### 4. X-Axis Standardization

**Consistent Temporal Ranges**:
- Round-based plots (7 total): xlim=[0, 1200] rounds
  - Covers 0-975 rounds of data (81% utilization)
  - network_lifetime, energy, PDR, clustering, overhead, delay evolution
- Delay plot (1 total): xlim=[0, 5000] seconds
  - Covers 0-4667.65s of data (93% utilization)
  - delay_distribution histogram
- Throughput: Auto-scaled based on time data

**Benefits**:
- Visual alignment for cross-plot analysis
- Consistent temporal reference frame
- Professional, extensible appearance

### 5. Confidence Band Removal

**Cleaned Visualization**:
- Removed ±1 Std Dev shaded areas from 8 plots
- delay_distribution.png had no bands (histogram)
- Impact: 45-52% average file size reduction
  - Before: 368-609 KB
  - After: 185-239 KB
- Result: Cleaner, less cluttered visualization

## Final Verification Results

| Metric | Summary | Plot | Status |
|--------|---------|------|--------|
| FND | 551 rounds | 551 rounds | ✅ Fixed |
| LND | 876 rounds | 876 rounds | ✅ Fixed |
| Mean PDR | 0.8382 | 0.8382 | ✅ Fixed |
| Mean Delay | 1153.11s | 1153.11s | ✅ Fixed |
| Median Delay | 777.38s | 777.38s | ✅ Fixed |
| Mean CHs | 7.56 | 7.56 | ✅ Fixed |
| Mean Control Ratio | 0.7393 | 0.7393 | ✅ Fixed |

## Current Plot Status (Final)

All 9 S0-Baseline plots now:
✓ Use DPI 300 for publication quality
✓ Display accurate statistical metrics matching summary
✓ Include professional formatting with enhanced font sizes
✓ Have consistent x-axis ranges (1200 rounds / 5000 seconds)
✓ Show cleaner appearance without confidence band shading
✓ Are optimized for file size (185-239 KB range)
✓ Follow standard plotting conventions
✓ Include proper annotations (FND/LND markers, grid styling)
✓ Have dual-curve visualization (dead nodes added)
✓ Are ready for publication and analysis

## Plots Regenerated

- ✅ network_lifetime.png (207 KB) - with dead nodes curve, correct markers
- ✅ energy_consumption.png (224 KB) - cleaner formatting
- ✅ total_energy_consumption_per_round.png (185 KB) - 45% size reduction
- ✅ pdr.png (234 KB) - correct per-run means
- ✅ throughput.png (238 KB) - cleaner visualization
- ✅ delay_distribution.png (188 KB) - standard formatting
- ✅ average_delay_per_round.png (239 KB) - 52% size reduction
- ✅ clustering_metrics.png (228 KB) - correct statistics
- ✅ control_overhead.png (197 KB) - accurate metrics

## Summary of Improvements

**Statistical**: 5 critical metrics fixed to match summary statistics
**Visual**: Dead nodes curve added for complete lifecycle view
**Formatting**: Professional publication-quality appearance applied
**Consistency**: X-axis ranges standardized across similar plots
**Optimization**: File sizes reduced 45-52% with improved clarity

All improvements verified and completed on February 2, 2026 at 08:49 UTC.

---
*Final Update: February 2, 2026 - All statistical fixes, formatting enhancements, and visualization improvements applied and verified*
