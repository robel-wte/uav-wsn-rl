#!/usr/bin/env python3
"""
Update all summary.txt files in scenario directories with latest metrics
"""

import pandas as pd
from pathlib import Path

SCENARIOS = {
    'S0-Baseline': 'S0-Baseline',
    'S1-A': 'S1-A',
    'S1-B': 'S1-B',
    'S2-A': 'S2-A',
    'S2-B': 'S2-B',
    'S3-A': 'S3-A',
    'S3-B': 'S3-B',
    'S4-A': 'S4-A',
    'S4-B': 'S4-B',
    'S5-A': 'S5-A',
    'S5-B': 'S5-B',
}

SCENARIO_DESCRIPTIONS = {
    'S0-Baseline': 'Baseline (P=0.1, N=100, v=10m/s, E=0.5J, Size=2000b)',
    'S1-A': 'CH Probability P=0.05 (50% of baseline)',
    'S1-B': 'CH Probability P=0.2 (200% of baseline)',
    'S2-A': 'Node Density N=200 (200% of baseline)',
    'S2-B': 'Node Density N=300 (300% of baseline)',
    'S3-A': 'UAV Speed v=15 m/s (150% of baseline)',
    'S3-B': 'UAV Speed v=20 m/s (200% of baseline)',
    'S4-A': 'Initial Energy E=1.0J (200% of baseline)',
    'S4-B': 'Initial Energy E=2.0J (400% of baseline)',
    'S5-A': 'Data Packet Size = 500 bits (25% of baseline)',
    'S5-B': 'Data Packet Size = 4000 bits (200% of baseline)',
}


def update_summary_file(scenario_name, metrics_dir):
    """Update summary.txt file for a scenario"""
    
    metrics_file = metrics_dir / 'metrics_summary.csv'
    
    if not metrics_file.exists():
        print(f"  ✗ {scenario_name}: metrics_summary.csv not found")
        return False
    
    try:
        df = pd.read_csv(metrics_file)
        if len(df) == 0:
            print(f"  ✗ {scenario_name}: empty metrics file")
            return False
        
        metrics = df.iloc[0]
        
        # Create summary content
        summary = f"""Scenario: {scenario_name}
====================

Description:
{SCENARIO_DESCRIPTIONS.get(scenario_name, 'N/A')}

Network Lifetime:
-----------------
FND (First Node Death): {int(metrics['FND'])} rounds
LND (Last Node Death): {int(metrics['LND'])} rounds
HNA (Half Nodes Alive): {int(metrics['HNA'])} rounds
Lifetime (LND-FND): {int(metrics['Lifetime'])} rounds

Energy:
-------
Total Energy Consumed: {metrics['TotalEnergy_J']:.4f} J
Mean Energy Per Round: {metrics['MeanEnergyPerRound_J']:.6f} J
Std Energy Per Round: {metrics['StdEnergyPerRound_J']:.6f} J

Performance Metrics:
-------------------
Mean PDR: {metrics['MeanPDR']:.4f}
Std PDR: {metrics['StdPDR']:.4f}
Min PDR: {metrics['MinPDR']:.4f}
Max PDR: {metrics['MaxPDR']:.4f}

Mean Delay: {metrics['MeanDelay_s']:.2f} s
Median Delay: {metrics['MedianDelay_s']:.2f} s
Std Delay: {metrics['StdDelay_s']:.2f} s
P95 Delay: {metrics['P95Delay_s']:.2f} s

Mean Throughput: {metrics['MeanThroughput_bps']:.2f} bps ({metrics['MeanThroughput_bps']/1000:.4f} kbps)
Peak Throughput: {metrics['PeakThroughput_bps']:.2f} bps ({metrics['PeakThroughput_bps']/1000:.4f} kbps)
Zero Throughput Rounds: {int(metrics['ZeroThroughputRounds'])} ({metrics['ZeroThroughputPercent']:.2f}%)

Clustering Metrics:
------------------
Mean Cluster Heads: {metrics['MeanCHs']:.2f}
Std Cluster Heads: {metrics['StdCHs']:.2f}
Mean Unclustered Nodes: {metrics['MeanUnclusteredNodes']:.2f}
Unclustered Percentage: {metrics['UnclusteredPercent']:.2f}%

Contact Performance:
-------------------
Total Contacts: {int(metrics['TotalContacts'])}
Contact Success Rate: {metrics['ContactSuccessRate']:.2%}
Mean Contact Duration: {metrics['MeanContactDuration_s']:.2f} s
Std Contact Duration: {metrics['StdContactDuration_s']:.2f} s

Control Overhead:
----------------
Mean Control Ratio: {metrics['MeanControlRatio']:.4f}
Total Control Packets: {int(metrics['TotalControlPackets'])}
Total Data Packets: {int(metrics['TotalDataPackets'])}
Packet Ratio: {int(metrics['TotalControlPackets'])}:{int(metrics['TotalDataPackets'])}

"""
        
        summary_file = metrics_dir / 'summary.txt'
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"  ✓ {scenario_name}: Updated")
        return True
        
    except Exception as e:
        print(f"  ✗ {scenario_name}: Error - {e}")
        return False


def main():
    """Update all summary.txt files"""
    
    print("=" * 60)
    print("Updating Summary Files for All Scenarios")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for scenario_name, dir_name in SCENARIOS.items():
        scenario_dir = Path(f'results/scenarios/{dir_name}')
        
        if not scenario_dir.exists():
            print(f"  ⚠ {scenario_name}: Directory not found")
            continue
        
        if update_summary_file(scenario_name, scenario_dir):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary Update Complete!")
    print(f"  ✓ Updated: {success_count} scenarios")
    if fail_count > 0:
        print(f"  ✗ Failed: {fail_count} scenarios")
    print("=" * 60)


if __name__ == '__main__':
    main()
