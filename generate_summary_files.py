#!/usr/bin/env python3
"""
Generate summary.txt files for all scenarios.
Extracts key metrics like FND, LND, energy, and performance.
"""

import pandas as pd
import os
from pathlib import Path

def generate_summary(scenario_dir, scenario_name):
    """Generate summary.txt for a scenario"""
    
    # Read CSV files
    stability_file = os.path.join(scenario_dir, 'stability.csv')
    energy_file = os.path.join(scenario_dir, 'energy.csv')
    pdr_file = os.path.join(scenario_dir, 'pdr.csv')
    throughput_file = os.path.join(scenario_dir, 'throughput.csv')
    delay_file = os.path.join(scenario_dir, 'delay.csv')
    overhead_file = os.path.join(scenario_dir, 'overhead.csv')
    
    # Read data
    stability_data = pd.read_csv(stability_file)
    energy_data = pd.read_csv(energy_file)
    pdr_data = pd.read_csv(pdr_file)
    throughput_data = pd.read_csv(throughput_file)
    delay_data = pd.read_csv(delay_file)
    overhead_data = pd.read_csv(overhead_file)
    
    # Calculate FND and LND
    last_row = stability_data.iloc[-1]
    last_round = int(last_row['Round'])
    
    # Find FND (first round where a node dies)
    dead_nodes_per_round = stability_data[stability_data['DeadNodes'] > 0]
    if len(dead_nodes_per_round) > 0:
        fnd_round = int(dead_nodes_per_round.iloc[0]['Round'])
    else:
        fnd_round = last_round
    
    # LND is the last round where we have data (or when all nodes are dead)
    lnd_round = last_round
    
    # Find HNA (half nodes alive)
    hna_round = None
    for idx, row in stability_data.iterrows():
        if row['AliveNodes'] <= 50:
            hna_round = int(row['Round'])
            break
    if hna_round is None:
        hna_round = lnd_round
    
    # Extract metrics
    total_energy = energy_data['EnergyConsumed'].sum()
    mean_energy = energy_data['EnergyConsumed'].mean()
    mean_pdr = pdr_data['PDR'].mean()
    mean_throughput = throughput_data['Throughput_kbps'].mean()
    mean_delay = delay_data['Delay_s'].mean() * 1000.0
    mean_overhead = overhead_data['OverheadRatio'].mean()
    
    # Generate summary text
    summary_text = f"""Scenario: {scenario_name}
====================

Network Lifetime:
-----------------
FND (First Node Death): {fnd_round} rounds
LND (Last Node Death): {lnd_round} rounds
HNA (Half Nodes Alive): {hna_round} rounds
Lifetime (LND-FND): {lnd_round - fnd_round} rounds

Energy:
-------
Total Energy Consumed: {total_energy:.4f} J
Mean Energy Per Round: {mean_energy:.6f} J

Performance:
------------
Mean PDR: {mean_pdr:.4f}
Mean Throughput: {mean_throughput:.4f} kbps
Mean Delay: {mean_delay:.4f} ms
Mean Overhead Ratio: {mean_overhead:.4f}

"""
    
    # Write summary file
    summary_file = os.path.join(scenario_dir, 'summary.txt')
    with open(summary_file, 'w') as f:
        f.write(summary_text)
    
    return {
        'scenario': scenario_name,
        'fnd': fnd_round,
        'lnd': lnd_round,
        'hna': hna_round,
        'lifetime': lnd_round - fnd_round,
        'total_energy': total_energy,
        'mean_pdr': mean_pdr,
        'mean_throughput': mean_throughput,
        'mean_delay': mean_delay,
        'mean_overhead': mean_overhead
    }

def main():
    base_dir = '/workspaces/uav-wsn-bm/results/scenarios'
    
    # Get all scenario directories
    scenarios = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    
    results = []
    for scenario_dir_name in scenarios:
        scenario_path = os.path.join(base_dir, scenario_dir_name)
        
        # Check if summary already exists
        summary_file = os.path.join(scenario_path, 'summary.txt')
        
        print(f"Processing {scenario_dir_name}...", end=" ")
        
        try:
            metrics = generate_summary(scenario_path, scenario_dir_name)
            results.append(metrics)
            print(f"✓ (LND={metrics['lnd']} rounds)")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Print summary table
    print("\n" + "="*100)
    print("SUMMARY: All Scenarios")
    print("="*100)
    print(f"{'Scenario':<20} {'FND':<10} {'LND':<10} {'HNA':<10} {'Lifetime':<10} {'Mean PDR':<10} {'Mean Delay':<15}")
    print("-"*100)
    for r in results:
        print(f"{r['scenario']:<20} {r['fnd']:<10} {r['lnd']:<10} {r['hna']:<10} {r['lifetime']:<10} {r['mean_pdr']:<10.4f} {r['mean_delay']:<15.2f}")

if __name__ == '__main__':
    main()
