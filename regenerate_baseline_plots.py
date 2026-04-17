#!/usr/bin/env python3
"""
Regenerate S0-Baseline plots based on multi-run data (30 runs).
Computes mean and std dev across all runs and generates plots with statistics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from pathlib import Path

# Set style for publication-quality plots (matching standard format)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 16
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 14
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['grid.color'] = '#d0d0d0'
plt.rcParams['grid.alpha'] = 0.5
plt.rcParams['grid.linewidth'] = 1.2
plt.rcParams['axes.linewidth'] = 1.8
plt.rcParams['axes.edgecolor'] = '#2d2d2d'

def load_multirun_data(metric_name, runs_dir='results/multi-run'):
    """Load and aggregate metric data from all runs."""
    
    all_data = []
    run_dirs = sorted([d for d in glob.glob(f'{runs_dir}/run-*') if os.path.isdir(d)])
    
    for run_dir in run_dirs:
        csv_file = f'{run_dir}/{metric_name}.csv'
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file, on_bad_lines='skip')
                df['run_id'] = int(os.path.basename(run_dir).split('-')[1])
                all_data.append(df)
            except Exception as e:
                print(f"  ⚠️  Error reading {csv_file}: {e}")
    
    return all_data

def aggregate_by_round(dfs, value_col, round_col='Round', group_by='Round'):
    """Aggregate data from multiple runs by computing mean and std."""
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Group by round and compute statistics
    grouped = combined.groupby(group_by)[value_col].agg(['mean', 'std', 'min', 'max', 'count'])
    grouped = grouped.reset_index()
    
    return grouped

def generate_network_lifetime_plot(output_dir):
    """Generate network lifetime plot with mean and confidence band."""
    
    print("\n  Generating network_lifetime.png...")
    
    # Load network data from all runs
    dfs = load_multirun_data('network')
    
    if not dfs:
        print("    ✗ No network data found")
        return False
    
    # Calculate FND and LND for each run, then take the mean
    fnd_values = []
    lnd_values = []
    
    for df in dfs:
        initial_nodes = df['AliveNodes'].iloc[0]
        
        # FND: First round where alive nodes < initial nodes
        fnd_row = df[df['AliveNodes'] < initial_nodes]
        if not fnd_row.empty:
            fnd_values.append(fnd_row.iloc[0]['Round'])
        
        # LND: First round where alive nodes == 0
        lnd_row = df[df['AliveNodes'] == 0]
        if not lnd_row.empty:
            lnd_values.append(lnd_row.iloc[0]['Round'])
    
    mean_fnd = np.mean(fnd_values) if fnd_values else None
    mean_lnd = np.mean(lnd_values) if lnd_values else None
    
    # Aggregate by round
    stats = aggregate_by_round(dfs, 'AliveNodes', round_col='Round')
    
    # Calculate dead nodes (assuming 100 total nodes)
    total_nodes = 100
    stats['dead_mean'] = total_nodes - stats['mean']
    stats['dead_std'] = stats['std']  # Same std dev as alive nodes
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot mean alive nodes
    ax.plot(stats['Round'], stats['mean'], 'b-', linewidth=2.5, label='Mean Alive Nodes')
    
    # Plot mean dead nodes
    ax.plot(stats['Round'], stats['dead_mean'], 'r-', linewidth=2.5, label='Mean Dead Nodes')
    
    # Mark FND and LND with the correct mean values
    if mean_fnd:
        ax.axvline(x=mean_fnd, color='orange', linestyle='--', linewidth=2.0, label=f'FND={int(mean_fnd)}')
    
    if mean_lnd:
        ax.axvline(x=mean_lnd, color='k', linestyle='--', linewidth=2.0, label=f'LND={int(mean_lnd)}')
    
    ax.set_xlabel('Round', fontweight='bold')
    ax.set_ylabel('Number of Nodes', fontweight='bold')
    ax.set_title('S0-Baseline: Network Lifetime - Alive and Dead Nodes')
    ax.grid(True)
    ax.legend(loc='best')
    ax.set_xlim([0, 1200])
    ax.set_ylim([0, total_nodes * 1.05])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/network_lifetime.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ network_lifetime.png")
    return True

def generate_energy_plots(output_dir):
    """Generate energy consumption plots."""
    
    print("\n  Generating energy plots...")
    
    # Load energy data from all runs
    dfs = load_multirun_data('energy')
    
    if not dfs:
        print("    ✗ No energy data found")
        return False
    
    # Aggregate by round
    stats = aggregate_by_round(dfs, 'EnergyConsumed', round_col='Round')
    
    # Energy consumption per round
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stats['Round'], stats['mean'], 'g-', linewidth=2.5, label='Mean Energy')
    
    ax.set_xlabel('Round', fontweight='bold')
    ax.set_ylabel('Energy Consumed (J)', fontweight='bold')
    ax.set_title('S0-Baseline: Energy Consumption per Round')
    ax.grid(True)
    ax.legend(loc='best')
    ax.set_xlim([0, 1200])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/energy_consumption.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ energy_consumption.png")
    
    # Cumulative energy consumption
    combined = pd.concat(dfs, ignore_index=True)
    cumulative_stats = []
    
    for run_id in combined['run_id'].unique():
        run_data = combined[combined['run_id'] == run_id].sort_values('Round')
        run_data['CumulativeEnergy'] = run_data['EnergyConsumed'].cumsum()
        cumulative_stats.append(run_data[['Round', 'CumulativeEnergy']])
    
    cumulative_df = pd.concat(cumulative_stats, ignore_index=True)
    cumulative_agg = cumulative_df.groupby('Round')['CumulativeEnergy'].agg(['mean', 'std'])
    cumulative_agg = cumulative_agg.reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(cumulative_agg['Round'], cumulative_agg['mean'], 'darkgreen', linewidth=2.5, label='Mean Cumulative Energy')
    
    ax.set_xlabel('Round', fontweight='bold')
    ax.set_ylabel('Cumulative Energy Consumed (J)', fontweight='bold')
    ax.set_title('S0-Baseline: Cumulative Energy Consumption')
    ax.grid(True)
    ax.legend(loc='best')
    ax.set_xlim([0, 1200])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/total_energy_consumption_per_round.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ total_energy_consumption_per_round.png")
    
    return True

def generate_pdr_plot(output_dir):
    """Generate PDR plot."""
    
    print("\n  Generating pdr.png...")
    
    # Load PDR data from all runs
    dfs = load_multirun_data('pdr')
    
    if not dfs:
        print("    ✗ No PDR data found")
        return False
    
    # Aggregate by round
    stats = aggregate_by_round(dfs, 'PDR', round_col='Round')
    
    # Calculate true mean PDR (mean of per-run means, not mean of per-round means)
    combined = pd.concat(dfs, ignore_index=True)
    mean_pdr_per_run = combined.groupby('run_id')['PDR'].mean()
    true_mean_pdr = mean_pdr_per_run.mean()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(stats['Round'], stats['mean'], 'purple', linewidth=2.5, label='Mean PDR')
    
    ax.set_xlabel('Round', fontweight='bold')
    ax.set_ylabel('Packet Delivery Ratio', fontweight='bold')
    ax.set_title('S0-Baseline: Packet Delivery Ratio')
    ax.set_ylim([0, 1])
    ax.grid(True)
    ax.axhline(y=true_mean_pdr, color='r', linestyle='--', linewidth=2.0,
              label=f'Overall Mean={true_mean_pdr:.4f}')
    ax.legend(loc='best')
    ax.set_xlim([0, 1200])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/pdr.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ pdr.png")
    return True

def generate_throughput_plot(output_dir):
    """Generate throughput plot."""
    
    print("\n  Generating throughput.png...")
    
    # Load throughput data from all runs
    dfs = load_multirun_data('throughput')
    
    if not dfs:
        print("    ✗ No throughput data found")
        return False
    
    # Normalize time for aggregation
    combined = pd.concat(dfs, ignore_index=True)
    
    # Create time bins for aggregation (every 10 seconds)
    combined['TimeBin'] = (combined['Time'] / 10).astype(int) * 10
    
    stats = combined.groupby('TimeBin')['Throughput_bps'].agg(['mean', 'std', 'count'])
    stats = stats.reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(stats.index, stats['mean'], 'orange', linewidth=2.5, label='Mean Throughput')
    
    ax.set_xlabel('Time (s)', fontweight='bold')
    ax.set_ylabel('Throughput (bps)', fontweight='bold')
    ax.set_title('S0-Baseline: Network Throughput')
    ax.grid(True)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ throughput.png")
    return True

def generate_delay_plot(output_dir):
    """Generate delay distribution plot."""
    
    print("\n  Generating delay plots...")
    
    # Load delay data from all runs
    dfs = load_multirun_data('delay')
    
    if not dfs:
        print("    ✗ No delay data found")
        return False
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Calculate true mean and median (per-run means, then average)
    mean_delay_per_run = combined.groupby('run_id')['Delay_s'].mean()
    median_delay_per_run = combined.groupby('run_id')['Delay_s'].median()
    true_mean_delay = mean_delay_per_run.mean()
    true_median_delay = median_delay_per_run.mean()
    
    # Delay distribution histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(combined['Delay_s'], bins=100, color='teal', alpha=0.7, edgecolor='black', linewidth=1.2)
    ax.axvline(x=true_mean_delay, color='r', linestyle='--', linewidth=2.5,
              label=f'Mean={true_mean_delay:.2f}s')
    ax.axvline(x=true_median_delay, color='orange', linestyle='--', linewidth=2.5,
              label=f'Median={true_median_delay:.2f}s')
    
    ax.set_xlabel('Delay (s)', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('S0-Baseline: Packet Delay Distribution')
    ax.grid(True, axis='y')
    ax.legend(loc='best')
    ax.set_xlim([0, 5000])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/delay_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ delay_distribution.png")
    
    # Average delay per round
    # Calculate round from ReceptionTime (round duration = 774 seconds)
    combined['Round'] = (combined['ReceptionTime'] / 774).apply(np.ceil).astype(int)
    
    if not combined.empty:
        delay_by_round = combined.groupby('Round')['Delay_s'].agg(['mean', 'std', 'median', 'count'])
        delay_by_round = delay_by_round.reset_index()
        
        # Filter to rounds with sufficient data
        delay_by_round = delay_by_round[delay_by_round['count'] >= 10]
        
        if not delay_by_round.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.plot(delay_by_round['Round'], delay_by_round['mean'], 'teal', linewidth=2.5, label='Mean Delay')
            
            ax.set_xlabel('Round', fontweight='bold')
            ax.set_ylabel('Delay (s)', fontweight='bold')
            ax.set_title('S0-Baseline: Average Delay per Round')
            ax.grid(True)
            ax.legend(loc='best')
            ax.set_xlim([0, 1200])
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/average_delay_per_round.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("    ✓ average_delay_per_round.png")
    
    return True

def generate_clustering_plot(output_dir):
    """Generate clustering metrics plot."""
    
    print("\n  Generating clustering_metrics.png...")
    
    # Load clustering data from all runs
    dfs = load_multirun_data('clustering')
    
    if not dfs:
        print("    ✗ No clustering data found")
        return False
    
    # Aggregate by round - count unique cluster heads per round
    combined = pd.concat(dfs, ignore_index=True)
    
    ch_per_round = combined.groupby(['Round', 'run_id'])['ClusterID'].count().reset_index()
    ch_stats = ch_per_round.groupby('Round')['ClusterID'].agg(['mean', 'std'])
    ch_stats = ch_stats.reset_index()
    
    # Calculate true mean CHs (mean of per-run means)
    mean_chs_per_run = ch_per_round.groupby('run_id')['ClusterID'].mean()
    true_mean_chs = mean_chs_per_run.mean()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(ch_stats['Round'], ch_stats['mean'], 'brown', linewidth=2.5, label='Mean Cluster Heads')
    
    ax.set_xlabel('Round', fontweight='bold')
    ax.set_ylabel('Number of Cluster Heads', fontweight='bold')
    ax.set_title('S0-Baseline: Clustering Metrics')
    ax.grid(True)
    ax.axhline(y=true_mean_chs, color='r', linestyle='--', linewidth=2.0,
              label=f'Overall Mean={true_mean_chs:.2f}')
    ax.legend(loc='best')
    ax.set_xlim([0, 1200])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/clustering_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ clustering_metrics.png")
    return True

def generate_overhead_plot(output_dir):
    """Generate control overhead plot."""
    
    print("\n  Generating control_overhead.png...")
    
    # Load overhead data from all runs
    dfs = load_multirun_data('overhead')
    
    if not dfs:
        print("    ✗ No overhead data found")
        return False
    
    # Aggregate by round
    stats = aggregate_by_round(dfs, 'ControlRatio', round_col='Round')
    
    # Calculate true mean control ratio (mean of per-run means)
    combined = pd.concat(dfs, ignore_index=True)
    mean_control_per_run = combined.groupby('run_id')['ControlRatio'].mean()
    true_mean_control = mean_control_per_run.mean()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(stats['Round'], stats['mean'], 'red', linewidth=2.5, label='Mean Control Ratio')
    
    ax.set_xlabel('Round', fontweight='bold')
    ax.set_ylabel('Control Ratio', fontweight='bold')
    ax.set_title('S0-Baseline: Control Overhead')
    ax.grid(True)
    ax.axhline(y=true_mean_control, color='darkred', linestyle='--', linewidth=2.0,
              label=f'Overall Mean={true_mean_control:.4f}')
    ax.legend(loc='best')
    ax.set_xlim([0, 1200])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/control_overhead.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("    ✓ control_overhead.png")
    return True

def regenerate_baseline_plots():
    """Regenerate all S0-Baseline plots from multi-run data."""
    
    output_dir = 'plots/scenarios/S0-Baseline'
    
    print("=" * 70)
    print("  Regenerating S0-Baseline Plots from Multi-Run Data")
    print("=" * 70)
    print(f"\nInput: results/multi-run/ (30 runs)")
    print(f"Output: {output_dir}/")
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_success = True
    
    # Generate each plot
    all_success &= generate_network_lifetime_plot(output_dir)
    all_success &= generate_energy_plots(output_dir)
    all_success &= generate_pdr_plot(output_dir)
    all_success &= generate_throughput_plot(output_dir)
    all_success &= generate_delay_plot(output_dir)
    all_success &= generate_clustering_plot(output_dir)
    all_success &= generate_overhead_plot(output_dir)
    
    print("\n" + "=" * 70)
    if all_success:
        print("✓ All plots regenerated successfully!")
    else:
        print("⚠️  Some plots may have failed - check messages above")
    print("=" * 70)
    
    return all_success

if __name__ == '__main__':
    success = regenerate_baseline_plots()
    exit(0 if success else 1)
