#!/usr/bin/env python3
"""Generate comparison plots for parametric scenarios."""

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
        'HNA': int(row['HNA']),
        'Lifetime': int(row['Lifetime']),
        'TotalEnergy': float(row['TotalEnergy_J']),
        'MeanEnergy': float(row['MeanEnergyPerRound_J']),
        'MeanPDR': float(row['MeanPDR']),
        'MeanThroughput': float(row['MeanThroughput_bps']) / 1000.0,
        'MeanDelay': float(row['MeanDelay_s']),
        'MeanOverhead': float(row.get('MeanControlRatio', 0)),
        'MeanCHs': float(row.get('MeanCHs', 0)),
        'UnclusteredPercent': float(row.get('UnclusteredPercent', 0)),
    }


def load_baseline_metrics_multirun():
    """Load baseline metrics from S0-Baseline multi-run statistical summary."""
    stats_file = 'results/multi-run/statistical_summary_new.csv'
    if not os.path.exists(stats_file):
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
            metrics['MeanThroughput'] = float(mean_val) / 1000.0
        elif metric == 'MeanDelay_s':
            metrics['MeanDelay'] = float(mean_val)
        elif metric == 'MeanControlRatio':
            metrics['MeanOverhead'] = float(mean_val)
        elif metric == 'MeanCHs':
            metrics['MeanCHs'] = float(mean_val)
        elif metric == 'UnclusteredPercent':
            metrics['UnclusteredPercent'] = float(mean_val)
    
    # Calculate HNA (approximately halfway between FND and LND)
    if 'FND' in metrics and 'LND' in metrics:
        metrics['HNA'] = int(round((metrics['FND'] + metrics['LND']) / 2))
    
    # Calculate MeanEnergy per round if not present
    if 'TotalEnergy' in metrics and 'LND' in metrics:
        metrics['MeanEnergy'] = metrics['TotalEnergy'] / metrics['LND']
    
    return metrics


# Load baseline metrics using multi-run average (S0-Baseline)
baseline = load_baseline_metrics_multirun()
if baseline is None:
    raise FileNotFoundError('Missing baseline multi-run statistics')

# Load scenario metrics (updated folders)
scenarios = {
    'S1-A\n(P=0.05)': 'results/scenarios/S1-A',
    'S1-B\n(P=0.2)': 'results/scenarios/S1-B',
    'S2-A\n(N=200)': 'results/scenarios/S2-A',
    'S2-B\n(N=300)': 'results/scenarios/S2-B',
    'S3-A\n(v=15)': 'results/scenarios/S3-A',
    'S3-B\n(v=20)': 'results/scenarios/S3-B',
    'S4-A\n(E=1.0J)': 'results/scenarios/S4-A',
    'S4-B\n(E=2.0J)': 'results/scenarios/S4-B',
    'S5-A\n(500b)': 'results/scenarios/S5-A',
    'S5-B\n(4000b)': 'results/scenarios/S5-B',
}

data = {}
# Add baseline with multi-run average
data['Baseline\n(P=0.1)'] = baseline

# Load other scenarios
for name, path in scenarios.items():
    metrics = load_metrics_summary(path)
    if metrics is None:
        raise FileNotFoundError(f'Missing metrics_summary.csv in {path}')
    data[name] = metrics

# Create plots directory
os.makedirs('plots/scenarios', exist_ok=True)

# Set global font sizes for better visibility
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
})

# Figure 1: Network Lifetime Metrics
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Parametric Analysis: Network Lifetime Metrics (All Scenarios)', fontsize=20, fontweight='bold')

scenarios_list = list(data.keys())
colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#8e44ad', '#c0392b', '#16a085', '#7f8c8d']

# FND
ax = axes[0, 0]
fnd_values = [data[s]['FND'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), fnd_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Rounds', fontweight='bold', fontsize=14)
ax.set_title('First Node Death (FND)', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, fnd_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val}',
                ha='center', va='bottom', fontsize=11)

# LND
ax = axes[0, 1]
lnd_values = [data[s]['LND'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), lnd_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Rounds', fontweight='bold', fontsize=14)
ax.set_title('Last Node Death (LND)', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, lnd_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val}',
                ha='center', va='bottom', fontsize=11)

# HNA
ax = axes[1, 0]
hna_values = [data[s]['HNA'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), hna_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Rounds', fontweight='bold', fontsize=14)
ax.set_title('Half Nodes Alive (HNA)', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, hna_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val}',
                ha='center', va='bottom', fontsize=11)

