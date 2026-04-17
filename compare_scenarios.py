#!/usr/bin/env python3
"""
Compare all parametric scenarios against baseline
Generates publication-ready comparison tables
"""

import pandas as pd
import os
from pathlib import Path

def read_metrics(csv_file):
    """Read metrics from CSV file."""
    if not os.path.exists(csv_file):
        return None
    df = pd.read_csv(csv_file)
    if len(df) > 0:
        return df.iloc[-1]  # Last row (final values)
    return None

def main():
    print("\n" + "="*80)
    print("PARAMETRIC SCENARIO COMPARISON")
    print("="*80 + "\n")
    
    # Define all scenarios
    scenarios = {
        'Baseline': {
            'path': 'results/multi-run/run-1',
            'label': 'Baseline (N=100, P=0.1, v=10, E=0.5J)',
            'params': {'N': 100, 'P': 0.1, 'v': 10, 'E': 0.5}
        },
        'S1-A': {
            'path': 'results/S1-CH-Probability/S1-A-P005',
            'label': 'S1-A: Low CH Prob (P=0.05)',
            'params': {'N': 100, 'P': 0.05, 'v': 10, 'E': 0.5}
        },
        'S1-B': {
            'path': 'results/S1-CH-Probability/S1-B-P020',
            'label': 'S1-B: High CH Prob (P=0.2)',
            'params': {'N': 100, 'P': 0.2, 'v': 10, 'E': 0.5}
        },
        'S2-A': {
            'path': 'results/S2-Node-Density/S2-A-N200',
            'label': 'S2-A: Medium Density (N=200)',
            'params': {'N': 200, 'P': 0.1, 'v': 10, 'E': 0.5}
        },
        'S2-B': {
            'path': 'results/S2-Node-Density/S2-B-N300',
            'label': 'S2-B: High Density (N=300)',
            'params': {'N': 300, 'P': 0.1, 'v': 10, 'E': 0.5}
        },
        'S3-A': {
            'path': 'results/S3-UAV-Speed/S3-A-v15',
            'label': 'S3-A: Moderate Speed (v=15 m/s)',
            'params': {'N': 100, 'P': 0.1, 'v': 15, 'E': 0.5}
        },
        'S3-B': {
            'path': 'results/S3-UAV-Speed/S3-B-v20',
            'label': 'S3-B: High Speed (v=20 m/s)',
            'params': {'N': 100, 'P': 0.1, 'v': 20, 'E': 0.5}
        },
        'S4-A': {
            'path': 'results/S4-Initial-Energy/S4-A-E10',
            'label': 'S4-A: Double Energy (E=1.0J)',
            'params': {'N': 100, 'P': 0.1, 'v': 10, 'E': 1.0}
        },
        'S4-B': {
            'path': 'results/S4-Initial-Energy/S4-B-E20',
            'label': 'S4-B: Quadruple Energy (E=2.0J)',
            'params': {'N': 100, 'P': 0.1, 'v': 10, 'E': 2.0}
        }
    }
    
    # Collect data
    results = []
    key_metrics = ['FND', 'LND', 'PDR', 'avg_delay', 'avg_CHs', 'avg_throughput']
    
    for scenario_id, info in scenarios.items():
        path = Path(info['path'])
        
        # Try to find metrics
        data_row = {'Scenario': scenario_id, 'Configuration': info['label']}
        
        # Try stability.csv first (has FND, LND)
        stability_file = path / 'stability.csv'
        stability_data = read_metrics(stability_file)
        if stability_data is not None:
            data_row['FND'] = f"{stability_data.get('FND', 0):.1f}s"
            data_row['LND'] = f"{stability_data.get('LND', 0):.1f}s"
        else:
            data_row['FND'] = 'N/A'
            data_row['LND'] = 'N/A'
        
        # PDR from pdr.csv
        pdr_file = path / 'pdr.csv'
        pdr_data = read_metrics(pdr_file)
        if pdr_data is not None:
            data_row['PDR'] = f"{pdr_data.get('PDR', 0):.2f}%"
        else:
            data_row['PDR'] = 'N/A'
        
        # Delay from delay.csv
        delay_file = path / 'delay.csv'
        delay_data = read_metrics(delay_file)
        if delay_data is not None:
            data_row['Avg_Delay'] = f"{delay_data.get('avg_delay', 0):.2f}s"
        else:
            data_row['Avg_Delay'] = 'N/A'
        
        # CHs from clustering.csv
        cluster_file = path / 'clustering.csv'
        cluster_data = read_metrics(cluster_file)
        if cluster_data is not None:
            data_row['Avg_CHs'] = f"{cluster_data.get('num_clusters', 0):.1f}"
        else:
            data_row['Avg_CHs'] = 'N/A'
        
        # Throughput from throughput.csv
        throughput_file = path / 'throughput.csv'
        throughput_data = read_metrics(throughput_file)
        if throughput_data is not None:
            data_row['Throughput'] = f"{throughput_data.get('throughput', 0):.2f} pkt/s"
        else:
            data_row['Throughput'] = 'N/A'
        
        results.append(data_row)
        
        if stability_data is not None:
            print(f"✓ Loaded: {scenario_id}")
        else:
            print(f"✗ Missing: {scenario_id}")
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    output_file = 'results/scenario_comparison.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved comparison table: {output_file}")
    
    # Print formatted table
    print("\n" + "="*120)
    print("PARAMETRIC SCENARIO COMPARISON TABLE")
    print("="*120)
    print(df.to_string(index=False))
    print("="*120)
    
    # Save formatted text version
    with open('results/scenario_comparison.txt', 'w') as f:
        f.write("="*120 + "\n")
        f.write("UAV-WSN PARAMETRIC SCENARIO COMPARISON\n")
        f.write("="*120 + "\n\n")
        f.write("Baseline: 30 runs with statistical validation (seed 1-30)\n")
        f.write("Scenarios: Single run each with consistent seed=1\n\n")
        f.write(df.to_string(index=False))
        f.write("\n\n" + "="*120 + "\n")
    
    print(f"✓ Saved formatted table: results/scenario_comparison.txt\n")

if __name__ == "__main__":
    main()
