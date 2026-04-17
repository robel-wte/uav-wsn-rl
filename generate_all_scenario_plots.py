#!/usr/bin/env python3
"""
Generate professional plots for all parametric scenarios S1-S5
Based on successful S0-Baseline plotting approach
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Professional plot styling (matching generate_baseline_plots.py)
plt.style.use('seaborn-v0_8-whitegrid')

# Professional color palette
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#F18F01',
    'success': '#06A77D',
    'danger': '#C73E1D',
    'accent': '#A23B72',
    'neutral': '#4A4A4A'
}

SCENARIOS = {
    'S1-A': {'name': 'S1-A: P=0.05', 'desc': 'CH Probability 0.05'},
    'S1-B': {'name': 'S1-B: P=0.2', 'desc': 'CH Probability 0.2'},
    'S2-A': {'name': 'S2-A: N=200', 'desc': 'Node Density 200'},
    'S2-B': {'name': 'S2-B: N=300', 'desc': 'Node Density 300'},
    'S3-A': {'name': 'S3-A: v=15 m/s', 'desc': 'UAV Speed 15 m/s'},
    'S3-B': {'name': 'S3-B: v=20 m/s', 'desc': 'UAV Speed 20 m/s'},
    'S4-A': {'name': 'S4-A: E=1.0J', 'desc': 'Initial Energy 1.0J'},
    'S4-B': {'name': 'S4-B: E=2.0J', 'desc': 'Initial Energy 2.0J'},
    'S5-A': {'name': 'S5-A: Size=500b', 'desc': 'Packet Size 500 bits'},
    'S5-B': {'name': 'S5-B: Size=4000b', 'desc': 'Packet Size 4000 bits'},
}


def plot_network_lifetime(scenario, data_dir, output_dir, metrics):
    """Plot network lifetime (Alive + Dead nodes) with FND/LND markers"""
    # Try different CSV names
    csv_file = data_dir / 'stability.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    fnd = metrics.get('FND', None)
    lnd = metrics.get('LND', None)
    
    # Filter to LND if available
    if lnd and lnd > 0:
        plot_df = df[df['Round'] <= lnd].copy()
    else:
        plot_df = df.copy()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot Alive Nodes
    ax.plot(plot_df['Round'], plot_df['AliveNodes'], 
            linewidth=2.5, color=COLORS['primary'], label='Alive Nodes')
    
    # Plot Dead Nodes (complementary)
    ax.plot(plot_df['Round'], plot_df['DeadNodes'],
            linewidth=2.2, color=COLORS['accent'], linestyle='--', label='Dead Nodes')
    
    # Mark FND
    if fnd and fnd > 0:
        ax.axvline(x=fnd, color=COLORS['danger'], linestyle='--', 
                   linewidth=2, alpha=0.7, label=f'FND (Round {fnd})')
    
    # Mark LND
    if lnd and lnd > 0:
        ax.axvline(x=lnd, color=COLORS['neutral'], linestyle=':', 
                   linewidth=2, alpha=0.7, label=f'LND (Round {lnd})')
        # Shade post-LND region
        ax.axvspan(lnd, plot_df['Round'].max(), alpha=0.1, color='gray')
    
    ax.set_xlabel('Round Number', fontsize=20, fontweight='bold')
    ax.set_ylabel('Number of Nodes', fontsize=20, fontweight='bold')
    ax.set_title(f'Network Lifetime - {SCENARIOS[scenario]["name"]}', 
                 fontsize=22, fontweight='bold', pad=20)
    ax.legend(fontsize=14, loc='best', framealpha=0.95)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=16)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'network_lifetime.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_energy_consumption(scenario, data_dir, output_dir):
    """Plot energy consumption (2-panel: Total + Average Residual)"""
    csv_file = data_dir / 'energy.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Panel 1: Total Energy Consumed
    ax1.plot(df['Round'], df['EnergyConsumed'], 
             linewidth=2.5, color=COLORS['danger'])
    ax1.set_ylabel('Total Energy (J)', fontsize=18, fontweight='bold')
    ax1.set_title(f'Energy Consumption - {SCENARIOS[scenario]["name"]}', 
                  fontsize=22, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(labelsize=14)
    
    # Panel 2: Average Residual Energy
    ax2.plot(df['Round'], df['AvgResidualEnergy'], 
             linewidth=2.5, color=COLORS['success'])
    ax2.set_xlabel('Round Number', fontsize=20, fontweight='bold')
    ax2.set_ylabel('Avg Residual (J)', fontsize=18, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(labelsize=14)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'energy_consumption.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_pdr(scenario, data_dir, output_dir):
    """Plot Packet Delivery Ratio (filtered for rounds with ≥5 packets)"""
    csv_file = data_dir / 'pdr.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    
    # Filter rounds with sufficient packets
    df_filtered = df[df['PacketsGenerated'] >= 5].copy()
    
    if len(df_filtered) == 0:
        print(f"  ⚠ Warning: No rounds with ≥5 packets for PDR")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.scatter(df_filtered['Round'], df_filtered['PDR'], 
               alpha=0.6, s=40, color=COLORS['primary'], label='Per-Round PDR')
    
    # Rolling mean
    if len(df_filtered) >= 20:
        window = 20
        df_filtered['PDR_MA'] = df_filtered['PDR'].rolling(window=window, center=True).mean()
        ax.plot(df_filtered['Round'], df_filtered['PDR_MA'], 
                linewidth=2.5, color=COLORS['secondary'], label=f'{window}-Round Moving Avg')
    
    ax.set_xlabel('Round Number', fontsize=20, fontweight='bold')
    ax.set_ylabel('Packet Delivery Ratio', fontsize=20, fontweight='bold')
    ax.set_title(f'Packet Delivery Ratio - {SCENARIOS[scenario]["name"]}', 
                 fontsize=22, fontweight='bold', pad=20)
    ax.legend(fontsize=14, loc='best')
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=16)
    ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'pdr.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_throughput(scenario, data_dir, output_dir, metrics):
    """Plot throughput with moving average"""
    csv_file = data_dir / 'throughput.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    
    # throughput.csv has Time column, not Round
    # Skip if not enough data
    if len(df) < 10:
        print(f"  ⚠ Warning: Insufficient data for throughput plot")
        return
    
    # Convert kbps if needed
    if 'Throughput_kbps' in df.columns:
        y_col = 'Throughput_kbps'
        y_label = 'Throughput (kbps)'
    else:
        y_col = 'Throughput_bps'
        y_label = 'Throughput (bps)'
        df['Throughput_kbps'] = df[y_col] / 1000
        y_col = 'Throughput_kbps'
        y_label = 'Throughput (kbps)'
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Raw throughput
    ax.plot(df.index, df[y_col], 
            linewidth=1.5, alpha=0.4, color=COLORS['primary'], label='Raw Throughput')
    
    # Moving average
    if len(df) >= 20:
        window = min(20, len(df) // 4)
        df['MA'] = df[y_col].rolling(window=window, center=True).mean()
        ax.plot(df.index, df['MA'], 
                linewidth=2.5, color=COLORS['secondary'], label=f'{window}-Point Moving Avg')
    
    ax.set_xlabel('Sample Index', fontsize=20, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=20, fontweight='bold')
    ax.set_title(f'Network Throughput - {SCENARIOS[scenario]["name"]}', 
                 fontsize=22, fontweight='bold', pad=20)
    ax.legend(fontsize=14, loc='best')
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=16)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'throughput.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_delay_distribution(scenario, data_dir, output_dir):
    """Plot delay distribution histogram"""
    csv_file = data_dir / 'delay.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    delays = df['Delay_s'].dropna()
    
    if len(delays) == 0:
        print(f"  ⚠ Warning: No delay data available")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.hist(delays, bins=50, color=COLORS['primary'], alpha=0.7, edgecolor='black')
    
    # Mark mean and median
    mean_delay = delays.mean()
    median_delay = delays.median()
    ax.axvline(mean_delay, color=COLORS['danger'], linestyle='--', 
               linewidth=2, label=f'Mean: {mean_delay:.2f}s')
    ax.axvline(median_delay, color=COLORS['success'], linestyle=':', 
               linewidth=2, label=f'Median: {median_delay:.2f}s')
    
    ax.set_xlabel('Delay (s)', fontsize=20, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=20, fontweight='bold')
    ax.set_title(f'Delay Distribution - {SCENARIOS[scenario]["name"]}', 
                 fontsize=22, fontweight='bold', pad=20)
    ax.legend(fontsize=14, loc='best')
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=16)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'delay_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_average_delay_per_round(scenario, data_dir, output_dir):
    """Plot average delay per round (aggregate per round)"""
    csv_file = data_dir / 'delay.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    
    # Group by generation time to get per-round aggregates
    if len(df) == 0:
        print(f"  ⚠ Warning: No delay data available")
        return
    
    # Create a per-time aggregation
    df_agg = df.groupby(df['GenerationTime'].astype(int) // 774).agg({
        'Delay_s': ['mean', 'count']
    }).reset_index()
    df_agg.columns = ['RoundGroup', 'AvgDelay', 'PacketCount']
    
    if len(df_agg) < 5:
        print(f"  ⚠ Warning: Insufficient data for per-round plots")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Panel 1: Average Delay
    ax1.plot(df_agg['RoundGroup'], df_agg['AvgDelay'], 
             linewidth=2, color=COLORS['primary'])
    ax1.set_ylabel('Avg Delay (s)', fontsize=18, fontweight='bold')
    ax1.set_title(f'Average Delay per Round - {SCENARIOS[scenario]["name"]}', 
                  fontsize=22, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(labelsize=14)
    
    # Panel 2: Packet Count
    ax2.plot(df_agg['RoundGroup'], df_agg['PacketCount'], 
             linewidth=2, color=COLORS['success'])
    ax2.set_xlabel('Round Group', fontsize=20, fontweight='bold')
    ax2.set_ylabel('Packets Delivered', fontsize=18, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(labelsize=14)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'average_delay_per_round.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_clustering_metrics(scenario, data_dir, output_dir):
    """Plot clustering metrics (2-panel: CHs + Unclustered %)"""
    csv_file = data_dir / 'clustering.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    
    if len(df) == 0:
        print(f"  ⚠ Warning: No clustering data available")
        return
    
    # Extract CHs count from ClusterID (each unique ClusterID is one CH)
    df_agg = df.groupby('Round').agg({
        'ClusterID': 'nunique',
        'MemberCount': 'sum'
    }).reset_index()
    df_agg.columns = ['Round', 'ClusterHeads', 'TotalMembers']
    
    # Calculate unclustered percentage
    total_nodes = 100  # Default baseline
    df_agg['UnclusteredNodes'] = total_nodes - df_agg['TotalMembers']
    df_agg['UnclusteredPercentage'] = (df_agg['UnclusteredNodes'] / total_nodes) * 100
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Panel 1: Cluster Heads
    ax1.plot(df_agg['Round'], df_agg['ClusterHeads'], 
             linewidth=2.5, color=COLORS['primary'])
    ax1.set_ylabel('Cluster Heads', fontsize=18, fontweight='bold')
    ax1.set_title(f'Clustering Metrics - {SCENARIOS[scenario]["name"]}', 
                  fontsize=22, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(labelsize=14)
    
    # Panel 2: Unclustered Percentage
    ax2.plot(df_agg['Round'], df_agg['UnclusteredPercentage'], 
             linewidth=2.5, color=COLORS['secondary'])
    ax2.set_xlabel('Round Number', fontsize=20, fontweight='bold')
    ax2.set_ylabel('Unclustered (%)', fontsize=18, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(labelsize=14)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'clustering_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_control_overhead(scenario, data_dir, output_dir):
    """Plot control overhead"""
    csv_file = data_dir / 'overhead.csv'
    if not csv_file.exists():
        print(f"  ⚠ Warning: {csv_file} not found")
        return
    
    df = pd.read_csv(csv_file)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(df['Round'], df['OverheadRatio'], 
            linewidth=2.5, color=COLORS['secondary'])
    
    ax.set_xlabel('Round Number', fontsize=20, fontweight='bold')
    ax.set_ylabel('Control Overhead Ratio', fontsize=20, fontweight='bold')
    ax.set_title(f'Control Overhead - {SCENARIOS[scenario]["name"]}', 
                 fontsize=22, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=16)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'control_overhead.png', dpi=300, bbox_inches='tight')
    plt.close()


def load_metrics(scenario_dir):
    """Load metrics from metrics_summary.csv"""
    metrics_file = scenario_dir / 'metrics_summary.csv'
    if not metrics_file.exists():
        return {}
    
    df = pd.read_csv(metrics_file)
    if len(df) == 0:
        return {}
    
    return df.iloc[0].to_dict()


def generate_scenario_plots(scenario):
    """Generate all plots for a given scenario"""
    scenario_dir = Path(f'results/scenarios/{scenario}')
    
    if not scenario_dir.exists():
        print(f"✗ Scenario {scenario} directory not found")
        return False
    
    print(f"\n{'='*60}")
    print(f"Generating plots for {SCENARIOS[scenario]['name']}")
    print(f"{'='*60}")
    
    # Create output directory
    output_dir = Path(f'plots/scenarios/{scenario}')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load metrics
    metrics = load_metrics(scenario_dir)
    
    # Generate all plots
    plot_functions = [
        ('network_lifetime', lambda: plot_network_lifetime(scenario, scenario_dir, output_dir, metrics)),
        ('energy_consumption', lambda: plot_energy_consumption(scenario, scenario_dir, output_dir)),
        ('pdr', lambda: plot_pdr(scenario, scenario_dir, output_dir)),
        ('throughput', lambda: plot_throughput(scenario, scenario_dir, output_dir, metrics)),
        ('delay_distribution', lambda: plot_delay_distribution(scenario, scenario_dir, output_dir)),
        ('average_delay_per_round', lambda: plot_average_delay_per_round(scenario, scenario_dir, output_dir)),
        ('clustering_metrics', lambda: plot_clustering_metrics(scenario, scenario_dir, output_dir)),
        ('control_overhead', lambda: plot_control_overhead(scenario, scenario_dir, output_dir)),
    ]
    
    for plot_name, plot_func in plot_functions:
        try:
            print(f"  ✓ Generating {plot_name}.png...")
            plot_func()
        except Exception as e:
            print(f"  ✗ Error generating {plot_name}: {e}")
    
    print(f"\n✓ All plots saved to: {output_dir}")
    return True


def main():
    """Main execution"""
    print("="*60)
    print("Parametric Scenario Plot Generation (S1-S5)")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for scenario in SCENARIOS.keys():
        if generate_scenario_plots(scenario):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*60)
    print(f"Plot Generation Complete!")
    print(f"  ✓ Success: {success_count}/{len(SCENARIOS)} scenarios")
    if fail_count > 0:
        print(f"  ✗ Failed: {fail_count}/{len(SCENARIOS)} scenarios")
    print("="*60)


if __name__ == '__main__':
    main()
