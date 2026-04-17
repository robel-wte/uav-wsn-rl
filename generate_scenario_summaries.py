#!/usr/bin/env python3
"""Generate summary metrics for single-run parametric scenarios."""

import pandas as pd
import os
import sys

def calculate_metrics(scenario_dir, scenario_name):
    """Calculate metrics from a scenario directory."""
    
    try:
        # Network lifetime metrics
        network_df = pd.read_csv(f'{scenario_dir}/network.csv', on_bad_lines='skip')
        network_df = network_df.dropna(subset=['Round'])  # Drop rows with NaN Round values
        fnd_row = network_df[network_df['AliveNodes'] < 100]
        
        if not fnd_row.empty:
            fnd = int(fnd_row.iloc[0]['Round'])
        else:
            fnd = -1
        
        lnd_row = network_df[network_df['AliveNodes'] == 0]
        if not lnd_row.empty:
            lnd = int(lnd_row.iloc[0]['Round'])
        else:
            # Simulation ended before all nodes died
            lnd = int(network_df['Round'].max())
        
        lifetime = lnd - fnd if fnd > 0 else lnd
        
        hna_df = network_df[network_df['AliveNodes'] <= 50]
        hna = int(hna_df.iloc[0]['Round']) if not hna_df.empty else lnd
        
        # Energy metrics
        energy_df = pd.read_csv(f'{scenario_dir}/energy.csv', on_bad_lines='skip')
        total_energy = energy_df['EnergyConsumed'].sum()
        mean_energy = energy_df['EnergyConsumed'].mean()
        
        # PDR metrics
        pdr_df = pd.read_csv(f'{scenario_dir}/pdr.csv', on_bad_lines='skip')
        mean_pdr = pdr_df['PDR'].mean()
        
        # Throughput metrics
        throughput_df = pd.read_csv(f'{scenario_dir}/throughput.csv', on_bad_lines='skip')
        mean_throughput = throughput_df['Throughput_kbps'].mean()
        
        # Delay metrics
        try:
            delay_df = pd.read_csv(f'{scenario_dir}/delay.csv', on_bad_lines='skip')
            if 'Delay_s' in delay_df.columns:
                mean_delay = delay_df['Delay_s'].mean() * 1000  # Convert to ms
            elif 'Delay_ms' in delay_df.columns:
                mean_delay = delay_df['Delay_ms'].mean()
            else:
                mean_delay = delay_df['Delay'].mean()
        except Exception as e:
            print(f"  Warning: Could not parse delay.csv: {e}")
            mean_delay = 0
        
        # Overhead metrics
        try:
            overhead_df = pd.read_csv(f'{scenario_dir}/overhead.csv', on_bad_lines='skip')
            if 'OverheadRatio' in overhead_df.columns:
                mean_overhead = overhead_df['OverheadRatio'].mean()
            else:
                mean_overhead = overhead_df['Overhead'].mean()
        except Exception as e:
            print(f"  Warning: Could not parse overhead.csv: {e}")
            mean_overhead = 0
        
        # Create summary output
        summary = f"""Scenario: {scenario_name}
====================

Network Lifetime:
-----------------
FND (First Node Death): {fnd} rounds
LND (Last Node Death): {lnd} rounds
HNA (Half Nodes Alive): {hna} rounds
Lifetime (LND-FND): {lifetime} rounds

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
        
        # Write to summary.txt
        output_file = f'{scenario_dir}/summary.txt'
        with open(output_file, 'w') as f:
            f.write(summary)
        
        print(f"✓ {scenario_name} metrics extracted")
        return True
        
    except Exception as e:
        print(f"✗ Error with {scenario_name}: {e}")
        return False

if __name__ == '__main__':
    scenarios = [
        ('results/scenarios/S1-A-P005', 'S1-A (P=0.05)'),
        ('results/scenarios/S1-B-P02', 'S1-B (P=0.2)'),
        ('results/scenarios/S2-A-N200', 'S2-A (N=200)'),
        ('results/scenarios/S2-B-N300', 'S2-B (N=300)'),
        ('results/scenarios/S3-A-V15', 'S3-A (v=15 m/s)'),
        ('results/scenarios/S3-B-V20', 'S3-B (v=20 m/s)'),
        ('results/scenarios/S4-A-E10', 'S4-A (E=1.0 J)'),
        ('results/scenarios/S4-B-E20', 'S4-B (E=2.0 J)'),
    ]
    
    success_count = 0
    for scenario_dir, scenario_name in scenarios:
        if os.path.exists(scenario_dir) and os.path.exists(f'{scenario_dir}/network.csv'):
            if calculate_metrics(scenario_dir, scenario_name):
                success_count += 1
        else:
            print(f"✗ {scenario_name}: Directory or CSV files not found")
    
    print(f"\n{success_count}/{len(scenarios)} scenarios processed successfully")
