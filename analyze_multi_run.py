#!/usr/bin/env python3
"""Aggregate and analyze results from multiple simulation runs."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import glob
import os

def calculate_confidence_interval(data, confidence=0.95):
    """Calculate confidence interval for given data."""
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)
    ci = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, ci

def analyze_multi_run_results(results_dir='results/multi-run'):
    """Analyze aggregated results from all runs."""
    
    print("=" * 60)
    print("  Multi-Run Statistical Analysis")
    print("=" * 60)
    
    # Load all run summaries
    summary_files = glob.glob(f'{results_dir}/run-*-summary.csv')
    
    if not summary_files:
        print(f"✗ No summary files found in {results_dir}")
        return None
    
    print(f"\nFound {len(summary_files)} runs")
    
    # Combine all runs into single dataframe
    all_runs = []
    for file in sorted(summary_files):
        df = pd.read_csv(file)
        all_runs.append(df)
    
    combined_df = pd.concat(all_runs, ignore_index=True)
    
    # Statistical summary
    print("\n" + "=" * 60)
    print(f"  STATISTICAL SUMMARY ({len(combined_df)} runs)")
    print("=" * 60)
    
    # Key metrics
    metrics_of_interest = [
        ('FND', 'rounds'),
        ('LND', 'rounds'),
        ('Lifetime', 'rounds'),
        ('MeanPDR', 'ratio'),
        ('MeanDelay_s', 'seconds'),
        ('MedianDelay_s', 'seconds'),
        ('TotalEnergy_J', 'joules'),
        ('MeanCHs', 'count'),
        ('UnclusteredPercent', 'percent'),
        ('MeanThroughput_bps', 'bps'),
        ('ContactSuccessRate', 'ratio'),
        ('MeanControlRatio', 'ratio')
    ]
    
    results = []
    
    for metric, unit in metrics_of_interest:
        if metric in combined_df.columns:
            data = combined_df[metric].dropna()
            if len(data) > 1:
                mean, ci = calculate_confidence_interval(data)
                
                result = {
                    'Metric': metric,
                    'Mean': mean,
                    'Std': np.std(data),
                    'Min': np.min(data),
                    'Max': np.max(data),
                    'CV%': (np.std(data) / mean * 100) if mean != 0 else 0,
                    'CI_95': ci,
                    'Unit': unit
                }
                results.append(result)
                
                print(f"\n{metric}:")
                print(f"  Mean ± 95% CI: {mean:.4f} ± {ci:.4f} {unit}")
                print(f"  Std Dev: {result['Std']:.4f}")
                print(f"  Range: [{result['Min']:.4f}, {result['Max']:.4f}]")
                print(f"  Coefficient of Variation: {result['CV%']:.2f}%")
    
    # Save statistical summary
    results_df = pd.DataFrame(results)
    results_df.to_csv(f'{results_dir}/statistical_summary.csv', index=False)
    
    # Generate summary report
    with open(f'{results_dir}/statistical_summary.txt', 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("  UAV-WSN Multi-Run Validation - Statistical Summary\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total Runs: {len(combined_df)}\n")
        f.write(f"Confidence Level: 95%\n\n")
        
        for _, row in results_df.iterrows():
            f.write(f"{row['Metric']}:\n")
            f.write(f"  Mean ± 95% CI: {row['Mean']:.4f} ± {row['CI_95']:.4f} {row['Unit']}\n")
            f.write(f"  Std Dev: {row['Std']:.4f}\n")
            f.write(f"  Range: [{row['Min']:.4f}, {row['Max']:.4f}]\n")
            f.write(f"  CV: {row['CV%']:.2f}%\n\n")
    
    print(f"\n✓ Statistical summary saved to:")
    print(f"  - {results_dir}/statistical_summary.csv")
    print(f"  - {results_dir}/statistical_summary.txt")
    
    # Generate visualization plots
    generate_validation_plots(combined_df, results_dir)
    
    # Variance analysis
    analyze_variance(combined_df, results_dir)
    
    return combined_df

def generate_validation_plots(df, output_dir):
    """Generate box plots and distribution plots for key metrics."""
    
    print("\n" + "=" * 60)
    print("  Generating Validation Plots")
    print("=" * 60)
    
    os.makedirs(f'{output_dir}/validation_plots', exist_ok=True)
    
    # Metrics to plot
    metrics = {
        'FND': 'First Node Death (rounds)',
        'LND': 'Last Node Death (rounds)',
        'MeanPDR': 'Mean PDR',
        'MeanDelay_s': 'Mean Delay (s)',
        'MeanCHs': 'Mean CHs per Round',
        'UnclusteredPercent': 'Unclustered Nodes (%)',
        'MeanThroughput_bps': 'Mean Throughput (bps)'
    }
    
    for metric, label in metrics.items():
        if metric not in df.columns:
            continue
        
        data = df[metric].dropna()
        if len(data) == 0:
            continue
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Box plot
        ax1.boxplot(data, vert=True)
        ax1.set_ylabel(label, fontsize=14, fontweight='bold')
        ax1.set_title(f'{label} - Box Plot', fontsize=16, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Histogram with mean/CI
        if len(data) > 1:
            mean, ci = calculate_confidence_interval(data)
            
            ax2.hist(data, bins=min(15, len(data)), alpha=0.7, color='steelblue', edgecolor='black')
            ax2.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.2f}')
            ax2.axvline(mean - ci, color='orange', linestyle=':', linewidth=2, label=f'95% CI: ±{ci:.2f}')
            ax2.axvline(mean + ci, color='orange', linestyle=':', linewidth=2)
            ax2.set_xlabel(label, fontsize=14, fontweight='bold')
            ax2.set_ylabel('Frequency', fontsize=14, fontweight='bold')
            ax2.set_title(f'{label} - Distribution', fontsize=16, fontweight='bold')
            ax2.legend(fontsize=12)
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/validation_plots/{metric}_validation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Generated: {metric}_validation.png")
    
    # Combined comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # FND/LND comparison
    if 'FND' in df.columns and 'LND' in df.columns:
        ax = axes[0, 0]
        fnd_data = df['FND'].dropna()
        lnd_data = df['LND'].dropna()
        if len(fnd_data) > 0 and len(lnd_data) > 0:
            ax.boxplot([fnd_data, lnd_data], labels=['FND', 'LND'])
            ax.set_ylabel('Rounds', fontsize=14, fontweight='bold')
            ax.set_title('Network Lifetime Variability', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
    
    # PDR distribution
    if 'MeanPDR' in df.columns:
        ax = axes[0, 1]
        pdr_data = df['MeanPDR'].dropna()
        if len(pdr_data) > 0:
            ax.hist(pdr_data, bins=min(20, len(pdr_data)), alpha=0.7, color='green', edgecolor='black')
            ax.set_xlabel('Mean PDR', fontsize=14, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=14, fontweight='bold')
            ax.set_title('PDR Distribution Across Runs', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
    
    # Delay distribution
    if 'MeanDelay_s' in df.columns:
        ax = axes[1, 0]
        delay_data = df['MeanDelay_s'].dropna()
        if len(delay_data) > 0:
            ax.hist(delay_data, bins=min(20, len(delay_data)), alpha=0.7, color='orange', edgecolor='black')
            ax.set_xlabel('Mean Delay (s)', fontsize=14, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=14, fontweight='bold')
            ax.set_title('Delay Distribution Across Runs', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
    
    # Energy consumption
    if 'TotalEnergy_J' in df.columns:
        ax = axes[1, 1]
        energy_data = df['TotalEnergy_J'].dropna()
        if len(energy_data) > 0:
            ax.hist(energy_data, bins=min(20, len(energy_data)), alpha=0.7, color='purple', edgecolor='black')
            ax.set_xlabel('Total Energy (J)', fontsize=14, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=14, fontweight='bold')
            ax.set_title('Energy Consumption Distribution', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/validation_plots/combined_validation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Generated: combined_validation.png")

def analyze_variance(df, output_dir):
    """Analyze which metrics have high/low variance."""
    
    print("\n" + "=" * 60)
    print("  Variance Analysis")
    print("=" * 60)
    
    cv_metrics = []
    
    for col in df.columns:
        if col == 'run_id':
            continue
        
        data = df[col].dropna()
        if len(data) > 0 and data.mean() != 0:
            cv = (data.std() / data.mean()) * 100
            cv_metrics.append({'Metric': col, 'CV%': cv, 'Category': categorize_variance(cv)})
    
    if len(cv_metrics) == 0:
        print("  No variance data to analyze")
        return
    
    cv_df = pd.DataFrame(cv_metrics).sort_values('CV%')
    
    print("\nCoefficient of Variation (CV) Analysis:")
    print("  Low variance (CV < 10%): Highly reproducible")
    print("  Medium variance (10% ≤ CV < 25%): Acceptable variability")
    print("  High variance (CV ≥ 25%): Significant variability\n")
    
    for _, row in cv_df.iterrows():
        print(f"  {row['Metric']:30s}: CV = {row['CV%']:6.2f}% ({row['Category']})")
    
    cv_df.to_csv(f'{output_dir}/variance_analysis.csv', index=False)
    print(f"\n✓ Variance analysis saved to: {output_dir}/variance_analysis.csv")

def categorize_variance(cv):
    """Categorize variance level."""
    if cv < 10:
        return 'Low'
    elif cv < 25:
        return 'Medium'
    else:
        return 'High'

if __name__ == '__main__':
    analyze_multi_run_results()
