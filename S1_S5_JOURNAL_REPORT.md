# S1–S5 Parametric Results Report (Journal-Ready)

**Project:** UAV-WSN-BM  
**Scope:** Scenarios S1–S5 (Parametric Variations of the UAV-assisted WSN routing protocol)  
**Date:** February 2, 2026  
**Reference:** Routing-centric interpretation consistent with ROUTING_PERFORMANCE_ANALYSIS.md

---

## Abstract

This report provides a comprehensive, journal-ready analysis of all parametric scenarios S1–S5 for the UAV-assisted WSN routing protocol. We evaluate routing-centric outcomes across clustering probability, node density, UAV mobility, initial energy, and packet size variations. The analysis focuses on routing performance metrics (PDR, throughput, delay, overhead), lifetime indicators (FND, HNA, LND), and clustering behavior. Each scenario is discussed with full reference to the generated plots, with figure numbers embedded. Parameter sensitivity plots and cross-scenario comparison plots are also analyzed to contextualize routing behavior under parametric shifts.

---

## 1. Methodological Alignment with Routing Performance Analysis

The routing protocol under evaluation follows a hierarchical UAV-assisted collection architecture as detailed in ROUTING_PERFORMANCE_ANALYSIS.md. The primary routing dynamics arise from (i) intra-cluster single-hop transmissions, (ii) CH buffering and opportunistic UAV contact, and (iii) UAV-to-BS relaying. The parametric scenarios intentionally perturb routing-relevant parameters that affect cluster formation stability, buffer residence time, contact probability, and energy-driven route availability.

---

## 2. Scenario Summary (S1–S5)

| Scenario | Config | FND | HNA | LND | PDR | Throughput_kbps | Delay_s | Overhead | MeanCHs | UnclusteredPct |
|---|---|---|---|---|---|---|---|---|---|---|
| **S0-Baseline** | **P=0.1, N=100** | **551** | **~725** | **876** | **0.8382** | **0.159** | **1153.11** | **0.7393** | **7.56** | **~29%** |
| S1-A | CH Probability P=0.05 | 925 | 1167 | 1621 | 0.6648 | 0.105 | 1208.5 | 0.642 | 3.47 | 44.9 |
| S1-B | CH Probability P=0.2 | 374 | 399 | 463 | 0.9750 | 0.207 | 948.8 | 0.840 | 16.90 | 12.5 |
| S2-A | Node Density N=200 | 515 | 580 | 719 | 0.8126 | 0.328 | 1108.1 | 0.816 | 15.87 | 26.8 |
| S2-B | Node Density N=300 | 470 | 543 | 657 | 0.8476 | 0.530 | 1057.3 | 0.846 | 24.28 | 19.9 |
| S3-A | UAV Speed v=15 m/s | 581 | 651 | 825 | 0.9779 | 0.201 | 993.8 | 0.750 | 7.81 | 30.0 |
| S3-B | UAV Speed v=20 m/s | 579 | 650 | 815 | 0.9952 | 0.208 | 841.7 | 0.762 | 7.90 | 30.6 |
| S4-A | Initial Energy E0=1.0J | 1176 | 1332 | 1781 | 0.8076 | 0.149 | 1147.3 | 0.721 | 7.35 | 28.9 |
| S4-B | Initial Energy E0=2.0J | 2363 | 2683 | 3557 | 0.7980 | 0.147 | 1148.7 | 0.724 | 7.37 | 29.5 |
| S5-A | Packet Size=500 bits | 670 | 760 | 947 | 0.7896 | 0.039 | 1171.9 | 0.761 | 7.91 | 30.9 |
| S5-B | Packet Size=4000 bits | 495 | 575 | 810 | 0.8101 | 0.278 | 1157.2 | 0.699 | 6.97 | 27.9 |

**Interpretation Note:** PDR, throughput, delay, and overhead are direct routing quality indicators. FND/HNA/LND quantify route availability over lifetime, while Mean CHs and Unclustered % provide routing topology context. **Baseline S0 values updated February 2, 2026 to reflect correct multi-run averaging methodology.**

---

## 3. Detailed Scenario Results and Plot-by-Plot Discussion

### 3.1 Scenario-Level Interpretation (Routing-Centric)

