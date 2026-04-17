#!/usr/bin/env python3
"""
Scenario-level Summary Analysis
Compares configurations within a single scenario (e.g., S1-A vs S1-B vs Baseline)
Generates comparative plots and statistical tables for publication
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import json

def load_scenario_summary(summary_file):
    """Load statistical summary from a scenario configuration."""
    df = pd.read_csv(summary_file)
    return df

def create_scenario_comparison_plots(scenario_name, configs, output_dir):
    """Create comparative plots for all configurations in a scenario."""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set publication style
    plt.rcParams.update({
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 14,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 11,
        'figure.titlesize': 16
    })
    
    metrics = ['FND', 'LND', 'PDR', 'avg_delay', 'avg_CHs', 'avg_throughput', 
               'avg_cluster_size', 'avg_residual_energy']
    
    metric_labels = {
        'FND': 'First Node Death (s)',
        'LND': 'Last Node Death (s)',
        'PDR': 'Packet Delivery Ratio (%)',
        'avg_delay': 'Average Delay (s)',
        'avg_CHs': 'Average Cluster Heads',
        'avg_throughput': 'Average Throughput (packets/s)',
        'avg_cluster_size': 'Average Cluster Size',
        'avg_residual_energy': 'Average Residual Energy (J)'
    }
    
    # Load data from all configurations
    data = {}
    for config_name, config_path in configs.items():
        summary_file = Path(config_path) / 'statistical_summary.csv'
        if summary_file.exists():
            data[config_name] = load_scenario_summary(summary_file)
    
    if not data:
        print(f"No data found for scenario {scenario_name}")
        return
    
    # Create comparison bar plots with error bars
    for metric in metrics:
        if metric not in data[list(data.keys())[0]]['Metric'].values:
            continue
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        config_names = []
        means = []
        ci_lows = []
        ci_highs = []
        
        for config_name in sorted(data.keys()):
            df = data[config_name]
            row = df[df['Metric'] == metric]
            if not row.empty:
                config_names.append(config_name)
                mean_val = row['Mean'].values[0]
                ci_low = row['CI_Lower'].values[0]
                ci_high = row['CI_Upper'].values[0]
                
                means.append(mean_val)
                ci_lows.append(mean_val - ci_low)
                ci_highs.append(ci_high - mean_val)
        
        # Create bar plot with error bars
        x = np.arange(len(config_names))
        bars = ax.bar(x, means, width=0.6, alpha=0.8, 
                     color=['#2ecc71', '#3498db', '#e74c3c'][:len(config_names)])
        ax.errorbar(x, means, yerr=[ci_lows, ci_highs], 
                   fmt='none', ecolor='black', capsize=5, capthick=2)
        
        ax.set_xlabel('Configuration', fontweight='bold')
        ax.set_ylabel(metric_labels.get(metric, metric), fontweight='bold')
        ax.set_title(f'{scenario_name}: {metric_labels.get(metric, metric)}', 
                    fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(config_names, rotation=0)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, (bar, mean) in enumerate(zip(bars, means)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mean:.2f}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_dir / f'{metric}_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Comparison plots saved to {output_dir}")

def create_summary_table(scenario_name, configs, output_dir):
    """Create summary comparison table."""
    
    output_dir = Path(output_dir)
    
    # Key metrics for publication
    key_metrics = ['FND', 'LND', 'PDR', 'avg_delay', 'avg_CHs', 'avg_throughput']
    
    # Load data
    summary_data = []
    for config_name in sorted(configs.keys()):
        config_path = Path(configs[config_name])
        summary_file = config_path / 'statistical_summary.csv'
        
        if summary_file.exists():
            df = load_scenario_summary(summary_file)
            config_summary = {'Configuration': config_name}
            
            for metric in key_metrics:
                row = df[df['Metric'] == metric]
                if not row.empty:
                    mean = row['Mean'].values[0]
                    ci_low = row['CI_Lower'].values[0]
                    ci_high = row['CI_Upper'].values[0]
                    config_summary[metric] = f"{mean:.2f} [{ci_low:.2f}, {ci_high:.2f}]"
                else:
                    config_summary[metric] = "N/A"
            
            summary_data.append(config_summary)
    
    # Create DataFrame and save
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_dir / 'scenario_comparison_table.csv', index=False)
    
    # Create formatted text version
    with open(output_dir / 'scenario_comparison_table.txt', 'w') as f:
        f.write(f"{'='*80}\n")
        f.write(f"{scenario_name} - Configuration Comparison\n")
        f.write(f"{'='*80}\n\n")
        f.write(summary_df.to_string(index=False))
        f.write(f"\n\n")
        f.write("Values shown as: Mean [95% CI Lower, 95% CI Upper]\n")
        f.write(f"{'='*80}\n")
    
    print(f"Summary table saved to {output_dir}")
    return summary_df

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_scenario_summary.py <scenario_name> <config1_path> [config2_path] ...")
        print("Example: python analyze_scenario_summary.py S1-CH-Probability")
        print("         results/baseline results/S1-CH-Probability/S1-A-P005 results/S1-CH-Probability/S1-B-P020")
        sys.exit(1)
    
    scenario_name = sys.argv[1]
    
    # Auto-detect configurations if not provided
    if len(sys.argv) == 2:
        # Auto-detect based on scenario name
        base_path = Path('results')
        if 'S1' in scenario_name:
            folder = 'S1-CH-Probability'
            configs = {
                'Baseline (P=0.1)': base_path / 'multi-run',
                'S1-A (P=0.05)': base_path / folder / 'S1-A-P005',
                'S1-B (P=0.2)': base_path / folder / 'S1-B-P020'
            }
        elif 'S2' in scenario_name:
            folder = 'S2-Node-Density'
            configs = {
                'Baseline (N=100)': base_path / 'multi-run',
                'S2-A (N=200)': base_path / folder / 'S2-A-N200',
                'S2-B (N=300)': base_path / folder / 'S2-B-N300'
            }
        elif 'S3' in scenario_name:
            folder = 'S3-UAV-Speed'
            configs = {
                'Baseline (v=10)': base_path / 'multi-run',
                'S3-A (v=15)': base_path / folder / 'S3-A-v15',
                'S3-B (v=20)': base_path / folder / 'S3-B-v20'
            }
        elif 'S4' in scenario_name:
            folder = 'S4-Initial-Energy'
            configs = {
                'Baseline (E=0.5J)': base_path / 'multi-run',
                'S4-A (E=1.0J)': base_path / folder / 'S4-A-E10',
                'S4-B (E=2.0J)': base_path / folder / 'S4-B-E20'
            }
        else:
            print(f"Unknown scenario: {scenario_name}")
            sys.exit(1)
        
        output_dir = base_path / folder.replace('S1', scenario_name).replace('S2', scenario_name).replace('S3', scenario_name).replace('S4', scenario_name) / f'{scenario_name}-summary'
    else:
        # Manual configuration paths provided
        configs = {}
        for i in range(2, len(sys.argv)):
            path = Path(sys.argv[i])
            config_name = path.name
            configs[config_name] = path
        
        output_dir = Path('results') / scenario_name / f'{scenario_name}-summary'
    
    print(f"\n{'='*80}")
    print(f"Scenario Summary Analysis: {scenario_name}")
    print(f"{'='*80}")
    print(f"Configurations to compare:")
    for name, path in configs.items():
        print(f"  - {name}: {path}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")
    
    # Create comparison plots
    create_scenario_comparison_plots(scenario_name, configs, output_dir)
    
    # Create summary table
    create_summary_table(scenario_name, configs, output_dir)
    
    print(f"\n{'='*80}")
    print(f"Scenario summary analysis complete!")
    print(f"Results saved to: {output_dir}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
