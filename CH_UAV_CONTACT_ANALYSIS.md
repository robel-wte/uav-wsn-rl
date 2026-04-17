# CH-UAV Contact & Data Transfer Process Analysis

## Overview
There are significant differences between **T_c (actual contact time)** and **T_req (required data transfer time)** because they measure fundamentally different things in the system architecture.

---

## 1. T_c: Geometric Contact Time Window

### Definition
T_c is the **duration of geometric communication window** - how long the UAV is within communication range of a stationary ground node during a flyby.

### Calculation
From [UAVNode.cc](UAVNode.cc#L825-L842):
```
T_c = 2 * sqrt(rmax^2 - b^2) / v

where:
  rmax = sqrt(commRadius^2 - uavHeight^2)
       = sqrt(192^2 - 30^2)
       = sqrt(36864 - 900)
       ≈ 189.6 m
  
  b = horizontal distance from UAV to CH (perpendicular offset)
  v = searchSpeed = 10 m/s
```

### Example Calculations
- **CH directly below waypoint** (b ≈ 0):
  - T_c = 2 × sqrt(189.6² - 0²) / 10 = 2 × 189.6 / 10 = **37.9 seconds**

- **CH 100m from waypoint** (b = 100):
  - T_c = 2 × sqrt(189.6² - 100²) / 10 = 2 × sqrt(25961.6) / 10 = **32.1 seconds**

- **CH 180m from waypoint** (b = 180):
  - T_c = 2 × sqrt(189.6² - 180²) / 10 = 2 × sqrt(5220.16) / 10 = **14.4 seconds**

### Key Insight
T_c **only depends on geometry** (CH location relative to UAV waypoint), NOT on data volume.

---

## 2. T_req: Analytical Data Transfer Time

### Definition
T_req is the **minimum time required to transfer all aggregated packets** using a practical wireless data rate.

### Calculation
```
T_req = (expected_members × packet_size) / dataRate
      = (expected_members × 2000 bits) / 100000 bps
      = expected_members × 0.02 seconds
```

### Example Calculations
- **CH with 1 member**: T_req = 1 × 0.02 = **0.02 seconds**
- **CH with 5 members**: T_req = 5 × 0.02 = **0.1 seconds**
- **CH with 10 members**: T_req = 10 × 0.02 = **0.2 seconds**
- **CH with 15 members**: T_req = 15 × 0.02 = **0.3 seconds**

### Key Insight
T_req **only depends on data volume** (number of aggregated packets), NOT on geometry.

---

## 3. The Contact & Data Transfer Process

### Communication Flow (from [UAVNode.cc](UAVNode.cc#L504-L586) and [SensorNode.cc](SensorNode.cc#L899-L936))

#### Phase 1: Contact Initiation (t = t_contact)
```
UAV sends: UAV_COLLECT message
           └─→ Direct message to CH (instant delivery)
           
CH receives: UAV_COLLECT
           └─→ Immediately responds with AGGREGATED_DATA message
           └─→ Data transfer is instantaneous (direct messaging)
```

#### Phase 2: Hovering (t = t_contact to t_contact + T_c)
```
UAV schedules contactTimer for simTime() + T_c
  ├─ T_c is the full geometric contact window
  ├─ Data already sent (instantaneous)
  ├─ UAV hovers for remaining time
  └─ Represents realistic hovering overhead
```

#### Phase 3: Contact End (t = t_contact + T_c)
```
contactTimer fires → contactAllCHsInRange()
  ├─ Move to next unvisited CH within range
  └─ Or fly to next waypoint if none nearby
```

### Key Observation
- **Actual data transfer in simulation:** ~0 seconds (direct messaging)
- **Recorded contact duration:** T_c seconds (hovering overhead)
- **The difference:** Hovering time while awaiting next waypoint activities

---

## 4. Why T_c >> T_req (The Big Differences)

### Primary Cause: Different Metrics
1. **T_c** = Geometric flyby duration (geometry-based)
2. **T_req** = Data transfer time (data-volume-based)

### Quantitative Analysis

#### Scenario from Round 4:
| Metric | Value | Ratio to T_req |
|--------|-------|————————|
| **Typical T_c** | 15-30 seconds | ~50-150x T_req |
| **Typical T_req** | 0.1-0.3 seconds | 1x |
| **handshakeDelay** | 0.05 seconds | 0.5x T_req |

#### Root Causes

**1. Low Practical Data Rate (100 kbps bottleneck)**
   - IEEE 802.15.4 max: 250 kbps
   - Practical throughput: ~100 kbps (MAC overhead, collisions, retransmissions)
   - Result: Even small amounts of data take measurable time
   - Each member packet (2000 bits): 0.02 seconds

**2. Geometric Contact Window is Long**
   - UAV altitude: 30m (fixed)
   - Comm radius: 192m (horizontal projection)
   - Search speed: 10 m/s (constant)
   - Result: Passing by any CH takes 15-40 seconds
   - Even with fast flyby, geometry dominates

**3. Clustered Aggregation Means Few Packets**
   - Expected members per CH: 3-10 (typical)
   - Data per member: 2000 bits = 1 packet
   - Total per CH: 6000-20000 bits = 3-10 packets
   - Time to transfer at 100 kbps: 0.06-0.2 seconds
   - T_c is **100-600x longer** than data transfer

**4. Hovering is Necessary for Waypoint Sequencing**
   - UAV uses pure Random Waypoint Model
   - Each contact duration T_c represents realistic hovering
   - UAV cannot move to next location until contact ends
   - This is not "wasted" time but necessary synchronization overhead

---

## 5. System Implications

### What T_c >> T_req Reveals

**1. Communication is NOT the bottleneck**
   - Data transfer time is negligible  relative to hovering time
   - Even with 100 kbps, data moves fast

**2. Mobility (waypoint transitions) dominates contact**
   - Time budget dominated by geometric constraints
   - Not by data volume constraints

**3. UAV hovering strategy could be optimized**
   - Current: Hover full T_c duration
   - Alternative: Hover(T_req + handshakeDelay) + move to next waypoint early
   - Could improve round-trip time and visit more CHs per round

**4. Contact failures are NOT due to transfer time**
   - From [UAVNode.cc line 539](UAVNode.cc#L539-L543), checks `if (transferTime > T_c)`
   - With T_req << T_c, failures only occur if:
     - CH is out of range (T_c = 0)
     - Channel quality fails (SNR-based)
     - Node has no energy
   - Data volume is NOT a limiting factor (in current design)

---

## 6. Detailed Contact Scheduling

From [UAVNode.cc line 586](UAVNode.cc#L586):
```cpp
// Hover for T_c duration (actual contact window, not just transfer time)
scheduleAt(simTime() + T_c, contactTimer);
```

**This schedules a fixed T_c duration, regardless of actual transfer time.**

**Consequence:**
- CH with T_req = 0.1s, T_c = 30s → Hover 30s
- CH with T_req = 0.2s, T_c = 20s → Hover 20s  
- CH with T_req = 0.05s, T_c = 35s → Hover 35s

**Result:** Idle hovering time = T_c - T_req - handshakeDelay

---

## 7. Recommended Improvements

### Option 1: Adaptive Hovering Duration
```
HOVER_DURATION = max(T_req + handshakeDelay + safety_margin, MIN_HOVER)
```
- **Benefit:** Could visit more CHs per round
- **Trade-off:** Requires CH discovery timing adjustments

### Option 2: Increase Data Rate (Realistic Channel Model)
```
Current: 100 kbps (IEEE 802.15.4 practical)
Option:  Consider if actual hardware supports higher rates
         (unlikely for long-range WSN)
```

### Option 3: Decrease Hovering Waypoint Duration
```
Current: UAV waits full T_c at each waypoint
Improve: Multiple smaller waypoints with shorter T_c
```

---

## Summary Table

| Aspect | T_c | T_req |
|--------|-----|-------|
| **Governs** | UAV hovering duration | Data transfer minimum |
| **Depends on** | Geometry (UAV position, CH location) | Data volume (aggregated packets) |
| **Typical value** | 10-40 seconds | 0.05-0.3 seconds |
| **Constraint** | Communication range + flight speed | Datarate + packet count |
| **Scheduled as** | Full duration (hovering overlay) | Compared against T_c (validation only) |
| **Bottleneck?** | **DOMINANT** (mobile system constraint) | **NOT** (communication is fast enough) |

---

## Conclusion

The large **T_c >> T_req** differences are **expected and correct** because:

1. **T_c is a mobility property** (how long UAV is in range)
2. **T_req is a communications property** (how long to transfer data)
3. **The system is mobility-constrained**, not data-rate-constrained
4. **Hovering overhead is realistic** for UAV-based data collection

The UAV's ability to visit CHs is limited by how fast it can fly between waypoints, not by how fast it can transfer data.