# Lifetime
ax = axes[1, 1]
lifetime_values = [data[s]['Lifetime'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), lifetime_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Rounds', fontweight='bold', fontsize=14)
ax.set_title('Network Lifetime (LND-FND)', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, lifetime_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val}',
                ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('plots/scenarios/lifetime_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/scenarios/lifetime_comparison.png")
plt.close()

# Figure 1B: Combined FND/LND (side-by-side bars)
fig, ax = plt.subplots(figsize=(16, 6.5))
fig.suptitle('Parametric Analysis: FND vs LND (All Scenarios)', fontsize=26, fontweight='bold')

fnd_values = [data[s]['FND'] for s in scenarios_list]
lnd_values = [data[s]['LND'] for s in scenarios_list]

bar_width = 0.08
indices = np.arange(len(scenarios_list)) * 0.24

bars_fnd = ax.bar(indices - bar_width / 2, fnd_values, width=bar_width, color='#2ecc71', label='FND')
bars_lnd = ax.bar(indices + bar_width / 2, lnd_values, width=bar_width, color='#3498db', label='LND')

ax.set_xticks(indices)
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=18)
ax.margins(x=0.005)
ax.set_ylabel('Rounds', fontweight='bold', fontsize=22)
ax.tick_params(axis='y', labelsize=18)
ax.set_title('First Node Death (FND) vs Last Node Death (LND)', fontweight='bold', fontsize=24)
ax.grid(axis='y', alpha=0.3)
ax.legend(fontsize=18)
ax.margins(x=0.01)

for bar, val in zip(bars_fnd, fnd_values):
    ax.text(bar.get_x() + bar.get_width() / 2, val, f'{val}', ha='center', va='bottom', fontsize=17, fontweight='bold')

for bar, val in zip(bars_lnd, lnd_values):
    ax.text(bar.get_x() + bar.get_width() / 2, val, f'{val}', ha='center', va='bottom', fontsize=17, fontweight='bold')

plt.tight_layout()
plt.savefig('plots/scenarios/lifetime_comparison_grouped.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/scenarios/lifetime_comparison_grouped.png")
plt.close()

# Figure 2: Energy Metrics
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
fig.suptitle('Parametric Analysis: Energy Consumption (All Scenarios)', fontsize=20, fontweight='bold')

# Total Energy
ax = axes[0]
energy_values = [data[s]['TotalEnergy'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), energy_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Joules', fontweight='bold', fontsize=14)
ax.set_title('Total Energy Consumed', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, energy_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.2f}',
                ha='center', va='bottom', fontsize=11)

# Mean Energy Per Round
ax = axes[1]
mean_energy_values = [data[s]['MeanEnergy'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), mean_energy_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Joules', fontweight='bold', fontsize=14)
ax.set_title('Mean Energy Per Round', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, mean_energy_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.4f}',
                ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('plots/scenarios/energy_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/scenarios/energy_comparison.png")
plt.close()

# Figure 3: Performance Metrics
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Parametric Analysis: Network Performance (All Scenarios)', fontsize=20, fontweight='bold')

# PDR
ax = axes[0, 0]
pdr_values = [data[s]['MeanPDR'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), pdr_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Ratio', fontweight='bold', fontsize=14)
ax.set_title('Packet Delivery Ratio (PDR)', fontweight='bold', fontsize=16)
ax.set_ylim([0, 1])
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, pdr_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.3f}',
                ha='center', va='bottom', fontsize=11)

# Throughput
ax = axes[0, 1]
throughput_values = [data[s]['MeanThroughput'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), throughput_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('kbps', fontweight='bold', fontsize=14)
ax.set_title('Mean Throughput', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, throughput_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.3f}',
                ha='center', va='bottom', fontsize=11)

# Delay (seconds)
ax = axes[1, 0]
delay_values = [data[s]['MeanDelay'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), delay_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Seconds', fontweight='bold', fontsize=14)
ax.set_title('Mean Delay', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, delay_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.1f}',
                ha='center', va='bottom', fontsize=11)

# Overhead
ax = axes[1, 1]
overhead_values = [data[s]['MeanOverhead'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), overhead_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Ratio', fontweight='bold', fontsize=14)
ax.set_title('Mean Overhead Ratio', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, overhead_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.3f}',
                ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('plots/scenarios/performance_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/scenarios/performance_comparison.png")
plt.close()

# Figure 4: Clustering Metrics
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
fig.suptitle('Parametric Analysis: Clustering Metrics (All Scenarios)', fontsize=20, fontweight='bold')

# Mean CHs
ax = axes[0]
chs_values = [data[s]['MeanCHs'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), chs_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Cluster Heads', fontweight='bold', fontsize=14)
ax.set_title('Mean Cluster Heads', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, chs_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.2f}',
                ha='center', va='bottom', fontsize=11)

# Unclustered Percent
ax = axes[1]
unc_values = [data[s]['UnclusteredPercent'] for s in scenarios_list]
bars = ax.bar(range(len(scenarios_list)), unc_values, color=colors[:len(scenarios_list)])
ax.set_xticks(range(len(scenarios_list)))
ax.set_xticklabels(scenarios_list, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Percent', fontweight='bold', fontsize=14)
ax.set_title('Mean Unclustered Nodes (%)', fontweight='bold', fontsize=16)
ax.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, unc_values)):
    ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.1f}',
                ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('plots/scenarios/clustering_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/scenarios/clustering_comparison.png")
plt.close()

print("\n✓ All comparison plots generated successfully!")
print(f"  - Compared {len(scenarios_list)} scenarios (including baseline)")
print(f"  - Output directory: plots/scenarios/")
