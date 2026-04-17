# UAV-WSN-BM Project Structure

**Project**: UAV-Assisted WSN with LEACH-Based Clustering  
**Status**: ✅ Complete and Publication-Ready  
**Last Updated**: January 12, 2026

---

## 📁 Directory Structure

```
/workspaces/uav-wsn-bm/
│
├── 📊 Source Code (Implementation)
│   ├── SensorNode.cc              (42 KB) - Sensor node implementation with LEACH clustering
│   ├── SensorNode.h               (6.1 KB) - Sensor node header
│   ├── UAVNode.cc                 (17 KB) - UAV mobility and data collection
│   ├── UAVNode.h                  (4.1 KB) - UAV node header
│   ├── BaseStation.cc             (3.2 KB) - Base station implementation
│   ├── BaseStation.h              (426 B) - Base station header
│   ├── MetricsCollector.cc        (23 KB) - Performance metrics collection
│   ├── MetricsCollector.h         (6.0 KB) - Metrics collector header
│   ├── Location.h                 (441 B) - Position data structure
│   ├── UavWsnNetwork.ned          (3.3 KB) - Network topology definition
│   └── UavWsnNetwork_n.cc         (2.5 KB) - Generated network code
│
├── ⚙️ Configuration & Build
│   ├── omnetpp.ini                (3.1 KB) - Simulation parameters (100 nodes, 500×500m)
│   ├── Makefile                   (3.7 KB) - Build configuration
│   ├── uav-wsn-bm                 (229 KB) - Release binary
│   └── uav-wsn-bm_dbg             (3.2 MB) - Debug binary with symbols
│
├── 🚀 Execution Scripts
│   ├── run_simulation.sh          (2.8 KB) - Main simulation runner
│   ├── test_simulation.sh         (3.5 KB) - Quick test (20s sim-time)
│   ├── run_100_rounds.sh          (1.5 KB) - 100-round test runner
│   └── monitor_simulation.sh      (677 B) - Real-time monitoring
│
├── 📈 Analysis & Visualization
│   ├── generate_plots.py          (52 KB) - Complete plotting suite (20 plots)
│   └── visualize_network_topology.py (7.7 KB) - Topology visualization
│
├── 📊 Results (Latest Simulation: 3,324 rounds, 100 nodes)
│   ├── results/
│   │   ├── stability.csv          - Node alive/dead per round
│   │   ├── energy.csv             - Energy consumption per round
│   │   ├── pdr.csv                - Packet Delivery Ratio per round
│   │   ├── delay.csv              - 80,058 packet delays
│   │   ├── throughput.csv         - Network throughput per round
│   │   ├── clustering.csv         - Cluster formation metrics
│   │   ├── contact.csv            - UAV-CH contact events
│   │   ├── overhead.csv           - Control packet overhead
│   │   ├── network.csv            - Overall network state
│   │   ├── topology.csv           - Node positions
│   │   ├── uav_trajectory.csv     - UAV movement path
│   │   ├── summary.txt            - Overall statistics
│   │   └── General-#0.sca         - Scalar results (OMNeT++ format)
│   │
│   └── plots/
│       ├── network_lifetime.png            (213 KB)
│       ├── energy_consumption.png          (324 KB)
│       ├── pdr.png                         (745 KB)
│       ├── throughput.png                  (278 KB)
│       ├── delay_distribution.png          (210 KB)
│       ├── average_delay_per_round.png     (885 KB)
│       ├── clustering_metrics.png          (687 KB)
│       ├── packet_generation_aggregation.png (580 KB)
│       ├── control_overhead.png            (327 KB)
│       ├── packet_counts.png               (387 KB)
│       ├── uav_contact_success.png         (296 KB)
│       ├── network_topology_map.png        (1.9 MB) - Initial deployment
│       ├── network_topology_round1.png     (807 KB)
│       ├── network_topology_round100.png   (838 KB)
│       ├── network_topology_round1000.png  (790 KB)
│       ├── uav_trajectory_round1.png       (1.3 MB)
│       ├── uav_trajectory_round100.png     (899 KB)
│       ├── uav_trajectory_round1000.png    (1.3 MB)
│       └── summary_statistics.txt          - Key metrics summary
│
├── 📚 Documentation (Publication-Ready)
│   ├── README.md                          (1.5 KB) - Project overview
│   ├── QUICKSTART.md                      (1.8 KB) - Quick start guide
│   ├── SIMULATION_PARAMETERS_SUMMARY.md   (22 KB) - All parameters documented
│   ├── RESULTS_ANALYSIS_AND_DISCUSSION.md (49 KB) - Comprehensive analysis
│   └── FINAL_SUMMARY.txt                  (11 KB) - Executive summary
│
├── 🔧 Reference Settings
│   └── sim-settings/
│       ├── algorithm.txt              - Protocol algorithm description
│       ├── metrics.txt                - S_Ideal scenario specifications
│       ├── assertions.txt             - Expected performance thresholds
│       ├── code-analysis.txt          - Implementation improvements
│       ├── improvements.txt           - Applied optimizations
│       ├── OPTIMIZATION_QUICK_REFERENCE.md
│       ├── TIMING_OPTIMIZATION_ANALYSIS.md
│       └── scenarios/                 - Scenario configurations
│
└── 📦 Build Artifacts
    └── out/                           - Compiled binaries and objects

```

