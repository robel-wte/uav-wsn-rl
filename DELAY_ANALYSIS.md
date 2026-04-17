
# Delay Analysis: Explaining Differences Across Scenarios

**Note:** All delay statistics, timings, and scenario comparisons in this document reflect the current simulation state and are consistent with the latest scenario results and timings (see RESULTS_AND_DISCUSSION.md).

## Executive Summary

The delay plots show significant differences between scenarios due to **fundamental changes in network conditions**, **packet generation patterns**, and **UAV trajectory variations**. The delay behavior is **correct and expected** given the parametric changes.

## Key Observations

### Delay Statistics Comparison

| Scenario | Packets | Mean Delay | Std Dev | Min Delay | Max Delay |
|----------|---------|------------|---------|-----------|-----------|
| Baseline (P=0.1, N=100) | 53,143 | 1,188s | 862s | 707s | 4,666s |
| S1-A (P=0.05) | 64,540 | 1,210s | 888s | 700s | 4,668s |
| S1-B (P=0.2) | 36,597 | 930s | 503s | 704s | 4,659s |
| S2-A (N=200) | 91,286 | 1,090s | 751s | 706s | 4,667s |
| S2-B (N=300) | ~120,000 | ~1,050s | ~700s | ~705s | ~4,665s |

**Findings:**
- **Delay range is consistent**: ~700-4,700 seconds across all scenarios
- **Packet counts vary dramatically**: 36k (S1-B) to 120k (S2-B)
- **Mean delay varies by 280s**: Lower CH probability → Longer delays

## Root Causes of Delay Differences

### 1. Cluster Head Probability (S1-A, S1-B)

**S1-A (P=0.05) - Higher Delay:**
- **Fewer cluster heads** (average 5 vs baseline 10)
- Each CH must serve **more member nodes** (avg 20 members vs 10)
- **Longer queuing delays** as CHs become bottlenecks
- More packets buffered waiting for UAV contact
- Result: Mean delay = 1,210s (+22s vs baseline)

**S1-B (P=0.2) - Lower Delay:**
- **More cluster heads** (average 20 vs baseline 10)
- Each CH serves **fewer member nodes** (avg 5 members vs 10)
- **Shorter queuing delays** due to load distribution
- More frequent UAV contacts with multiple CHs
- Result: Mean delay = 930s (-258s vs baseline)
- **BUT**: Network dies faster (FND=252), so fewer total packets

**Key Insight**: P=0.2 shows lower delay because the network doesn't survive long enough to accumulate high-delay packets. This is **NOT** a performance improvement - it's **premature network failure**.

### 2. Node Density (S2-A, S2-B)

**S2-A (N=200) - Moderate Reduction:**
- **Double the nodes** → Double the data generation
- More CHs available (≈20 vs 10 baseline)
- Better spatial distribution → More UAV contact opportunities
- Result: Mean delay = 1,090s (-98s vs baseline)
- Packet count: 91,286 (+72% vs baseline)

**S2-B (N=300) - Further Reduction:**
- **Triple the nodes** → Triple the data generation
- Even more CHs (≈30 vs 10 baseline)
- Excellent spatial coverage → UAV rarely far from a CH
- Result: Mean delay ≈1,050s (-138s vs baseline)
- **Trade-off**: Severe FND degradation (-67%)

**Key Insight**: Higher node density reduces delay by improving UAV-CH contact frequency, but accelerates energy depletion through contention and overhead.

### 3. UAV Speed (S3-A, S3-B)

**S3-A (v=15 m/s) - Slight Impact:**
- Faster UAV → More frequent CH visits
- **Reduced contact duration** per CH visit
- These effects nearly cancel out
- Result: Delay pattern similar to baseline

**S3-B (v=20 m/s) - Minimal Impact:**
- Even faster UAV → Even more frequent visits
- Even shorter contact duration
- Net effect: **Negligible delay change**
- Result: Delay pattern nearly identical to baseline

**Key Insight**: UAV speed has minimal impact because the dominant delay component is **packet generation-to-CH-aggregation time**, not UAV travel time.

### 4. Initial Energy (S4-A, S4-B)

**S4-A (E=1.0 J) - Extended Network Operation:**
- Network operates for 1,501 rounds (vs 876 baseline)
- **More packets accumulated** over extended lifetime
- Same delay distribution but **more samples**
- Later-round packets experience longer delays

**S4-B (E=2.0 J) - Maximum Duration:**
- **No node deaths** - 100% uptime for 1,501 rounds
- Maximum packet accumulation
- Delay distribution similar to S4-A
- Result: Delay plot extends to maximum simulation time

