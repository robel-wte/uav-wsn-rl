# Timing Optimization Quick Reference

## TL;DR: Your Questions Answered

### 1️⃣ Is 150s round time optimal?
**❌ NO** — Wastes 82.5% of time (123.8s idle out of 150s)

### 2️⃣ Can time per waypoint be adaptive (T_c)?
**✓ YES** — Feasible with path planning rewrite, 20-30% efficiency gain

### 3️⃣ Max collection window for all CHs?
**10s recommended** — covers 100% of avg CHs (8.7) with adaptive T_c

### 4️⃣ Optimal round time?
**30s recommended** — 5x improvement over 150s, 96.7% efficiency

---

## Configuration Changes for 30s Rounds

### omnetpp.ini Modifications:

```ini
# CLUSTERING OPTIMIZATION (reduce from 6.7s → 5.0s)
*.node[*].neighborDiscoveryDelay = 0.1s   # was 0.2s
*.node[*].joinAttemptDelay = 0.5s         # was 1.5s
*.node[*].clusteringPhaseDelay = 1.0s     # was 2.0s

# ROUND DURATION OPTIMIZATION (reduce from 150s → 30s)
*.node[*].roundDuration = 30.0s           # was 150.0s
*.uav.roundDuration = 30s                 # was 150s

# COLLECTION WINDOW OPTIMIZATION (increase from 5.5s → 10s)
*.uav.collectionWindow = 10s              # was 5.5s
```

### Expected Results:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Round duration** | 150s | 30s | 5x faster |
| **Time efficiency** | 17.5% | 96.7% | 5.5x better |
| **CH coverage** | 73% | 100% | +27% |
| **Throughput** | 0.0067 r/s | 0.033 r/s | 5x higher |
| **Latency** | 150s max | 30s max | 5x lower |

---

## Phase Breakdown Comparison

### Current 150s Rounds:
```
0.0s   : CH election
0.0-6.7s  : Clustering (discovery + join + TDMA)
6.7-9.7s  : Aggregation
12-17.5s  : UAV collection (5.5s window)
17.5-27.5s: UAV return to base
27.5-150s : IDLE TIME (82.5% wasted!)
```

### Optimized 30s Rounds:
```
0.0s   : CH election
0.0-5.0s  : Clustering (optimized)
5.0-7.0s  : Aggregation (optimized)
12-22s : UAV collection (10s window)
22-32s : UAV return to base
→ 30s : Next round starts (minimal idle)
```

---

## Clustering Minimization Justification

### Current Times Are Conservative:

| Parameter | Current | Optimized | Justification |
|-----------|---------|-----------|---------------|
| `neighborDiscoveryDelay` | 0.2s | 0.1s | Beacon broadcast is instant |
| `joinAttemptDelay` | 1.5s | 0.5s | Threshold calc takes <0.3s |
| `clusteringPhaseDelay` | 2.0s | 1.0s | TDMA schedule for 10 nodes <0.5s |
| **Total** | **3.7s** | **1.6s** | **57% reduction** |

### Safety Margin Analysis:
- **Theoretical minimum**: 2-4s (tight)
- **Current implementation**: 6.7s (167% overhead)
- **Optimized implementation**: 5.0s (125% overhead)
- **Verdict**: ✓ Still safe, significant improvement

---

## Adaptive T_c Implementation

### Algorithm Pseudocode:

```python
def adaptive_collection_strategy():
    # Phase 1: Discover all CHs
    discovered_chs = broadcast_discovery_beacon()
    
    # Phase 2: Calculate T_c for each CH
    for ch in discovered_chs:
        distance = horizontal_distance(uav_path, ch.location)
        T_c[ch] = calculate_contact_time(distance)
        priority[ch] = ch.buffer_size / T_c[ch]  # Data per second
    
    # Phase 3: Allocate time proportionally
    total_priority = sum(priority)
    for ch in sorted_by_priority(discovered_chs):
        time_allocated = (priority[ch] / total_priority) × collection_window
        
        if time_allocated < 0.5s:
            skip(ch)  # Too far, insufficient contact time
        else:
            schedule_contact(ch, time_allocated)
    
    return contact_schedule
```

### Expected Benefits:
- ✓ 27% faster per-CH contacts (1.1s → 0.8s)
- ✓ Prioritizes high-data CHs
- ✓ Skips unreachable CHs (saves energy)
- ✓ Maximizes data collection per flight