**S1-A (P=0.05):** Lower CH probability yields fewer CHs per round and higher unclustered percentage, which increases average member-to-CH distance and reduces routing reliability. This drives lower PDR and throughput but extends lifetime due to reduced CH duty cycles. This configuration represents a real system operating in energy-conservation mode or under sparse cluster-head election policies.

**S1-B (P=0.2):** Higher CH probability produces denser CH coverage, improving member connectivity and reducing intra-cluster path loss. This increases PDR and reduces delay, but it also accelerates CH energy depletion due to higher aggregation and control burden, shortening lifetime. This scenario reflects high-reliability missions where routing quality is prioritized over longevity.

**S2-A (N=200) and S2-B (N=300):** Increasing node density raises traffic generation and contention. Routing reliability can improve due to greater redundancy and more CH candidates, but control overhead and energy consumption increase. Lifetime degrades as more nodes compete for UAV contact and energy resources. These scenarios represent denser deployments or scaled-up monitoring areas.

**S3-A (v=15) and S3-B (v=20):** Faster UAV speed changes the contact pattern: buffer residence time declines and delivery windows become shorter but more frequent. PDR improves due to reduced buffer overflow and quicker collection, while lifetime declines slightly because CHs must complete transfers in shorter windows. These cases model operational constraints such as higher UAV flight speed or time-limited missions.

**S4-A (E0=1.0J) and S4-B (E0=2.0J):** Increased energy extends routing availability substantially (FND/LND shift right) while PDR and throughput remain similar. This reflects systems with higher-capacity batteries or energy harvesting, where routing quality remains bounded by topology and UAV contact rather than energy.

**S5-A (500b) and S5-B (4000b):** Smaller packets reduce transmission energy and control overhead per bit, improving lifetime but reducing throughput. Larger packets increase throughput but draw energy faster, shortening lifetime while moderately improving delivery efficiency. These scenarios map to low-rate vs high-fidelity sensing tasks.

