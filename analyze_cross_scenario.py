#!/usr/bin/env python3
"""
Cross-Scenario Analysis
Compares results across all scenarios for publication-ready insights
Creates comprehensive comparison plots and tables
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

def load_all_scenarios():
    """Load statistical summaries from all scenarios."""
    
    base_path = Path('results')
    
    scenarios = {
        'Baseline': {
            'path': base_path / 'multi-run',
            'label': 'Baseline\n(N=100, P=0.1, v=10, E=0.5J)',
            'params': 'N=100, P=0.1, v=10m/s, E₀=0.5J'
        },
        'S1-A': {
            'path': base_path / 'S1-CH-Probability' / 'S1-A-P005',
            'label': 'S1-A\n(P=0.05)',
            'params': 'N=100, P=0.05, v=10m/s, E₀=0.5J'
        },
        'S1-B': {
            'path': base_path / 'S1-CH-Probability' / 'S1-B-P020',
            'label': 'S1-B\n(P=0.2)',
            'params': 'N=100, P=0.2, v=10m/s, E₀=0.5J'
        },
        'S2-A': {
            'path': base_path / 'S2-Node-Density' / 'S2-A-N200',
            'label': 'S2-A\n(N=200)',
            'params': 'N=200, P=0.1, v=10m/s, E₀=0.5J'
        },
        'S2-B': {
            'path': base_path / 'S2-Node-Density' / 'S2-B-N300',
            'label': 'S2-B\n(N=300)',
            'params': 'N=300, P=0.1, v=10m/s, E₀=0.5J'
        },
        'S3-A': {
            'path': base_path / 'S3-UAV-Speed' / 'S3-A-v15',
            'label': 'S3-A\n(v=15)',
            'params': 'N=100, P=0.1, v=15m/s, E₀=0.5J'
        },
        'S3-B': {
            'path': base_path / 'S3-UAV-Speed' / 'S3-B-v20',
            'label': 'S3-B\n(v=20)',
            'params': 'N=100, P=0.1, v=20m/s, E₀=0.5J'
        },
        'S4-A': {
            'path': base_path / 'S4-Initial-Energy' / 'S4-A-E10',
            'label': 'S4-A\n(E=1.0J)',
            'params': 'N=100, P=0.1, v=10m/s, E₀=1.0J'
        },
        'S4-B': {
            'path': base_path / 'S4-Initial-Energy' / 'S4-B-E20',
            'label': 'S4-B\n(E=2.0J)',
            'params': 'N=100, P=0.1, v=10m/s, E₀=2.0J'
        }
    }
    
    # Load data
    data = {}
    for scenario_id, info in scenarios.items():
        summary_file = info['path'] / 'statistical_summary.csv'
        if summary_file.exists():
            df = pd.read_csv(summary_file)
            data[scenario_id] = {
                'data': df,
                'label': info['label'],
                'params': info['params']
            }
            print(f"✓ Loaded: {scenario_id}")
        else:
            print(f"✗ Missing: {scenario_id} ({summary_file})")
    
    return data

def create_comprehensive_comparison(data, output_dir):
    """Create comprehensive cross-scenario comparison plots."""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set publication style
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 9,
        'ytick.labelsize': 10,
        'legend.fontsize': 9,
        'figure.titlesize': 14
    })
    
    # Key metrics for publication
    metrics = [
        ('FND', 'First Node Death (s)', '#e74c3c'),
        ('LND', 'Last Node Death (s)', '#3498db'),
        ('PDR', 'Packet Delivery Ratio (%)', '#2ecc71'),
        ('avg_delay', 'Average Delay (s)', '#f39c12'),
        ('avg_CHs', 'Average Cluster Heads', '#9b59b6'),
        ('avg_throughput', 'Throughput (packets/s)', '#1abc9c')
    ]
    
    # Create individual metric plots
    for metric, label, color in metrics:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        scenario_ids = []
        scenario_labels = []
        means = []
        ci_lows = []
        ci_highs = []
        
        for scenario_id in sorted(data.keys()):
            df = data[scenario_id]['data']
            row = df[df['Metric'] == metric]
            
            if not row.empty:
                scenario_ids.append(scenario_id)
                scenario_labels.append(data[scenario_id]['label'])
                
                mean_val = row['Mean'].values[0]
                ci_low = row['CI_Lower'].values[0]
                ci_high = row['CI_Upper'].values[0]
                
                means.append(mean_val)
                ci_lows.append(mean_val - ci_low)
                ci_highs.append(ci_high - mean_val)
        
        # Create bar plot
        x = np.arange(len(scenario_ids))
        bars = ax.bar(x, means, width=0.7, alpha=0.8, color=color)
        ax.errorbar(x, means, yerr=[ci_lows, ci_highs],
                   fmt='none', ecolor='black', capsize=4, capthick=1.5)
        
        ax.set_xlabel('Scenario Configuration', fontweight='bold')
        ax.set_ylabel(label, fontweight='bold')
        ax.set_title(f'Cross-Scenario Comparison: {label}', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(scenario_labels, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mean:.1f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(output_dir / f'{metric}_cross_scenario.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"✓ Individual metric plots saved")
    
    # Create 2x3 grid comparison for paper
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Cross-Scenario Performance Comparison', fontweight='bold', fontsize=16)
    
    for idx, (metric, label, color) in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]
        
        scenario_ids = []
        scenario_labels = []
        means = []
        ci_lows = []
        ci_highs = []
        
        for scenario_id in sorted(data.keys()):
            df = data[scenario_id]['data']
            row = df[df['Metric'] == metric]
            
            if not row.empty:
                scenario_ids.append(scenario_id)
                scenario_labels.append(data[scenario_id]['label'])
                
                mean_val = row['Mean'].values[0]
                ci_low = row['CI_Lower'].values[0]
                ci_high = row['CI_Upper'].values[0]
                
                means.append(mean_val)
                ci_lows.append(mean_val - ci_low)
                ci_highs.append(ci_high - mean_val)
        
        x = np.arange(len(scenario_ids))
        bars = ax.bar(x, means, width=0.7, alpha=0.8, color=color)
        ax.errorbar(x, means, yerr=[ci_lows, ci_highs],
                   fmt='none', ecolor='black', capsize=3, capthick=1)
        
        ax.set_ylabel(label, fontweight='bold', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(scenario_labels, rotation=45, ha='right', fontsize=8)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels (smaller for grid)
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mean:.1f}',
                   ha='center', va='bottom', fontsize=7)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cross_scenario_grid.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Grid comparison plot saved")

def create_comprehensive_table(data, output_dir):
    """Create comprehensive comparison table for publication."""
    
    output_dir = Path(output_dir)
    
    key_metrics = ['FND', 'LND', 'PDR', 'avg_delay', 'avg_CHs', 'avg_throughput']
    
    # Build table data
    table_data = []
    for scenario_id in sorted(data.keys()):
        df = data[scenario_id]['data']
        row_data = {
            'Scenario': scenario_id,
            'Configuration': data[scenario_id]['params']
        }
        
        for metric in key_metrics:
            metric_row = df[df['Metric'] == metric]
            if not metric_row.empty:
                mean = metric_row['Mean'].values[0]
                ci_low = metric_row['CI_Lower'].values[0]
                ci_high = metric_row['CI_Upper'].values[0]
                row_data[metric] = f"{mean:.2f} ± {(ci_high - ci_low)/2:.2f}"
            else:
                row_data[metric] = "N/A"
        
        table_data.append(row_data)
    
    # Create DataFrame
    table_df = pd.DataFrame(table_data)
    
    # Save CSV
    table_df.to_csv(output_dir / 'cross_scenario_comparison.csv', index=False)
    
    # Save formatted text version
    with open(output_dir / 'cross_scenario_comparison.txt', 'w') as f:
        f.write("="*120 + "\n")
        f.write("CROSS-SCENARIO PERFORMANCE COMPARISON\n")
        f.write("="*120 + "\n\n")
        f.write(table_df.to_string(index=False))
        f.write("\n\n")
        f.write("Values shown as: Mean ± Half-Width of 95% CI\n")
        f.write("All results based on 30 independent simulation runs\n")
        f.write("="*120 + "\n")
    
    # Create LaTeX table for paper
    with open(output_dir / 'cross_scenario_latex.tex', 'w') as f:
        f.write("\\begin{table}[htbp]\n")
        f.write("\\centering\n")
        f.write("\\caption{Cross-Scenario Performance Comparison}\n")
        f.write("\\label{tab:cross_scenario}\n")
        f.write("\\begin{tabular}{llcccccc}\n")
        f.write("\\hline\n")
        f.write("Scenario & Configuration & FND (s) & LND (s) & PDR (\\%) & Delay (s) & CHs & Throughput \\\\\n")
        f.write("\\hline\n")
        
        for _, row in table_df.iterrows():
            scenario = row['Scenario']
            config = row['Configuration'].replace('_', '\\_')
            f.write(f"{scenario} & {config} & ")
            f.write(f"{row['FND']} & {row['LND']} & {row['PDR']} & ")
            f.write(f"{row['avg_delay']} & {row['avg_CHs']} & {row['avg_throughput']} \\\\\n")
        
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    
    print(f"✓ Comparison tables saved (CSV, TXT, LaTeX)")
    return table_df

def create_sensitivity_analysis(data, output_dir):
    """Create sensitivity analysis plots showing parameter impact."""
    
    output_dir = Path(output_dir)
    
    # Group scenarios by parameter variation
    param_groups = {
        'CH Probability': {
            'scenarios': ['Baseline', 'S1-A', 'S1-B'],
            'param_values': [0.1, 0.05, 0.2],
            'param_name': 'CH Probability (P)'
        },
        'Node Density': {
            'scenarios': ['Baseline', 'S2-A', 'S2-B'],
            'param_values': [100, 200, 300],
            'param_name': 'Number of Nodes (N)'
        },
        'UAV Speed': {
            'scenarios': ['Baseline', 'S3-A', 'S3-B'],
            'param_values': [10, 15, 20],
            'param_name': 'UAV Speed (m/s)'
        },
        'Initial Energy': {
            'scenarios': ['Baseline', 'S4-A', 'S4-B'],
            'param_values': [0.5, 1.0, 2.0],
            'param_name': 'Initial Energy (J)'
        }
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Parameter Sensitivity Analysis', fontweight='bold', fontsize=16)
    
    for idx, (param_name, group_info) in enumerate(param_groups.items()):
        ax = axes[idx // 2, idx % 2]
        
        scenarios = group_info['scenarios']
        param_values = group_info['param_values']
        x_label = group_info['param_name']
        
        # Plot FND and LND trends
        fnd_means = []
        lnd_means = []
        
        for scenario_id in scenarios:
            if scenario_id in data:
                df = data[scenario_id]['data']
                
                fnd_row = df[df['Metric'] == 'FND']
                lnd_row = df[df['Metric'] == 'LND']
                
                if not fnd_row.empty:
                    fnd_means.append(fnd_row['Mean'].values[0])
                if not lnd_row.empty:
                    lnd_means.append(lnd_row['Mean'].values[0])
        
        ax.plot(param_values, fnd_means, 'o-', linewidth=2, markersize=8, 
               label='FND', color='#e74c3c')
        ax.plot(param_values, lnd_means, 's-', linewidth=2, markersize=8,
               label='LND', color='#3498db')
        
        ax.set_xlabel(x_label, fontweight='bold')
        ax.set_ylabel('Time (s)', fontweight='bold')
        ax.set_title(f'Impact of {param_name}', fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Sensitivity analysis plot saved")

def main():
    print("\n" + "="*80)
    print("CROSS-SCENARIO ANALYSIS")
    print("="*80 + "\n")
    
    output_dir = Path('results/cross-scenario-analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load all scenario data
    print("Loading scenario data...")
    data = load_all_scenarios()
    
    if len(data) < 2:
        print("\nError: Need at least 2 scenarios for comparison")
        print("Please run individual scenarios first")
        sys.exit(1)
    
    print(f"\n✓ Loaded {len(data)} scenarios\n")
    
    # Create comprehensive comparison plots
    print("Creating cross-scenario comparison plots...")
    create_comprehensive_comparison(data, output_dir)
    
    # Create comprehensive table
    print("\nCreating comparison tables...")
    create_comprehensive_table(data, output_dir)
    
    # Create sensitivity analysis
    print("\nCreating sensitivity analysis...")
    create_sensitivity_analysis(data, output_dir)
    
    print("\n" + "="*80)
    print("CROSS-SCENARIO ANALYSIS COMPLETE!")
    print(f"Results saved to: {output_dir}")
    print("="*80 + "\n")
    
    print("Generated files:")
    print(f"  - Individual metric plots: *_cross_scenario.png")
    print(f"  - Grid comparison: cross_scenario_grid.png")
    print(f"  - Sensitivity analysis: sensitivity_analysis.png")
    print(f"  - Comparison table (CSV): cross_scenario_comparison.csv")
    print(f"  - Comparison table (TXT): cross_scenario_comparison.txt")
    print(f"  - LaTeX table: cross_scenario_latex.tex")
    print()

if __name__ == "__main__":
    main()