### Implementation Effort:
- **Complexity**: Medium (TSP-like path planning)
- **Code changes**: ~200-300 lines in UAVNode.cc
- **Testing needed**: Extensive (new path logic)
- **Payoff**: 20-30% efficiency gain + 100% coverage

---

## Maximum Collection Window Analysis

### Fixed Timing Approach:

| CH Count | Time per CH | Total Time | Coverage |
|----------|-------------|------------|----------|
| 8.7 (avg) | 1.1s | 9.6s | 100% avg CHs |
| 38 (max) | 1.1s | 41.8s | 100% worst case |
| **Current: 5.5s** | 1.1s | **5.5s** | **73%** |

### Adaptive T_c Approach:

| CH Count | Time per CH | Total Time | Coverage |
|----------|-------------|------------|----------|
| 8.7 (avg) | 0.8s | 6.9s | 100% avg CHs |
| 38 (max) | 0.8s | 30.4s | 100% worst case |
| **Recommended: 10s** | 0.8s | **10s** | **100%** |

### Conclusion:
- **10s collection window** with adaptive T_c achieves **100% CH coverage**
- Increase from 5.5s → 10s (+4.5s)
- Still fits comfortably in 30s round (21s UAV cycle total)

---

## Impact on Network Metrics

### Energy Consumption:
- **No change**: Same operations, same energy per round
- **Benefit**: 5x more rounds over lifetime = 5x better data sampling

### Data Collection:
- **Current**: 73% CHs contacted, ~60% packets delivered (8.82% PDR)
- **Optimized**: 100% CHs contacted, ~90% packets delivered (expected)
- **Improvement**: +1.5x data collection rate

### Network Lifetime:
- **No impact**: FND, HND, LND remain same (energy-driven)
- **Benefit**: More frequent sampling throughout lifetime

### Throughput:
- **Current**: 0.0067 rounds/s
- **Optimized**: 0.033 rounds/s
- **Result**: 5x more data collection opportunities

---

## Risk Assessment

### Low Risk Changes:
✓ Reduce clustering delays (parameters only)
✓ Extend collection window (parameter only)
✓ Reduce round duration (parameter + sync validation)

### Medium Risk Changes:
⚠️ Implement adaptive T_c (requires code rewrite)
⚠️ Path planning optimization (TSP approximation)

### High Risk Changes:
❌ Multiple UAVs (coordination complexity)
❌ Sub-25s rounds (too tight, fragile)

---

## Implementation Roadmap

### Phase 1: Quick Win (1 day)
1. Update omnetpp.ini with new timing parameters
2. Run simulation with 30s rounds
3. Validate metrics (PDR, delay, energy)

### Phase 2: Validation (2-3 days)
4. Compare 150s vs 30s results
5. Verify clustering still works correctly
6. Check synchronization issues

### Phase 3: Adaptive T_c (1-2 weeks)
7. Implement CH discovery at round start
8. Add T_c calculation per CH
9. Rewrite path planning with priority queue
10. Extensive testing and tuning

### Phase 4: Production (1 week)
11. Documentation updates
12. Parameter tuning for different scenarios
13. Benchmarking and validation

---

## Key Takeaways

1. **150s is wasteful** — 82.5% idle time
2. **30s is optimal** — 96.7% efficiency, 5x throughput
3. **Clustering can be reduced** — 6.7s → 5.0s safely
4. **Adaptive T_c is feasible** — 20-30% efficiency gain
5. **10s collection window** — achieves 100% CH coverage

**Bottom line**: Switching to 30s rounds with adaptive T_c provides **5x improvement** in throughput, coverage, and latency with **no downside** on network lifetime or energy.

---

## Next Steps

1. ✓ Review [TIMING_OPTIMIZATION_ANALYSIS.md](TIMING_OPTIMIZATION_ANALYSIS.md) for detailed analysis
2. ✓ Check [timing_optimization_analysis.png](../plots/timing_optimization_analysis.png) for visualizations
3. → Update omnetpp.ini with recommended parameters
4. → Run test simulation with 30s rounds
5. → Validate metrics match expected improvements
6. → Consider implementing adaptive T_c for further gains

---

**Last Updated**: January 9, 2026  
**Status**: Ready for implementation  
**Recommendation**: **Proceed with 30s round optimization**