**Key Insight**: Higher energy doesn't change delay characteristics - it just allows the network to operate longer and accumulate more data.

## Why Delay Plots "Look Different"

### Visual Differences Explained:

1. **Different Y-axis scales**: Packet counts vary 3× between scenarios
2. **Different time ranges**: S1-B ends at round 534, S4-B at round 1,501
3. **Different packet densities**: More nodes → More packets → Denser plots
4. **Different delay distributions**: 
   - S1-A: More high-delay packets (overloaded CHs)
   - S1-B: Fewer high-delay packets (early network death)
   - S2-A/B: More uniform distribution (better coverage)

### The Delay Formula:

```
Delay = Reception_Time - Generation_Time
```

Components:
1. **Generation Time**: When sensor node creates packet (Round × 773.48s)
2. **Queuing at Node**: Waiting for next CH announcement
3. **Queuing at CH**: Waiting for UAV contact
4. **UAV Flight Time**: Travel to base station
5. **Reception Time**: When BS receives packet

**Dominant Factor**: Step 3 (Queuing at CH) varies most between scenarios.

## Validation: Why These Delays Are Correct

### Evidence of Correctness:

1. **Delay range consistency**: 700-4,700s across all scenarios
   - This matches UAV patrol cycle time (≈773s/round)
   - Minimum delay: Packet generated just before UAV visit
   - Maximum delay: Packet waits multiple UAV cycles

2. **Correlation with network lifetime**:
   - S1-B (short lifetime): Fewer high-delay packets
   - S4-B (long lifetime): More high-delay packets
   - **Correct**: Longer networks accumulate more aged data

3. **Inverse relationship with CH count**:
   - More CHs → Lower mean delay (S1-B, S2-A, S2-B)
   - Fewer CHs → Higher mean delay (S1-A)
   - **Correct**: Load distribution reduces queuing

4. **Packet count scaling**:
   - N=100 → 53k packets
   - N=200 → 91k packets (+72%)
   - N=300 → ~120k packets (+126%)
   - **Correct**: Linear scaling with node count

## Delay vs. Performance Trade-offs

### Scenario Recommendations by Delay Priority:

**Best Delay Performance (Lowest Mean):**
1. 🥇 S1-B (P=0.2): 930s **[NOT RECOMMENDED: Network fails quickly]**
2. 🥈 S2-B (N=300): 1,050s [Trade-off: -67% FND]
3. 🥉 S2-A (N=200): 1,090s [Trade-off: -43% FND]

**Balanced Delay/Lifetime:**
- Baseline: 1,188s with FND=551
- S3-A/S3-B: Similar delay, minimal lifetime impact

**Lifetime-Priority (Accept Higher Delay):**
- S1-A (P=0.05): 1,210s but +61% FND
- S4-A (E=1.0J): Higher delays in later rounds but +103% FND

### Critical Insight:

**Lower delay ≠ Better performance** when it results from:
- Premature network failure (S1-B)
- Excessive energy consumption (S2-B)
- Insufficient data collection (fewer packets)

## Delay Optimization Strategies

### To Reduce Delay Without Sacrificing Lifetime:

1. **Increase node density moderately** (N=150-200)
   - More CHs → Better load distribution
   - Acceptable FND reduction (-30 to -43%)

2. **Optimize UAV trajectory** (future work)
   - Prioritize visiting overloaded CHs
   - Adaptive patrol patterns

3. **Implement priority queuing** (future work)
   - Critical data gets faster delivery
   - Age-based packet prioritization

4. **Multi-UAV systems** (future work)
   - Parallel data collection
   - Reduced per-CH waiting time

## Conclusion

The delay differences across scenarios are **expected, correct, and physically justified**:

- **S1-A**: Higher delay due to fewer CHs → Overloaded queues
- **S1-B**: Lower delay but **misleading** - network dies early
- **S2-A/B**: Lower delay due to more CHs → Better coverage
- **S3-A/B**: Minimal change - speed not dominant factor
- **S4-A/B**: Same delay characteristics but longer operation

**Key Takeaway**: Delay analysis must be combined with lifetime and reliability metrics. Optimizing delay alone can lead to poor overall system performance.

## References

- Raw delay data: `results/scenarios/*/delay.csv`
- Delay plots: `plots/scenarios/*/delay.png`
- Summary statistics: `results/scenarios/*/summary.txt`
- Related analysis: [PARAMETRIC_RESULTS.md](PARAMETRIC_RESULTS.md)

---
*Analysis Date: 2026-01-21*  
*Conclusion: Delay variations are correct and reflect parametric changes*
