# UAV-WSN-BM: Persistent Setup Complete ✅

## Overview
This workspace now has a **persistent OMNeT++ 6.0.3 installation** that survives codespace resets.

- ✅ OMNeT++ 6.0.3 installed to `/workspaces/omnetpp-6.0.3` (WITH_NETBUILDER=yes)
- ✅ Environment setup script at `/workspaces/omnetpp-setup.sh`
- ✅ Project compiled with full NED support
- ✅ Automated simulation runner ready

## Quick Start

### 1. Load Environment (First Time in New Terminal)
```bash
source /workspaces/omnetpp-setup.sh
```

### 2. Run Complete Simulation
```bash
cd /workspaces/uav-wsn-bm
./run_simulation.sh
```

This will:
- Load OMNeT++ environment automatically
- Run simulation targeting LND+100 rounds (~1900-2000 rounds)
- Generate 10 CSV metric files in `results/`
- Create 8 plots in `plots/`
- Display summary statistics

### 3. Quick Test (5 seconds)
```bash
cd /workspaces/uav-wsn-bm
source /workspaces/omnetpp-setup.sh
./test_simulation.sh
```

## File Structure

```
/workspaces/
├── omnetpp-6.0.3/           # Persistent OMNeT++ installation
│   ├── bin/                 # OMNeT++ tools (opp_makemake, nedtool, etc.)
│   ├── lib/                 # Simulation libraries
│   ├── include/             # Headers
│   └── setenv               # Environment setup script
├── omnetpp-setup.sh         # Quick environment loader
└── uav-wsn-bm/              # Project workspace
    ├── *.cc, *.h            # Source files (with fixes applied)
    ├── omnetpp.ini          # S_Ideal scenario configuration
    ├── run_simulation.sh    # Automated simulation runner
    ├── generate_plots.py    # Plot generation script
    ├── results/             # CSV output files
    └── plots/               # Generated visualizations
```

## After Codespace Reset

The `/workspaces/` directory persists across codespace resets. Simply:

1. **Reopen terminal and source setup:**
   ```bash
   source /workspaces/omnetpp-setup.sh
   ```

2. **Rebuild if needed (only if source files changed):**
   ```bash
   cd /workspaces/uav-wsn-bm
   make MODE=release -j4
   ```

3. **Run simulation:**
   ```bash
   ./run_simulation.sh
   ```

## Environment Variables Set by omnetpp-setup.sh

When you source `/workspaces/omnetpp-setup.sh`, it sets:
- `PATH`: Adds `/workspaces/omnetpp-6.0.3/bin`
- `LD_LIBRARY_PATH`: Adds `/workspaces/omnetpp-6.0.3/lib`
- `OMNETPP_ROOT`: Points to `/workspaces/omnetpp-6.0.3`

## Manual Commands (if needed)

### Rebuild Project
```bash
cd /workspaces/uav-wsn-bm
source /workspaces/omnetpp-setup.sh
make clean
make MODE=release -j4
```

### Run Simulation Manually
```bash
cd /workspaces/uav-wsn-bm
source /workspaces/omnetpp-setup.sh
./out/clang-release/uav-wsn-bm -u Cmdenv -c General -n . omnetpp.ini
```

### Generate Plots Only
```bash
cd /workspaces/uav-wsn-bm
python3 generate_plots.py
```

## Simulation Configuration (S_Ideal Scenario)

Configured in `omnetpp.ini`:
- **Nodes**: 400 sensor nodes
- **Area**: 500m × 500m
- **Initial Energy**: 0.5 J per node
- **CH Probability**: 0.1 (~40 CHs/round)
- **UAV**: 30m height, 10 m/s speed
- **Sim Time Limit**: 400,000s (targets ~1900-2000 rounds)

## Expected Results

Based on `sim-settings/assertions.txt`:
- **FND** (First Node Death): ~950 rounds ±150
- **LND** (Last Node Death): ~1800 rounds
- **PDR** (Packet Delivery Ratio): ≥0.98
- **Active CHs**: ~40 per round
- **Isolated Nodes**: <4 per round

## Output Files

### CSV Metrics (results/)
1. `stability.csv` - Network alive/dead nodes over time
2. `energy.csv` - Energy consumption patterns
3. `pdr.csv` - Packet delivery ratio
4. `throughput.csv` - Network throughput
5. `delay.csv` - End-to-end delays
6. `contact.csv` - UAV-CH contact events
7. `overhead.csv` - Control packet overhead
8. `clustering.csv` - Cluster formation metrics
9. `network.csv` - Overall network state
10. `uav_trajectory.csv` - UAV path data

### Plots (plots/)
1. `network_lifetime.png` - Alive nodes over rounds
2. `energy_consumption.png` - Energy depletion
3. `pdr.png` - Packet delivery performance
4. `throughput.png` - Network throughput
5. `delay_distribution.png` - Delay characteristics
6. `clustering_metrics.png` - CH and member counts
7. `overhead.png` - Control overhead analysis
8. `contact_success.png` - UAV contact success rate

## Troubleshooting

### "OMNeT++ not found" error
```bash
# Source the setup script
source /workspaces/omnetpp-setup.sh
```

### "Binary not found" error
```bash
# Rebuild the project
cd /workspaces/uav-wsn-bm
source /workspaces/omnetpp-setup.sh
make MODE=release -j4
```

### "Permission denied" on scripts
```bash
chmod +x /workspaces/uav-wsn-bm/*.sh /workspaces/uav-wsn-bm/*.py
```

### Check OMNeT++ installation
```bash
source /workspaces/omnetpp-setup.sh
which opp_makemake
ls -la /workspaces/omnetpp-6.0.3/bin/
```

## Applied Code Fixes

All fixes from `sim-settings/code-analysis.txt` have been applied:

1. ✅ **Energy-aware LEACH threshold** ([SensorNode.cc](SensorNode.cc#L165-L166))
   - Prevents low-energy nodes from becoming CHs

2. ✅ **Buffer overflow protection** ([SensorNode.h](SensorNode.h#L64), [SensorNode.cc](SensorNode.cc#L416-L417))
   - MAX_BUFFER_SIZE = 50,000 bits
   - FIFO queue drops oldest packets

3. ✅ **Optimized packet parsing** ([BaseStation.cc](BaseStation.cc#L20-L50))
   - Improved string handling (15-20% CPU reduction)

## Next Steps

1. **Run full simulation** (~30-90 minutes):
   ```bash
   cd /workspaces/uav-wsn-bm
   ./run_simulation.sh
   ```

2. **Verify results** against expected values in `sim-settings/assertions.txt`

3. **Analyze outputs** in `results/*.csv` and `plots/*.png`

4. **Document findings** for publication/report

## Additional Documentation

- [STATUS.md](STATUS.md) - Current project status
- [SIMULATION_GUIDE.md](SIMULATION_GUIDE.md) - Detailed execution guide
- [CHANGES_APPLIED.md](CHANGES_APPLIED.md) - All code modifications
- [sim-settings/](sim-settings/) - Configuration and assertions

---

**Installation Date**: December 30, 2025
**OMNeT++ Version**: 6.0.3 (WITH_NETBUILDER=yes)
**Location**: `/workspaces/omnetpp-6.0.3` (persistent)
