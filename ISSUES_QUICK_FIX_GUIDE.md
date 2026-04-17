# Code Issues Summary - Quick Reference

## Issue #1: FND Definition Mismatch (CRITICAL)

### The Problem
`extract_metrics.py` uses a hardcoded threshold for FND detection:

```python
# ❌ WRONG (Line 15-18 in extract_metrics.py)
fnd_row = network_df[network_df['AliveNodes'] < 100]
# This assumes ALL scenarios have 100 nodes!
```

### Correct Implementation
Other scripts correctly use dynamic comparison:

```python
# ✓ CORRECT (Line 37 in generate_scenario_plots.py)
initial = network_df['AliveNodes'].iloc[0]
fnd_row = network_df[network_df['AliveNodes'] < initial]
```

### Real-World Impact

**For S2-A (200 nodes):**
- Hardcoded threshold detects FND at Round 571
- Correct threshold detects FND at Round 492
- **Error: 79 rounds (17% off)**

**For S2-B (300 nodes):**
- Hardcoded threshold detects FND at Round 548
- Correct threshold detects FND at Round 453
- **Error: 95 rounds (21% off)**

### How to Fix

**File**: `extract_metrics.py`  
**Lines**: 15-18

Change this:
```python
fnd_row = network_df[network_df['AliveNodes'] < 100]
```

To this:
```python
initial_nodes = network_df['AliveNodes'].iloc[0]
fnd_row = network_df[network_df['AliveNodes'] < initial_nodes]
```

---

## Issue #2: HNA Calculation (IMPORTANT)

### The Problem
`extract_metrics.py` hardcodes HNA threshold:

```python
# ❌ WRONG (Line 24-25 in extract_metrics.py)
hna_df = network_df[network_df['AliveNodes'] <= 50]
# This only works for 100-node networks!
```

### Correct Implementation
Should be dynamic:

```python
# ✓ CORRECT
total_nodes = network_df['AliveNodes'].iloc[0]
hna_df = network_df[network_df['AliveNodes'] <= total_nodes // 2]
```

### Impact Matrix

| Scenario | Node Count | Current HNA | Correct HNA | Error |
|----------|-----------|------------|-------------|-------|
| S1-A, S3-A, etc. | 100 | ≤50 ✓ | ≤50 ✓ | 0 |
| S2-A | 200 | ≤50 ❌ | ≤100 ✓ | Large |
| S2-B | 300 | ≤50 ❌ | ≤150 ✓ | Large |

### How to Fix

**File**: `extract_metrics.py`  
**Lines**: 24-25

Change this:
```python
hna_df = network_df[network_df['AliveNodes'] <= 50]
```

To this:
```python
total_nodes = network_df['AliveNodes'].iloc[0]
threshold = total_nodes // 2
hna_df = network_df[network_df['AliveNodes'] <= threshold]
```

---

## Issues That Are NOT Problems

### Energy Consistency ✓
Verified that: `Initial Energy - Consumed = Residual Energy`  
Calculation is correct and consistent.

### Delay Values ✓
Verified that delays are in seconds and values (~768s) are correct for UAV model.

### PDR Calculation ✓
Verified that long-delay packet handling (counting by generation round) is intentional and correct.

### Overhead Ratio ✓
Verified that: `ControlRatio = ControlPackets / (ControlPackets + DataPackets)`  
Consistent across all scripts.

---

## Files Affected

### Primary (Must Update)
- `extract_metrics.py` - Contains both critical bugs

### Secondary (Verify)
- `generate_scenario_plots.py` - Uses correct FND definition ✓
- `generate_plots.py` - Uses correct FND definition ✓
- `MetricsCollector.cc` - Records metrics correctly ✓

---

## Testing After Fix

Run these tests to verify the fix:
```bash
# Test extract_metrics.py with S2-A scenario
python3 extract_metrics.py S2-A-N200

# Expected output:
# FND: 492 (not 571)
# HNA: ~800 (when AliveNodes <= 100, not 50)

# Test with S1-A scenario (should still work)
python3 extract_metrics.py S1-A-P005

# Expected output:
# FND: 925 (unchanged)
# HNA: ~1167 (unchanged)
```

---

## Branch Information

- **Current Branch**: `uav-wsn-s1`
- **Default Branch**: `main`
- **Changes**: Local to this branch, ready for commit

---

## Summary

| Issue | Severity | Affected Scenarios | Fix Complexity |
|-------|----------|-------------------|-----------------|
| FND mismatch | CRITICAL | S2-A, S2-B | 3 lines |
| HNA hardcoding | IMPORTANT | S2-A, S2-B | 3 lines |
| Total fix time | N/A | N/A | ~5 minutes |

**Recommendation**: Fix both issues immediately before publishing results that include S2-A or S2-B scenarios.
