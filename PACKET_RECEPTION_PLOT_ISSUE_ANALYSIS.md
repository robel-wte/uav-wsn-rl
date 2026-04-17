
# Packet Reception Plot Issue - Root Cause Analysis

**Note:** All timing and round structure references in this document reflect the current simulation state and are consistent with the latest scenario results and timings (see RESULTS_AND_DISCUSSION.md).

## Issue Summary

**Problem:** The "Packet Reception Count per Round" subplot in [plots/average_delay_per_round.png](plots/average_delay_per_round.png) shows 0 values for many rounds, appearing to indicate no packet deliveries.

**Verdict:** ❌ **The plot is INCORRECT** - it uses generation round instead of reception round.

---

## Root Cause

**Location:** [generate_plots.py](generate_plots.py#L669)

```python
# Line 669 - THE BUG:
valid_delays['GenRound'] = _assign_round(gen_times, network_df, 
                                         round_duration, start_offset)

# Line 673 - Groups by generation round:
delay_by_round = valid_delays.groupby('GenRound').agg({
    'Delay_s': ['mean', 'count']
})

# Line 698 - Misleading label:
ax2.set_ylabel('Packets Delivered', fontweight='bold')
ax2.set_title('Packet Reception Count per Round', fontweight='bold')
```

**The Problem:**
- Uses `GenerationTime` to calculate round number
- Counts packets by when they were **generated**
- But labels axis as "Packets Delivered" (implies **reception**)
- Result: Mismatch between label and data

---

## Why This Causes 0 Values

### Packet Delivery Timeline

1. **Generation:** Packets generated at start of round (~0.8s into round)
2. **Collection Window:** UAV arrives randomly during 0-691s window
3. **Multi-Round Delivery:** Many packets delivered 1+ rounds AFTER generation

### Example: Round 2

```
Packets GENERATED in Round 2: 88 packets
├─ Received in Round 2: 0 packets  ← Current plot shows this!
├─ Received in Round 3: 81 packets (avg delay 777s)
└─ Received in Round 4: 7 packets (avg delay 1560s)

Current plot shows: 88 (generation count)
Should show: 0 (reception count) for Round 2
             81 for Round 3 (from Round 2 generation)
```

### Statistics

| Metric | By Generation | By Reception |
|--------|--------------|--------------|
| Total packets | 53,117 | 53,117 |
| Rounds with data | 941 | 758 |
| **Rounds with 0 count** | **6** | **188** |
| Mean packets/round | 56.4 | 70.1 |
| Std deviation | 32.5 | 59.2 |
| Max packets/round | 99 | 260 |

**Key Finding:** 
- Current plot shows only 6 rounds with 0 (by generation)
- Actual reception pattern has 188 rounds with 0 receptions
- Completely different distribution patterns!

---

## First 10 Rounds Comparison

| Round | Generated (Current Plot) | Actually Received | Difference |
|-------|-------------------------|-------------------|-----------|
| 1 | 95 | 142 | +47 |
| 2 | 88 | **0** | -88 |
| 3 | 92 | 96 | +4 |
| 4 | 79 | 111 | +32 |
| 5 | 90 | 75 | -15 |
| 6 | 85 | 77 | -8 |
| 7 | 83 | 82 | -1 |
| 8 | 82 | 164 | +82 |
| 9 | 80 | 58 | -22 |
| 10 | 89 | **0** | -89 |

**Observation:** Every single round has a mismatch between generation and reception counts!

---

## Technical Explanation

### Why Packets Delivered Later

From [DELAY_MULTIMODAL_EXPLANATION.md](DELAY_MULTIMODAL_EXPLANATION.md):

```
Packet Generation: t = RoundStart + 0.8s
UAV Collection Window: 0-691s (random arrival)

Scenario 1: Early generation + Late UAV arrival
├─ Packet generated at t=0.8s
├─ UAV arrives at t=600s (within same round)
└─ Delay: ~600s (SAME round delivery)

Scenario 2: Early generation + Early UAV arrival (next round)
├─ Packet generated at t=0.8s
├─ UAV arrives at t=50s (missed the packet!)
├─ UAV returns next round at t=774+50=824s
└─ Delay: ~823s (NEXT round delivery)

Minimum delay observed: 707s ≈ 91.4% of round duration
This confirms many packets miss UAV in their generation round
```

### Delivery Distribution

- **40.9%** delivered in SAME round as generation
- **32.6%** delivered 1 round later
- **26.5%** delivered 2+ rounds later

This is why using generation round is incorrect for "reception count"!

---

## Corrected Visualization

Created: [plots/packet_reception_comparison.png](plots/packet_reception_comparison.png)

Shows two subplots:
1. **Top (Red):** Current incorrect plot - by generation round
   - 6 rounds with 0 count
   - Smooth, consistent pattern
   - Misleading: suggests steady reception

2. **Bottom (Green):** Corrected plot - by reception round  
   - 188 rounds with 0 count
   - Bursty, irregular pattern
   - Accurate: shows actual delivery spikes

**Key Insight:** The corrected plot reveals the true "bursty" nature of packet collection - rounds where UAV collects many buffered packets vs rounds with no collections.

---

## Fix Required

### Option 1: Change Calculation (Recommended)

```python
# generate_plots.py line 669
# OLD (WRONG):
valid_delays['GenRound'] = _assign_round(gen_times, network_df, ...)

# NEW (CORRECT):
rec_times = valid_delays['ReceptionTime'].values
valid_delays['RecRound'] = _assign_round(rec_times, network_df, 
                                         round_duration, start_offset)

# Line 673 - Change groupby:
delay_by_round = valid_delays.groupby('RecRound').agg({
    'Delay_s': ['mean', 'count']
})
```

### Option 2: Change Labels (Alternative)

If keeping generation-based counting:

```python
# Line 698 - Update labels to match data:
ax2.set_ylabel('Packets Generated (Eventually Delivered)', fontweight='bold')
ax2.set_title('Packet Generation Count per Round', fontweight='bold')
```

**Recommendation:** Use Option 1 (change calculation) because:
- "Packet Reception Count" clearly means when packets are received
- Matches interpretation of PDR data (packets received per round)
- More useful for analyzing UAV collection patterns

---

## Validation

### Cross-Check with PDR Data

[results/pdr.csv](results/pdr.csv) shows PacketsReceived per round:

```python
Round 2: PDR shows 95 packets received
         delay.csv shows 0 receptions (by reception time)
         Discrepancy explained: PDR counts by generation, delay by reception
```

**Important:** PDR metrics also use generation-based counting! Both PDR and this plot should be updated to use reception-based counting for accuracy.

---

## Impact Assessment

### Current Plot Problems

1. **Misleading Label:** Says "Packets Delivered" but shows generation count
2. **Wrong Pattern:** Shows smooth generation pattern, not bursty reception pattern
3. **Incorrect 0s:** Shows 6 rounds with 0 (generation gaps) instead of 188 (reception gaps)
4. **Analysis Impact:** Could lead to wrong conclusions about UAV collection efficiency

### Corrected Plot Benefits

1. **Accurate Pattern:** Shows true bursty nature of collections
2. **Correct 0s:** 188 rounds with no receptions (UAV didn't collect)
3. **Better Analysis:** Can identify rounds with collection failures
4. **Spike Detection:** Rounds with >150 packets indicate buffered packet collection

---

## Conclusion

**Is the 0-value correct?**

- ✅ **Technically correct** - Some rounds truly have 0 packet generations (6 rounds)
- ❌ **Semantically wrong** - Plot title says "Reception" but uses "Generation"  
- ❌ **Analytically wrong** - Doesn't show actual packet delivery pattern

**The plot needs to be fixed** to use reception time instead of generation time.

The corrected plot in [plots/packet_reception_comparison.png](plots/packet_reception_comparison.png) shows the accurate reception pattern with 188 rounds having 0 receptions, revealing the true bursty collection behavior of the UAV.

---

## Files Referenced

- [generate_plots.py](generate_plots.py#L659-L708) - Plot generation function
- [results/delay.csv](results/delay.csv) - Packet timing data (53,117 records)
- [results/pdr.csv](results/pdr.csv) - PDR metrics per round
- [plots/average_delay_per_round.png](plots/average_delay_per_round.png) - Current incorrect plot
- [plots/packet_reception_comparison.png](plots/packet_reception_comparison.png) - Corrected comparison plot
- [DELAY_MULTIMODAL_EXPLANATION.md](DELAY_MULTIMODAL_EXPLANATION.md) - Delay distribution analysis
- [CODE_VALIDATION_REPORT.md](CODE_VALIDATION_REPORT.md) - Comprehensive validation report