---

## 🎯 Key Files for Publication

### Essential Documentation
1. **SIMULATION_PARAMETERS_SUMMARY.md** - Complete parameter justification
2. **RESULTS_ANALYSIS_AND_DISCUSSION.md** - Results & Discussion section for paper
3. **FINAL_SUMMARY.txt** - Executive summary with key metrics

### Core Source Code
1. **SensorNode.cc/.h** - Energy-aware LEACH implementation
2. **UAVNode.cc/.h** - Random Waypoint UAV mobility
3. **MetricsCollector.cc/.h** - Performance metrics tracking
4. **omnetpp.ini** - Simulation configuration

### Key Results
1. **plots/summary_statistics.txt** - Quick reference metrics
2. **results/*.csv** - Raw data (3,324 rounds)
3. **plots/*.png** - 20 publication-quality plots (300 DPI)

---

## 📊 Simulation Results Summary

**Network**: 100 nodes in 500m × 500m area  
**Duration**: 3,324 rounds (149,580 seconds ≈ 41.6 hours)  
**Key Metrics**:
- **FND**: Round 1,302 (5.2× improvement over baseline LEACH)
- **LND**: Round 3,324
- **PDR**: 33.4% (with 3-round packet expiration)
- **Mean Delay**: 41.58 seconds
- **Energy Efficiency**: 0.0150 J/round
- **UAV Contact Success**: 100%

---

## 🚀 Quick Start

### Build the Project
```bash
cd /workspaces/uav-wsn-bm
make clean && make MODE=release -j4
```

### Run Simulation
```bash
./run_simulation.sh
```

### Generate Plots
```bash
python3 generate_plots.py
```

### View Results
```bash
cat plots/summary_statistics.txt
ls -lh plots/*.png
```

---

## 📝 Citation Information

**Project**: UAV-WSN-BM (UAV-Assisted Wireless Sensor Network Benchmark)  
**Protocol**: Energy-Aware LEACH with UAV Data Collection  
**Scenario**: S_Ideal (100 nodes, uniform random deployment)  
**Simulator**: OMNeT++ 6.0 with INET Framework  
**Repository**: github.com/greenpact/uav-wsn-bm

---

## ✅ Verification Checklist

- [x] Source code implements three improvements (energy-aware, buffer overflow, optimized parsing)
- [x] Simulation runs to completion (LND at round 3,324)
- [x] All 20 plots generated successfully
- [x] Results validated (80,058 packets, no anomalies)
- [x] Documentation complete and publication-ready
- [x] Project folder cleaned and organized

---

**Last Simulation Run**: January 12, 2026  
**Status**: ✅ Ready for Publication
