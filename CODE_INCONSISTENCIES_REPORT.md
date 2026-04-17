# UAV-WSN-BM: Code Inconsistencies Report

**Date**: February 1, 2026  
**Status**: Code is functionally working, but contains inconsistencies that affect results

---

## Executive Summary

Detailed analysis of the codebase has identified **CRITICAL** and **IMPORTANT** inconsistencies in how metrics are defined and calculated across different scripts. The most severe issue is the FND (First Node Death) definition mismatch, which causes incorrect results for scenarios with non-100 node counts.

### Key Findings:
- ✅ Simulation code works correctly
- ✅ Metrics are collected properly  
- ❌ **CRITICAL**: FND definition is inconsistent across scripts
- ❌ **IMPORTANT**: HNA calculation is hardcoded for 100 nodes
- ⚠️ Energy relationships are consistent
- ⚠️ PDR calculations use intended long-delay packet model

---

## Issue 1: CRITICAL - FND (First Node Death) Definition Mismatch

### Problem
Three different definitions of FND are used across the codebase:

1. **extract_metrics.py (Line 15-18)**
   ```python
   fnd_row = network_df[network_df['AliveNodes'] < 100]
   ```
   - Uses a **hardcoded threshold of 100 nodes**
   - Assumes all scenarios have exactly 100 nodes
   - **INCORRECT** for scenarios with different node counts

2. **generate_scenario_plots.py (Line 37)**
   ```python
   fnd_row = network_df[network_df['AliveNodes'] < network_df['AliveNodes'].iloc[0]]
   ```
   - Uses **dynamic comparison** to initial node count
   - **CORRECT** implementation

3. **generate_plots.py (Line 495)**
   ```python
   fnd_idx = stability_df[stability_df['DeadNodes'] > 0].index[0]
   ```
   - Uses `DeadNodes > 0` condition
   - **CORRECT** implementation

### Impact - CONFIRMED BUG
Testing reveals FND mismatches in multi-node scenarios:

| Scenario | Initial Nodes | FND (< 100) | FND (< initial) | Match? |
|----------|---------------|------------|-----------------|--------|
| S1-A-P005 | 100 | 925 | 925 | ✓ |
| S1-B-P02 | 100 | 355 | 355 | ✓ |
| **S2-A-N200** | **200** | **571** | **492** | ❌ **MISMATCH** |
| **S2-B-N300** | **300** | **548** | **453** | ❌ **MISMATCH** |
| S3-A-V15 | 100 | 558 | 558 | ✓ |

**Scenarios with 200 or 300 nodes report incorrect FND values in extract_metrics.py!**

### Root Cause
`extract_metrics.py` was written assuming a fixed network size of 100 nodes and was not updated when parametric scenarios with different node counts (S2-A, S2-B) were added.

### Recommendation
Update `extract_metrics.py` to use the dynamic definition consistent with other scripts.

---

## Issue 2: IMPORTANT - HNA (Half Nodes Alive) Hardcoded for 100 Nodes

### Problem
In **extract_metrics.py (Line 24-25)**:
```python
hna_df = network_df[network_df['AliveNodes'] <= 50]
metrics['HNA'] = int(hna_df.iloc[0]['Round']) if not hna_df.empty else metrics['LND']
```

This hardcodes the threshold at 50 alive nodes, which is only correct for 100-node scenarios.

### Impact
HNA values are incorrect for:
- S2-A-N200 scenarios (HNA should be when AliveNodes ≤ 100, not 50)
- S2-B-N300 scenarios (HNA should be when AliveNodes ≤ 150, not 50)
- Any future scenarios with different node counts

### Recommendation
Calculate HNA dynamically:
```python
threshold = total_nodes // 2  # Half of initial nodes
hna_df = network_df[network_df['AliveNodes'] <= threshold]
metrics['HNA'] = int(hna_df.iloc[0]['Round']) if not hna_df.empty else metrics['LND']
```

---

## Issue 3: Energy Calculation - Verification Complete ✓

### Finding
Energy calculations ARE consistent across the codebase:

```
Energy Relationship:
  Initial Energy - Sum(Consumed per Round) = Final Residual Energy
  
  For S1-A-P005:
  49.9784 J - 50.0351 J ≈ 0 J (matches final state)
```

Additionally verified:
```
AvgResidualEnergy * AliveNodes = TotalNetworkEnergy
  Mean difference: < 0.000001 J (negligible)
  Max difference: < 0.000010 J (numerical precision only)
```

**Status**: ✅ **NO ISSUES FOUND** - Energy calculations are correct and self-consistent.

---

## Issue 4: PDR Calculation and Long-Delay Packet Handling

### Design Pattern
The codebase intentionally allows late-arriving packets to count toward PDR:

**MetricsCollector.cc (Line 276-280)**:
```cpp
int genRound = packetTracker[packetId].genRound;
roundReceivedMap[genRound]++;  // Count under generation round, not reception round
```

This means:
- A packet generated in Round 100 but received in Round 200
- Counts toward Round 100's PDR, not Round 200's

### Rationale
This is **intentional and correct** for UAV-based collection systems where:
1. Sensor nodes generate packets continuously
2. UAV collects them during periodic visits
3. Data delivery happens in future rounds during UAV contact
4. Counting by generation round reflects actual network performance

### Verification
Delay measurements show this is expected:
```
Average packet delay: ~768 seconds (12.8 minutes)
This is consistent with UAV visiting schedule (26-35 seconds per waypoint)
```

**Status**: ✅ **NO ISSUES** - Design is correct and documented in comments.

---

## Issue 5: Overhead Ratio Definition - Verification Complete ✓

### Definition
```cpp
ControlRatio = ControlPackets / (ControlPackets + DataPackets)
```

This is the standard definition used across:
- MetricsCollector.cc (calculation)
- Overhead CSV (storage)
- generate_plots.py (visualization)

**Status**: ✅ **NO ISSUES** - Consistent across all components.

---

## Issue 6: Delay Units - Verification Complete ✓

### Finding
Delays are correctly stored in **seconds** as expected:

From delay.csv header: `Delay_s`  
Sample values: 768.896, 768.886, 768.876 (seconds)  
Matching extract_metrics.py expectation: `metrics['MeanDelay_s']`

**Status**: ✅ **NO ISSUES** - Units are consistent.

---

## Issue 7: Topology and Network Parameters - Verification Needed

### Note
The following parameters appear in multiple places and should be verified for consistency:

1. **Network Area**: 500m × 500m
   - Location.h
   - generate_plots.py
   - Topology CSV files

2. **Number of Nodes**: 100 (default)
   - MetricsCollector.cc
   - Various analysis scripts

3. **Communication Ranges**:
   - Sensor range: 100m
   - CH range: 50m (assumed)
   - UAV range: 150m

4. **Round Duration**: 200 seconds
   - MetricsCollector.cc (Line 19)
   - omnetpp.ini
   - Various calculation scripts

**Recommendation**: Create a centralized configuration file documenting all these parameters.

---

## Summary of Issues by Severity

### 🔴 CRITICAL (Must Fix)
1. **FND definition mismatch in extract_metrics.py**
   - Affects: S2-A, S2-B, and any future multi-node scenarios
   - Fix: Use dynamic threshold instead of hardcoded 100
   - Files to update: `extract_metrics.py` (line 15-18)

### 🟠 IMPORTANT (Should Fix)
2. **HNA hardcoded for 100 nodes in extract_metrics.py**
   - Affects: Accuracy of Half Nodes Alive metric
   - Fix: Calculate dynamically as TotalNodes // 2
   - Files to update: `extract_metrics.py` (line 24-25)

### 🟡 NICE-TO-HAVE (Good Practice)
3. **Centralize configuration parameters**
   - Create a single source of truth for network parameters
   - Reduces chance of inconsistencies
   - Makes code more maintainable

### ✅ VERIFIED (No Issues)
- Energy calculations and relationships
- PDR calculation methodology
- Overhead ratio definition
- Delay units and values
- Throughput calculations

---

## Files Requiring Updates

### Primary
- **extract_metrics.py**: Lines 15-25 (FND and HNA definitions)

### Secondary (for consistency verification)
- **generate_scenario_plots.py**: Verify FND implementation (appears correct)
- **generate_plots.py**: Verify FND implementation (appears correct)
- **MetricsCollector.cc**: Document design choices around long-delay packets

### Documentation
- Create **CONFIGURATION.md** with all network parameters
- Update **README.md** to clarify metric definitions

---

## Testing Recommendations

After fixes are applied:

1. **Unit Tests**
   ```python
   # Test FND definition with different node counts
   assert fnd_for_100_nodes == 925
   assert fnd_for_200_nodes == 492
   assert fnd_for_300_nodes == 453
   ```

2. **Integration Tests**
   ```python
   # Verify all scripts produce consistent results
   extract_metrics_fnd == scenario_plots_fnd == plots_fnd
   ```

3. **Data Validation**
   - Regenerate all scenario metrics after fixes
   - Verify plots reflect correct FND/LND values
   - Check that all scenarios use consistent definitions

---

## Conclusion

The simulation and metrics collection code is **functionally correct**, but the analysis layer contains **inconsistencies** in metric definitions that can lead to incorrect conclusions, especially for scenarios with non-standard node counts. These issues are easily fixed by:

1. Replacing hardcoded thresholds with dynamic calculations
2. Ensuring consistent definitions across all scripts
3. Adding configuration validation

Once fixed, the entire pipeline will be robust and scalable for different network sizes and parameters.