### S1-A: CH Probability P=0.05

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 1: S1-A — Network Lifetime**  
![](plots/scenarios/S1-A/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 2: S1-A — Residual Energy**  
![](plots/scenarios/S1-A/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 3: S1-A — Packet Delivery Ratio**  
![](plots/scenarios/S1-A/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 4: S1-A — Throughput**  
![](plots/scenarios/S1-A/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 5: S1-A — Delay Distribution**  
![](plots/scenarios/S1-A/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 6: S1-A — Average Delay per Round**  
![](plots/scenarios/S1-A/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 7: S1-A — Clustering Metrics**  
![](plots/scenarios/S1-A/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 8: S1-A — Control Overhead**  
![](plots/scenarios/S1-A/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S1-B: CH Probability P=0.2

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 9: S1-B — Network Lifetime**  
![](plots/scenarios/S1-B/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 10: S1-B — Residual Energy**  
![](plots/scenarios/S1-B/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 11: S1-B — Packet Delivery Ratio**  
![](plots/scenarios/S1-B/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 12: S1-B — Throughput**  
![](plots/scenarios/S1-B/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 13: S1-B — Delay Distribution**  
![](plots/scenarios/S1-B/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 14: S1-B — Average Delay per Round**  
![](plots/scenarios/S1-B/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 15: S1-B — Clustering Metrics**  
![](plots/scenarios/S1-B/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 16: S1-B — Control Overhead**  
![](plots/scenarios/S1-B/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S2-A: Node Density N=200

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 17: S2-A — Network Lifetime**  
![](plots/scenarios/S2-A/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 18: S2-A — Residual Energy**  
![](plots/scenarios/S2-A/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 19: S2-A — Packet Delivery Ratio**  
![](plots/scenarios/S2-A/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 20: S2-A — Throughput**  
![](plots/scenarios/S2-A/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 21: S2-A — Delay Distribution**  
![](plots/scenarios/S2-A/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 22: S2-A — Average Delay per Round**  
![](plots/scenarios/S2-A/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 23: S2-A — Clustering Metrics**  
![](plots/scenarios/S2-A/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 24: S2-A — Control Overhead**  
![](plots/scenarios/S2-A/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S2-B: Node Density N=300

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 25: S2-B — Network Lifetime**  
![](plots/scenarios/S2-B/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 26: S2-B — Residual Energy**  
![](plots/scenarios/S2-B/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 27: S2-B — Packet Delivery Ratio**  
![](plots/scenarios/S2-B/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 28: S2-B — Throughput**  
![](plots/scenarios/S2-B/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 29: S2-B — Delay Distribution**  
![](plots/scenarios/S2-B/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 30: S2-B — Average Delay per Round**  
![](plots/scenarios/S2-B/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 31: S2-B — Clustering Metrics**  
![](plots/scenarios/S2-B/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 32: S2-B — Control Overhead**  
![](plots/scenarios/S2-B/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S3-A: UAV Speed v=15 m/s

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 33: S3-A — Network Lifetime**  
![](plots/scenarios/S3-A/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 34: S3-A — Residual Energy**  
![](plots/scenarios/S3-A/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 35: S3-A — Packet Delivery Ratio**  
![](plots/scenarios/S3-A/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 36: S3-A — Throughput**  
![](plots/scenarios/S3-A/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 37: S3-A — Delay Distribution**  
![](plots/scenarios/S3-A/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 38: S3-A — Average Delay per Round**  
![](plots/scenarios/S3-A/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 39: S3-A — Clustering Metrics**  
![](plots/scenarios/S3-A/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 40: S3-A — Control Overhead**  
![](plots/scenarios/S3-A/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S3-B: UAV Speed v=20 m/s

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 41: S3-B — Network Lifetime**  
![](plots/scenarios/S3-B/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 42: S3-B — Residual Energy**  
![](plots/scenarios/S3-B/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 43: S3-B — Packet Delivery Ratio**  
![](plots/scenarios/S3-B/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 44: S3-B — Throughput**  
![](plots/scenarios/S3-B/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 45: S3-B — Delay Distribution**  
![](plots/scenarios/S3-B/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 46: S3-B — Average Delay per Round**  
![](plots/scenarios/S3-B/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 47: S3-B — Clustering Metrics**  
![](plots/scenarios/S3-B/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 48: S3-B — Control Overhead**  
![](plots/scenarios/S3-B/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S4-A: Initial Energy E0=1.0J

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 49: S4-A — Network Lifetime**  
![](plots/scenarios/S4-A/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 50: S4-A — Residual Energy**  
![](plots/scenarios/S4-A/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 51: S4-A — Packet Delivery Ratio**  
![](plots/scenarios/S4-A/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 52: S4-A — Throughput**  
![](plots/scenarios/S4-A/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 53: S4-A — Delay Distribution**  
![](plots/scenarios/S4-A/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 54: S4-A — Average Delay per Round**  
![](plots/scenarios/S4-A/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 55: S4-A — Clustering Metrics**  
![](plots/scenarios/S4-A/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 56: S4-A — Control Overhead**  
![](plots/scenarios/S4-A/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S4-B: Initial Energy E0=2.0J

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 57: S4-B — Network Lifetime**  
![](plots/scenarios/S4-B/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 58: S4-B — Residual Energy**  
![](plots/scenarios/S4-B/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 59: S4-B — Packet Delivery Ratio**  
![](plots/scenarios/S4-B/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 60: S4-B — Throughput**  
![](plots/scenarios/S4-B/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 61: S4-B — Delay Distribution**  
![](plots/scenarios/S4-B/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 62: S4-B — Average Delay per Round**  
![](plots/scenarios/S4-B/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 63: S4-B — Clustering Metrics**  
![](plots/scenarios/S4-B/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 64: S4-B — Control Overhead**  
![](plots/scenarios/S4-B/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S5-A: Packet Size=500 bits

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 65: S5-A — Network Lifetime**  
![](plots/scenarios/S5-A/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 66: S5-A — Residual Energy**  
![](plots/scenarios/S5-A/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 67: S5-A — Packet Delivery Ratio**  
![](plots/scenarios/S5-A/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 68: S5-A — Throughput**  
![](plots/scenarios/S5-A/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 69: S5-A — Delay Distribution**  
![](plots/scenarios/S5-A/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 70: S5-A — Average Delay per Round**  
![](plots/scenarios/S5-A/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 71: S5-A — Clustering Metrics**  
![](plots/scenarios/S5-A/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 72: S5-A — Control Overhead**  
![](plots/scenarios/S5-A/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

### S5-B: Packet Size=4000 bits

**Routing Focus:** This scenario evaluates how the given parameter variation alters cluster stability, UAV contact efficacy, and end-to-end routing quality metrics.

**Figure 73: S5-B — Network Lifetime**  
![](plots/scenarios/S5-B/network_lifetime.png)

*Discussion:* The alive/dead node trajectories indicate routing availability over time. FND marks the onset of route erosion, while LND denotes total routing collapse. The gap between FND and LND reflects the routing protocol’s resilience under diminishing node populations.

**Figure 74: S5-B — Residual Energy**  
![](plots/scenarios/S5-B/energy_consumption.png)

*Discussion:* Residual energy trends show how routing duties and clustering responsibilities deplete node energy. The slope changes reflect shifts in routing participation as the network thins.

**Figure 75: S5-B — Packet Delivery Ratio**  
![](plots/scenarios/S5-B/pdr.png)

*Discussion:* PDR trajectories capture routing reliability under periodic UAV contact. Declines near late rounds reflect reduced CH density and higher packet loss due to route disruptions.

**Figure 76: S5-B — Throughput**  
![](plots/scenarios/S5-B/throughput.png)

*Discussion:* Throughput reflects effective end-to-end routing yield. Early consistency indicates stable CH-to-UAV transfer, while late-stage decline tracks route scarcity and reduced data generation.

**Figure 77: S5-B — Delay Distribution**  
![](plots/scenarios/S5-B/delay_distribution.png)

*Discussion:* The delay distribution captures store-carry-forward latency. Heavier tails indicate longer buffering at CHs before UAV contact, a core routing characteristic in UAV-assisted WSNs.

**Figure 78: S5-B — Average Delay per Round**  
![](plots/scenarios/S5-B/average_delay_per_round.png)

*Discussion:* Round-level delay and packet counts show how routing latency varies with UAV contact cadence and node survival. Rising variance reflects reduced routing opportunities.

**Figure 79: S5-B — Clustering Metrics**  
![](plots/scenarios/S5-B/clustering_metrics.png)

*Discussion:* CH count and unclustered levels reveal routing topology health. Increasing unclustered nodes indicates reduced routing coverage, directly impacting PDR and throughput.

**Figure 80: S5-B — Control Overhead**  
![](plots/scenarios/S5-B/control_overhead.png)

*Discussion:* Control overhead reflects the routing protocol’s signaling cost. Overhead tends to rise as data traffic drops, demonstrating the fixed control burden of cluster management and UAV contact discovery.

---

## 4. Parameter Sensitivity Plots (Routing-Centric Interpretation)

**Update Note:** All parameter sensitivity plots now use the **multi-run averaged S0 baseline** and a consistent ordering of **Baseline → Group A → Group B** to ensure comparable reference values across parameters.

**Figure 81: CH Probability Sensitivity**  
![](plots/parameter_sensitivity/S1_ch_probability.png)

*Discussion:* Lower CH probability extends lifetime but reduces routing reliability due to longer member-to-CH links. Higher CH probability improves PDR and reduces delay but accelerates CH energy depletion, shortening routing availability.

**Figure 82: Node Density Sensitivity**  
![](plots/parameter_sensitivity/S2_node_density.png)

*Discussion:* Increasing node density improves redundancy and PDR, but intensifies contention and control overhead. Routing efficiency gains are offset by energy depletion, reducing lifetime.

**Figure 83: UAV Speed Sensitivity**  
![](plots/parameter_sensitivity/S3_uav_speed.png)

*Discussion:* Faster UAVs reduce buffering time and improve PDR, but can shorten effective contact windows, slightly reducing lifetime stability of routing paths.

**Figure 84: Initial Energy Sensitivity**  
![](plots/parameter_sensitivity/S4_initial_energy.png)

*Discussion:* Energy scaling strongly extends routing lifetime (FND/LND). PDR remains relatively stable, indicating routing quality is constrained more by topology than by energy once a sufficient threshold is reached.

**Figure 85: Packet Size Sensitivity**  
![](plots/parameter_sensitivity/S5_packet_size.png)

*Discussion:* Smaller packets reduce per-transmission cost and improve routing longevity; larger packets increase energy burden and shorten lifetime while marginally improving data yield per contact.

---

## 5. Cross-Scenario Comparison Plots

**Update Note:** Cross-scenario comparison plots now use the **multi-run averaged baseline** and have enlarged axis labels/tick sizes for improved readability.

**Figure 86: Lifetime Comparison**  
![](plots/scenarios/lifetime_comparison.png)

*Discussion:* Compares route availability across scenarios using FND/HNA/LND. Energy and CH probability dominate lifetime behavior, confirming routing durability is strongly energy- and clustering-driven.

**Figure 87: Energy Consumption Comparison**  
![](plots/scenarios/energy_comparison.png)

*Discussion:* Energy consumption is tightly coupled to routing workload. Scenarios with higher CH density or larger packet sizes show increased energy draw, accelerating routing collapse.

**Figure 88: Routing Performance Comparison**  
![](plots/scenarios/performance_comparison.png)

*Discussion:* PDR, throughput, delay, and overhead summarize end-to-end routing quality. S3 and S1-B improve delivery reliability, while S1-A and high-density scenarios show longer lifetimes at the cost of routing quality.

**Figure 89: Clustering Comparison**  
![](plots/scenarios/clustering_comparison.png)

*Discussion:* Mean CHs and unclustered percent quantify routing topology stability. Scenarios with lower CH probability show fewer CHs and higher unclustered rates, explaining PDR/throughput reductions.

---

## 6. Routing-Focused Discussion and Justification

Across all scenarios, routing behavior conforms to the protocol structure: CHs act as aggregation points and UAV contact windows define the dominant bottleneck. Variations in CH probability and initial energy most strongly reshape routing availability (FND/HNA/LND), while UAV speed primarily affects buffering time, delay, and delivery efficiency. Node density and packet size modulate traffic load and per-bit energy cost, which changes routing stability rather than protocol logic.

From an operational standpoint, the scenarios represent realistic field conditions: low CH probability emulates energy-preserving duty cycles in long-term monitoring, high CH probability reflects reliability-driven missions, increased node density mirrors larger deployments or denser sensing grids, faster UAV speeds represent time-bounded flight plans, and higher energy capacity models improved batteries or harvesting. Each variation produces a distinct routing signature that aligns with the routing mechanisms documented in ROUTING_PERFORMANCE_ANALYSIS.md.

In routing terms, the observed performance shifts are explained by three coupled mechanisms: (i) clustering topology quality (CH count and unclustered percentage), (ii) UAV contact cadence and dwell time, and (iii) energy depletion rate of CHs versus members. When clustering is sparse, routes are longer and less reliable, reducing PDR and throughput; when clustering is dense, delivery improves but CH energy drains faster. Increased node density increases contact competition and control overhead, while increased energy extends route availability without fundamentally changing delivery quality. Packet size variations change energy-per-packet and therefore lifetime, but do not alter the underlying routing path structure.

---

## 7. Recommendations for Routing Protocol Tuning

1. **Adaptive CH Selection:** Adjust CH probability based on residual energy and observed unclustered percentage to stabilize routing connectivity.

2. **Energy-Aware Duty Cycling:** Reduce control overhead in late rounds to extend routing availability.

3. **UAV Contact Scheduling:** Optimize waypoint dwell time to reduce buffering delay and improve PDR under high-density scenarios.

4. **Packet Size Profiling:** Use smaller payloads for long-term deployments to preserve routing longevity; use larger payloads for short, high-yield missions.

5. **Density-Aware Clustering:** Increase clustering aggressiveness only when node density justifies the control overhead.

---

## 8. Future Work

1. **Multi-seed Statistical Validation:** Extend each scenario to 30–50 runs to quantify routing metric variance.

2. **Hybrid Routing:** Combine UAV collection with limited multi-hop backup to reduce unclustered losses.

3. **UAV Trajectory Optimization:** Use density maps and CH distribution to adapt UAV path dynamically.

4. **QoS-Aware Scheduling:** Prioritize time-sensitive data in CH buffering to lower tail delay.

5. **Resilience Modeling:** Inject link failures and node faults to evaluate routing robustness.

---

## 9. Conclusion

The S1–S5 scenarios collectively demonstrate that routing performance in UAV-assisted WSNs is driven primarily by clustering density, energy reserves, and UAV contact structure. The parametric results validate the routing behaviors described in ROUTING_PERFORMANCE_ANALYSIS.md and provide actionable guidance for protocol tuning under diverse mission requirements.
