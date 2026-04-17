#!/usr/bin/env python3
"""
Generate parameter sensitivity plots showing how varying a parameter affects metrics.
Creates side-by-side comparisons for each parameter group.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_metrics_summary(scenario_dir):
    """Load metrics from metrics_summary.csv for a scenario directory."""
    metrics_file = os.path.join(scenario_dir, 'metrics_summary.csv')
    if not os.path.exists(metrics_file):
        return None

    df = pd.read_csv(metrics_file)
    if len(df) == 0:
        return None

    row = df.iloc[0]
    return {
        'FND': int(row['FND']),
        'LND': int(row['LND']),
        'Lifetime': int(row['Lifetime']),
        'TotalEnergy': float(row['TotalEnergy_J']),
        'MeanPDR': float(row['MeanPDR']),
        'MeanThroughput': float(row['MeanThroughput_bps']) / 1000.0,
        'MeanDelay': float(row['MeanDelay_s']),
        'MeanOverhead': float(row.get('MeanControlRatio', 0)),
    }

def load_baseline_metrics():
    """Load baseline metrics from S0-Baseline multi-run statistical summary."""
    # Use multi-run averaged statistics instead of single-run data
    stats_file = 'results/multi-run/statistical_summary_new.csv'
    if not os.path.exists(stats_file):
        # Fallback to single-run data if multi-run stats not available
        print("Warning: Multi-run stats not found, using single-run baseline data")
        return load_metrics_summary('results/scenarios/S0-Baseline')
    
    df = pd.read_csv(stats_file)
    
    # Extract mean values from the statistical summary
    metrics = {}
    for _, row in df.iterrows():
        metric = row['Metric']
        mean_val = row['Mean']
        
        if metric == 'FND':
            metrics['FND'] = int(round(mean_val))
        elif metric == 'LND':
            metrics['LND'] = int(round(mean_val))
        elif metric == 'Lifetime':
            metrics['Lifetime'] = int(round(mean_val))
        elif metric == 'TotalEnergy_J':
            metrics['TotalEnergy'] = float(mean_val)
        elif metric == 'MeanPDR':
            metrics['MeanPDR'] = float(mean_val)
        elif metric == 'MeanThroughput_bps':
            metrics['MeanThroughput'] = float(mean_val) / 1000.0  # Convert to kbps
        elif metric == 'MeanDelay_s':
            metrics['MeanDelay'] = float(mean_val)
        elif metric == 'MeanControlRatio':
            metrics['MeanOverhead'] = float(mean_val)
    
    return metrics


def plot_metric(ax, x, y, labels, color, ylabel, title, fmt=None):
    """Common plotting helper with ordered labels and annotations."""
    ax.plot(x, y, 'o-', linewidth=2, markersize=8, color=color)
    ax.set_xlabel('Scenario (Group A → Baseline → Group B)', fontweight='bold')
    ax.set_ylabel(ylabel, fontweight='bold')
    ax.set_title(title, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    for xi, yi in zip(x, y):
        label = fmt.format(yi) if fmt else f'{yi}'
        ax.text(xi, yi, label, ha='center', va='bottom', fontsize=9)


def plot_fnd_lnd(ax, x, fnd, lnd, labels):
    """Plot FND and LND on the same axis."""
    ax.plot(x, fnd, 'o-', linewidth=2, markersize=8, color='#2ecc71', label='FND')
    ax.plot(x, lnd, 's--', linewidth=2, markersize=7, color='#3498db', label='LND')
    ax.set_xlabel('Scenario (Group A → Baseline → Group B)', fontweight='bold')
    ax.set_ylabel('Rounds', fontweight='bold')
    ax.set_title('First/Last Node Death (FND/LND)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    for xi, yi in zip(x, fnd):
        ax.text(xi, yi, f'{yi}', ha='center', va='bottom', fontsize=9)
    for xi, yi in zip(x, lnd):
        ax.text(xi, yi, f'{yi}', ha='center', va='bottom', fontsize=9)
    ax.legend(fontsize=9, loc='best')

def plot_ch_probability_sensitivity():
    """Plot S1: CH Probability parameter sensitivity."""
    
    baseline = load_baseline_metrics()
    s1a = load_metrics_summary('results/scenarios/S1-A')
    s1b = load_metrics_summary('results/scenarios/S1-B')
    
    if not baseline or not s1a or not s1b:
        print("✗ S1 scenarios: Missing summary files")
        return False
    
    # Ordered cases: Group A, Baseline, Group B
    x = [0, 1, 2]
    labels = ['Group A\n(0.05)', 'Baseline\n(0.1)', 'Group B\n(0.2)']
    data = {
        'FND': [s1a['FND'], baseline['FND'], s1b['FND']],
        'LND': [s1a['LND'], baseline['LND'], s1b['LND']],
        'PDR': [s1a['MeanPDR'], baseline['MeanPDR'], s1b['MeanPDR']],
        'Throughput': [s1a['MeanThroughput'], baseline['MeanThroughput'], s1b['MeanThroughput']],
        'Energy': [s1a['TotalEnergy'], baseline['TotalEnergy'], s1b['TotalEnergy']],
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('S1: Impact of CH Probability on Network Metrics\nOrder: Group A → Baseline → Group B', 
                 fontsize=16, fontweight='bold')
    
    # FND + LND
    ax = axes[0, 0]
    plot_fnd_lnd(ax, x, data['FND'], data['LND'], labels)
    
    # PDR
    ax = axes[0, 1]
    plot_metric(ax, x, data['PDR'], labels, '#e74c3c', 'Ratio', 'Packet Delivery Ratio', fmt='{:.3f}')
    ax.set_ylim([0, 1])
    
    # Throughput
    ax = axes[1, 0]
    plot_metric(ax, x, data['Throughput'], labels, '#f39c12', 'kbps', 'Mean Throughput', fmt='{:.3f}')
    
    # Energy
    ax = axes[1, 1]
    plot_metric(ax, x, data['Energy'], labels, '#16a085', 'Joules', 'Total Energy Consumed', fmt='{:.2f}')
    
    plt.tight_layout()
    os.makedirs('plots/parameter_sensitivity', exist_ok=True)
    plt.savefig('plots/parameter_sensitivity/S1_ch_probability.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ S1: CH Probability sensitivity plot")
    return True

def plot_node_density_sensitivity():
    """Plot S2: Node Density parameter sensitivity."""
    
    baseline = load_baseline_metrics()
    s2a = load_metrics_summary('results/scenarios/S2-A')
    s2b = load_metrics_summary('results/scenarios/S2-B')
    
    if not baseline or not s2a or not s2b:
        print("✗ S2 scenarios: Missing summary files")
        return False
    
    # Ordered cases: Baseline, Group A, Group B
    x = [0, 1, 2]
    labels = ['Baseline\n(100)', 'Group A\n(200)', 'Group B\n(300)']
    data = {
        'FND': [baseline['FND'], s2a['FND'], s2b['FND']],
        'LND': [baseline['LND'], s2a['LND'], s2b['LND']],
        'PDR': [baseline['MeanPDR'], s2a['MeanPDR'], s2b['MeanPDR']],
        'Throughput': [baseline['MeanThroughput'], s2a['MeanThroughput'], s2b['MeanThroughput']],
        'Energy': [baseline['TotalEnergy'], s2a['TotalEnergy'], s2b['TotalEnergy']],
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('S2: Impact of Node Density on Network Metrics\nOrder: Baseline → Group A → Group B', 
                 fontsize=16, fontweight='bold')
    
    # FND + LND
    ax = axes[0, 0]
    plot_fnd_lnd(ax, x, data['FND'], data['LND'], labels)
    
    # PDR
    ax = axes[0, 1]
    plot_metric(ax, x, data['PDR'], labels, '#e74c3c', 'Ratio', 'Packet Delivery Ratio', fmt='{:.3f}')
    ax.set_ylim([0, 1])
    
    # Throughput
    ax = axes[1, 0]
    plot_metric(ax, x, data['Throughput'], labels, '#f39c12', 'kbps', 'Mean Throughput', fmt='{:.3f}')
    
    # Energy
    ax = axes[1, 1]
    plot_metric(ax, x, data['Energy'], labels, '#16a085', 'Joules', 'Total Energy Consumed', fmt='{:.2f}')
    
    plt.tight_layout()
    os.makedirs('plots/parameter_sensitivity', exist_ok=True)
    plt.savefig('plots/parameter_sensitivity/S2_node_density.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ S2: Node Density sensitivity plot")
    return True

def plot_uav_speed_sensitivity():
    """Plot S3: UAV Speed parameter sensitivity."""
    
    baseline = load_baseline_metrics()
    s3a = load_metrics_summary('results/scenarios/S3-A')
    s3b = load_metrics_summary('results/scenarios/S3-B')
    
    if not baseline or not s3a or not s3b:
        print("✗ S3 scenarios: Missing summary files")
        return False
    
    # Ordered cases: Baseline, Group A, Group B
    x = [0, 1, 2]
    labels = ['Baseline\n(10 m/s)', 'Group A\n(15 m/s)', 'Group B\n(20 m/s)']
    data = {
        'FND': [baseline['FND'], s3a['FND'], s3b['FND']],
        'LND': [baseline['LND'], s3a['LND'], s3b['LND']],
        'PDR': [baseline['MeanPDR'], s3a['MeanPDR'], s3b['MeanPDR']],
        'Throughput': [baseline['MeanThroughput'], s3a['MeanThroughput'], s3b['MeanThroughput']],
        'Energy': [baseline['TotalEnergy'], s3a['TotalEnergy'], s3b['TotalEnergy']],
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('S3: Impact of UAV Speed on Network Metrics\nOrder: Baseline → Group A → Group B', 
                 fontsize=16, fontweight='bold')
    
    # FND + LND
    ax = axes[0, 0]
    plot_fnd_lnd(ax, x, data['FND'], data['LND'], labels)
    
    # PDR
    ax = axes[0, 1]
    plot_metric(ax, x, data['PDR'], labels, '#e74c3c', 'Ratio', 'Packet Delivery Ratio', fmt='{:.3f}')
    ax.set_ylim([0, 1])
    
    # Throughput
    ax = axes[1, 0]
    plot_metric(ax, x, data['Throughput'], labels, '#f39c12', 'kbps', 'Mean Throughput', fmt='{:.3f}')
    
    # Energy
    ax = axes[1, 1]
    plot_metric(ax, x, data['Energy'], labels, '#16a085', 'Joules', 'Total Energy Consumed', fmt='{:.2f}')
    
    plt.tight_layout()
    os.makedirs('plots/parameter_sensitivity', exist_ok=True)
    plt.savefig('plots/parameter_sensitivity/S3_uav_speed.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ S3: UAV Speed sensitivity plot")
    return True

def plot_initial_energy_sensitivity():
    """Plot S4: Initial Energy parameter sensitivity."""
    
    baseline = load_baseline_metrics()
    s4a = load_metrics_summary('results/scenarios/S4-A')
    s4b = load_metrics_summary('results/scenarios/S4-B')
    
    if not baseline or not s4a or not s4b:
        print("✗ S4 scenarios: Missing summary files")
        return False
    
    # Ordered cases: Baseline, Group A, Group B
    x = [0, 1, 2]
    labels = ['Baseline\n(0.5 J)', 'Group A\n(1.0 J)', 'Group B\n(2.0 J)']
    data = {
        'FND': [baseline['FND'], s4a['FND'], s4b['FND']],
        'LND': [baseline['LND'], s4a['LND'], s4b['LND']],
        'PDR': [baseline['MeanPDR'], s4a['MeanPDR'], s4b['MeanPDR']],
        'Throughput': [baseline['MeanThroughput'], s4a['MeanThroughput'], s4b['MeanThroughput']],
        'Energy': [baseline['TotalEnergy'], s4a['TotalEnergy'], s4b['TotalEnergy']],
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('S4: Impact of Initial Energy on Network Metrics\nOrder: Baseline → Group A → Group B', 
                 fontsize=16, fontweight='bold')
    
    # FND + LND
    ax = axes[0, 0]
    plot_fnd_lnd(ax, x, data['FND'], data['LND'], labels)
    
    # PDR
    ax = axes[0, 1]
    plot_metric(ax, x, data['PDR'], labels, '#e74c3c', 'Ratio', 'Packet Delivery Ratio', fmt='{:.3f}')
    ax.set_ylim([0, 1])
    
    # Throughput
    ax = axes[1, 0]
    plot_metric(ax, x, data['Throughput'], labels, '#f39c12', 'kbps', 'Mean Throughput', fmt='{:.3f}')
    
    # Energy
    ax = axes[1, 1]
    plot_metric(ax, x, data['Energy'], labels, '#16a085', 'Joules', 'Total Energy Consumed', fmt='{:.2f}')
    
    plt.tight_layout()
    os.makedirs('plots/parameter_sensitivity', exist_ok=True)
    plt.savefig('plots/parameter_sensitivity/S4_initial_energy.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ S4: Initial Energy sensitivity plot")
    return True

def plot_packet_size_sensitivity():
    """Plot S5: Packet Size parameter sensitivity."""
    
    baseline = load_baseline_metrics()
    s5a = load_metrics_summary('results/scenarios/S5-A')
    s5b = load_metrics_summary('results/scenarios/S5-B')
    
    if not baseline or not s5a or not s5b:
        print("✗ S5 scenarios: Missing summary files")
        return False
    
    # Ordered cases: Group A, Baseline, Group B
    x = [0, 1, 2]
    labels = ['Group A\n(500b)', 'Baseline\n(2000b)', 'Group B\n(4000b)']
    data = {
        'FND': [s5a['FND'], baseline['FND'], s5b['FND']],
        'LND': [s5a['LND'], baseline['LND'], s5b['LND']],
        'PDR': [s5a['MeanPDR'], baseline['MeanPDR'], s5b['MeanPDR']],
        'Throughput': [s5a['MeanThroughput'], baseline['MeanThroughput'], s5b['MeanThroughput']],
        'Energy': [s5a['TotalEnergy'], baseline['TotalEnergy'], s5b['TotalEnergy']],
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('S5: Impact of Packet Size on Network Metrics\nOrder: Group A → Baseline → Group B', 
                 fontsize=16, fontweight='bold')
    
    # FND + LND
    ax = axes[0, 0]
    plot_fnd_lnd(ax, x, data['FND'], data['LND'], labels)
    
    # PDR
    ax = axes[0, 1]
    plot_metric(ax, x, data['PDR'], labels, '#e74c3c', 'Ratio', 'Packet Delivery Ratio', fmt='{:.3f}')
    ax.set_ylim([0, 1])
    
    # Throughput
    ax = axes[1, 0]
    plot_metric(ax, x, data['Throughput'], labels, '#f39c12', 'kbps', 'Mean Throughput', fmt='{:.3f}')
    
    # Energy
    ax = axes[1, 1]
    plot_metric(ax, x, data['Energy'], labels, '#16a085', 'Joules', 'Total Energy Consumed', fmt='{:.2f}')
    
    plt.tight_layout()
    os.makedirs('plots/parameter_sensitivity', exist_ok=True)
    plt.savefig('plots/parameter_sensitivity/S5_packet_size.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ S5: Packet Size sensitivity plot")
    return True

def main():
    print("="*60)
    print("Generating Parameter Sensitivity Plots")
    print("="*60)
    
    success_count = 0
    
    if plot_ch_probability_sensitivity():
        success_count += 1
    
    if plot_node_density_sensitivity():
        success_count += 1
    
    if plot_uav_speed_sensitivity():
        success_count += 1
    
    if plot_initial_energy_sensitivity():
        success_count += 1

    if plot_packet_size_sensitivity():
        success_count += 1
    
    print("\n" + "="*60)
    print(f"Parameter sensitivity plots: {success_count}/5 completed")
    print("="*60)
    
    if success_count > 0:
        print("\nOutput: plots/parameter_sensitivity/")

if __name__ == '__main__':
    main()
