# UAV-WSN-BM - Quick Reference Card

## ✅ Persistent Setup Complete!

OMNeT++ 6.0.3 is installed to `/workspaces/omnetpp-6.0.3` (738 MB) and **survives codespace resets**.

## 🚀 Run Simulation (3 Simple Steps)

```bash
# 1. Load environment (in each new terminal)
source /workspaces/omnetpp-setup.sh

# 2. Go to project
cd /workspaces/uav-wsn-bm

# 3. Run simulation
./run_simulation.sh
```

**Runtime**: 30-90 minutes | **Output**: 10 CSV files + 8 plots

## ⚡ Quick Test (5 seconds)

```bash
source /workspaces/omnetpp-setup.sh
cd /workspaces/uav-wsn-bm
./test_simulation.sh
```

## 🔄 After Codespace Reset

Simply reload environment:
```bash
source /workspaces/omnetpp-setup.sh
```

**No reinstallation needed!** Everything in `/workspaces/` persists.

## 📚 Documentation

| File | Purpose |
|------|---------|
| [PERSISTENT_SETUP.md](PERSISTENT_SETUP.md) | Complete setup guide |
| [STATUS.md](STATUS.md) | Project status |
| [CHANGES_APPLIED.md](CHANGES_APPLIED.md) | Applied fixes |
| [/workspaces/README_PERSISTENT_INSTALLATION.md](/workspaces/README_PERSISTENT_INSTALLATION.md) | Installation reference |


## 📊 Expected Results (Current Baseline)

- **FND**: 552 rounds (427,248 s ≈ 118.7 hours)
- **LND**: 975 rounds (754,650 s ≈ 209.6 hours)
- **Network Lifetime (LND-FND)**: 423 rounds (90.9 hours)
- **Mean PDR**: ~0.85 (see summary_scenarios_metrics.md)
- **Active CHs**: ~10 per round (baseline)
- **Round Duration**: 774 s (see phase breakdown in README.md)

See `RESULTS_AND_DISCUSSION.md` and `summary_scenarios_metrics.md` for full scenario results and timings.

## 🛠️ Rebuild if Needed

```bash
source /workspaces/omnetpp-setup.sh
cd /workspaces/uav-wsn-bm
make clean && make MODE=release -j4
```

## ✨ Auto-Load on Startup (Optional)

```bash
echo "source /workspaces/startup.sh" >> ~/.bashrc
```

Now every terminal automatically loads OMNeT++ environment!

---

**Status**: Production Ready ✅  
**Persistence**: Survives resets ✅  
**Next**: Run `./run_simulation.sh`
