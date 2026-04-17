#!/usr/bin/env python3
"""
Generate individual metric plots for each parametric scenario.
Similar to generate_plots.py but for single-run scenario data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Configure matplotlib to handle complex trajectories
plt.rcParams['agg.path.chunksize'] = 10000
plt.rcParams['path.simplify'] = True
plt.rcParams['path.simplify_threshold'] = 0.5

def plot_scenario_metrics(scenario_dir, scenario_name, output_dir):
    """Generate all metric plots for a single scenario."""
    
    print(f"\nGenerating plots for {scenario_name}...")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 1. Network Lifetime Plot (Alive Nodes over Time)
        network_df = pd.read_csv(f'{scenario_dir}/network.csv', on_bad_lines='skip')
        network_df = network_df.dropna(subset=['Round'])
        
        plt.figure(figsize=(10, 6))
        plt.plot(network_df['Round'], network_df['AliveNodes'], 'b-', linewidth=2)
        plt.xlabel('Round', fontweight='bold', fontsize=12)
        plt.ylabel('Number of Alive Nodes', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Network Lifetime', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.ylim([0, max(network_df['AliveNodes']) * 1.1])
        
        # Mark FND and LND
        fnd_row = network_df[network_df['AliveNodes'] < network_df['AliveNodes'].iloc[0]]
        if not fnd_row.empty:
            fnd = fnd_row.iloc[0]['Round']
            plt.axvline(x=fnd, color='r', linestyle='--', label=f'FND={int(fnd)}')
        
        lnd_row = network_df[network_df['AliveNodes'] == 0]
        if not lnd_row.empty:
            lnd = lnd_row.iloc[0]['Round']
            plt.axvline(x=lnd, color='k', linestyle='--', label=f'LND={int(lnd)}')
        
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{output_dir}/network_lifetime.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ network_lifetime.png")
        
        # 2. Energy Consumption Plot
        energy_df = pd.read_csv(f'{scenario_dir}/energy.csv', on_bad_lines='skip')
        
        plt.figure(figsize=(10, 6))
        plt.plot(energy_df['Round'], energy_df['EnergyConsumed'], 'g-', linewidth=2)
        plt.xlabel('Round', fontweight='bold', fontsize=12)
        plt.ylabel('Energy Consumed (J)', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Energy Consumption per Round', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/energy_consumption.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ energy_consumption.png")
        
        # 3. PDR Plot
        pdr_df = pd.read_csv(f'{scenario_dir}/pdr.csv', on_bad_lines='skip')
        
        plt.figure(figsize=(10, 6))
        plt.plot(pdr_df['Round'], pdr_df['PDR'], 'purple', linewidth=2)
        plt.xlabel('Round', fontweight='bold', fontsize=12)
        plt.ylabel('Packet Delivery Ratio', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Packet Delivery Ratio', fontweight='bold', fontsize=14)
        plt.ylim([0, 1])
        plt.grid(True, alpha=0.3)
        plt.axhline(y=pdr_df['PDR'].mean(), color='r', linestyle='--', 
                    label=f'Mean={pdr_df["PDR"].mean():.3f}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{output_dir}/pdr.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ pdr.png")
        
        # 4. Throughput Plot
        throughput_df = pd.read_csv(f'{scenario_dir}/throughput.csv', on_bad_lines='skip')
        
        plt.figure(figsize=(10, 6))
        plt.plot(throughput_df['Time'], throughput_df['Throughput_kbps'], 'orange', linewidth=1.5)
        plt.xlabel('Time (s)', fontweight='bold', fontsize=12)
        plt.ylabel('Throughput (kbps)', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Network Throughput', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/throughput.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ throughput.png")
        
        # 5. Delay Plot
        delay_df = pd.read_csv(f'{scenario_dir}/delay.csv', on_bad_lines='skip')
        
        # Sample for visualization if too many points
        if len(delay_df) > 5000:
            delay_df = delay_df.sample(5000, random_state=1)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(delay_df['ReceptionTime'], delay_df['Delay_s'], alpha=0.3, s=10, color='teal')
        plt.xlabel('Reception Time (s)', fontweight='bold', fontsize=12)
        plt.ylabel('Delay (s)', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Packet Delay', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/delay.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ delay.png")
        
        # 6. Clustering Plot
        clustering_df = pd.read_csv(f'{scenario_dir}/clustering.csv', on_bad_lines='skip')
        # Group by round to get unique cluster counts per round
        clusters_per_round = clustering_df.groupby('Round')['TotalClusters'].first()
        
        plt.figure(figsize=(10, 6))
        plt.plot(clusters_per_round.index, clusters_per_round.values, 'brown', linewidth=2)
        plt.xlabel('Round', fontweight='bold', fontsize=12)
        plt.ylabel('Number of Cluster Heads', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Cluster Heads per Round', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.axhline(y=clusters_per_round.mean(), color='r', linestyle='--',
                    label=f'Mean={clusters_per_round.mean():.2f}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{output_dir}/clustering.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ clustering.png")
        
        # 7. Overhead Plot
        overhead_df = pd.read_csv(f'{scenario_dir}/overhead.csv', on_bad_lines='skip')
        
        plt.figure(figsize=(10, 6))
        plt.plot(overhead_df['Round'], overhead_df['OverheadRatio'], 'red', linewidth=2)
        plt.xlabel('Round', fontweight='bold', fontsize=12)
        plt.ylabel('Overhead Ratio', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: Network Overhead', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/overhead.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ overhead.png")
        
        # 8. UAV Trajectory Plot
        traj_df = pd.read_csv(f'{scenario_dir}/uav_trajectory.csv', on_bad_lines='skip')
        
        # Downsample trajectory if it has too many points
        if len(traj_df) > 5000:
            step = len(traj_df) // 5000
            traj_df = traj_df.iloc[::step].reset_index(drop=True)
        
        plt.figure(figsize=(10, 10))
        plt.plot(traj_df['X'], traj_df['Y'], 'b-', linewidth=1, alpha=0.6)
        plt.scatter(traj_df['X'].iloc[0], traj_df['Y'].iloc[0], 
                   s=200, c='green', marker='o', label='Start', zorder=5)
        plt.scatter(traj_df['X'].iloc[-1], traj_df['Y'].iloc[-1], 
                   s=200, c='red', marker='X', label='End', zorder=5)
        plt.xlabel('X Coordinate (m)', fontweight='bold', fontsize=12)
        plt.ylabel('Y Coordinate (m)', fontweight='bold', fontsize=12)
        plt.title(f'{scenario_name}: UAV Trajectory', fontweight='bold', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/uav_trajectory.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ uav_trajectory.png")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error generating plots: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    scenarios = [
        ('results/scenarios/S1-A-P005', 'S1-A (P=0.05)', 'plots/scenarios/S1-A'),
        ('results/scenarios/S1-B-P02', 'S1-B (P=0.2)', 'plots/scenarios/S1-B'),
        ('results/scenarios/S2-A-N200', 'S2-A (N=200)', 'plots/scenarios/S2-A'),
        ('results/scenarios/S2-B-N300', 'S2-B (N=300)', 'plots/scenarios/S2-B'),
        ('results/scenarios/S3-A-V15', 'S3-A (v=15 m/s)', 'plots/scenarios/S3-A'),
        ('results/scenarios/S3-B-V20', 'S3-B (v=20 m/s)', 'plots/scenarios/S3-B'),
        ('results/scenarios/S4-A-E10', 'S4-A (E=1.0 J)', 'plots/scenarios/S4-A'),
        ('results/scenarios/S4-B-E20', 'S4-B (E=2.0 J)', 'plots/scenarios/S4-B'),
        ('results/scenarios/S5-A', 'S5-A (Hybrid)', 'plots/scenarios/S5-A'),
        ('results/scenarios/S5-B', 'S5-B (Hybrid)', 'plots/scenarios/S5-B'),
    ]
    
    success_count = 0
    for scenario_dir, scenario_name, output_dir in scenarios:
        if os.path.exists(scenario_dir) and os.path.exists(f'{scenario_dir}/network.csv'):
            if plot_scenario_metrics(scenario_dir, scenario_name, output_dir):
                success_count += 1
        else:
            print(f"\n✗ {scenario_name}: Directory or data files not found")
    
    print(f"\n{'='*60}")
    print(f"Plot generation complete: {success_count}/{len(scenarios)} scenarios")
    print(f"{'='*60}")
    
    if success_count > 0:
        print("\nGenerated plots:")
        for scenario_dir, scenario_name, output_dir in scenarios:
            if os.path.exists(output_dir):
                print(f"  {output_dir}/")

if __name__ == '__main__':
    main()
