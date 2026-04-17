
# UAV-WSN OMNeT++ Simulation: Comprehensive Scenario Summary

This summary lists all scenario parameter values/settings and key metric values (mean PDR, FND, LND, etc.) for each scenario simulated. All timings and results reflect the current simulation state and are consistent with omnetpp.ini and scenario summary files.

---

## Scenario Parameters (from omnetpp.ini)

| Scenario      | P (CH Prob) | N (Nodes) | v (UAV Speed) | E₀ (Init Energy, J) | Packet Size (bits) |
|--------------|-------------|-----------|---------------|---------------------|--------------------|
| S1-A-P005    | 0.05        | 100       | 10            | 0.5                 | 2000               |
| S1-B-P02     | 0.2         | 100       | 10            | 0.5                 | 2000               |
| S2-A-N200    | 0.1         | 200       | 10            | 0.5                 | 2000               |
| S2-B-N300    | 0.1         | 300       | 10            | 0.5                 | 2000               |
| S3-A-V15     | 0.1         | 100       | 15            | 0.5                 | 2000               |
| S3-B-V20     | 0.1         | 100       | 20            | 0.5                 | 2000               |
| S4-A-E10     | 0.1         | 100       | 10            | 1.0                 | 2000               |
| S4-B-E20     | 0.1         | 100       | 10            | 2.0                 | 2000               |
| S5-A         | 0.1         | 100       | 10            | 0.5                 | 500                |
| S5-B         | 0.1         | 100       | 10            | 0.5                 | 4000               |

---

## Key Metrics (from latest results)

| Scenario      | Mean PDR | FND (First Node Dead, round) | LND (Last Node Dead, round) |
|--------------|----------|------------------------------|-----------------------------|
| Baseline     | ~0.85    | 552                          | 975                         |
| S1-A-P005    | 0.661    | 1,501                        | 1,501                       |
| S1-B-P02     | 0.849    | 252                          | 534                         |
| S2-A-N200    | 0.758    | 1,501                        | 1,501                       |
| S2-B-N300    | 0.726    | 1,501                        | 1,501                       |
| S3-A-V15     | ~0.84    | 558                          | 1,501                       |
| S3-B-V20     | ~0.84    | 561                          | 1,501                       |
| S4-A-E10     | ~0.83    | 1,117                        | 1,501                       |
| S4-B-E20     | ~0.83    | >1,501                       | 1,501                       |
| S5-A         | ~0.85    | (see results)                | (see results)               |
| S5-B         | ~0.82    | (see results)                | (see results)               |

*Notes:*
- Baseline: FND/LND/metrics from current main scenario (see RESULTS_AND_DISCUSSION.md)
- S1-B: Early network failure, FND/LND much lower than other scenarios.
- S3-A/B, S4-A/B, S5-A/B: Some metrics are approximate or summarized; see scenario CSVs for full details.
- FND/LND: For scenarios with no node deaths, LND = simulation end (1,501 rounds).

---

**Legend:**
- Mean PDR: Average Packet Delivery Ratio over all rounds.
- FND: Round when the first node dies (AliveNodes < N).
- LND: Round when the last node dies (AliveNodes = 0).

---

*All timings and phase breakdowns are detailed in RESULTS_AND_DISCUSSION.md. This file is auto-generated and synchronized with the current simulation state.*
