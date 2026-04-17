#!/usr/bin/env python3
"""
Perform multi-run for baseline scenario and generate statistical summaries.
Uses existing OMNeT++ simulation runs from results/multi-run directory.
"""

import pandas as pd
import numpy as np
import glob
import os
from pathlib import Path
from scipy import stats

def extract_single_run_metrics(run_id, input_dir):
    """Extract metrics from one run's CSV files."""
    
    metrics = {'run_id': run_id}
    
    try:
        # Network lifetime metrics
        network_df = pd.read_csv(f'{input_dir}/network.csv')
        initial_nodes = network_df['AliveNodes'].iloc[0]
        
        fnd_row = network_df[network_df['AliveNodes'] < initial_nodes]
        metrics['FND'] = int(fnd_row.iloc[0]['Round']) if not fnd_row.empty else -1
        
        lnd_row = network_df[network_df['AliveNodes'] == 0]
        metrics['LND'] = int(lnd_row.iloc[0]['Round']) if not lnd_row.empty else len(network_df)
        
        metrics['Lifetime'] = metrics['LND'] - metrics['FND'] if metrics['FND'] > 0 else metrics['LND']
        
        # Energy metrics
        energy_df = pd.read_csv(f'{input_dir}/energy.csv')
        metrics['TotalEnergy_J'] = energy_df['EnergyConsumed'].sum()
        
        # PDR metrics
        pdr_df = pd.read_csv(f'{input_dir}/pdr.csv')
        metrics['MeanPDR'] = pdr_df['PDR'].mean()
        
        # Delay metrics
        delay_df = pd.read_csv(f'{input_dir}/delay.csv')
        metrics['MeanDelay_s'] = delay_df['Delay_s'].mean()
        metrics['MedianDelay_s'] = delay_df['Delay_s'].median()
        
        # Clustering metrics
        clustering_df = pd.read_csv(f'{input_dir}/clustering.csv')
        chs_per_round = clustering_df.groupby('Round')['ClusterID'].count()
        unclustered_per_round = clustering_df.groupby('Round')['UnclusteredNodes'].first()
        
        metrics['MeanCHs'] = chs_per_round.mean()
        metrics['UnclusteredPercent'] = (unclustered_per_round.mean() / 100) * 100
        
        # Throughput metrics
        throughput_df = pd.read_csv(f'{input_dir}/throughput.csv')
        metrics['MeanThroughput_bps'] = throughput_df['Throughput_bps'].mean()
        
        # Contact metrics
        contact_df = pd.read_csv(f'{input_dir}/contact.csv')
        total_contacts = len(contact_df)
        successful_contacts = len(contact_df[contact_df['ContactStatus'] == 1]) if 'ContactStatus' in contact_df.columns else total_contacts
        metrics['ContactSuccessRate'] = successful_contacts / total_contacts if total_contacts > 0 else 1.0
        
        # Control overhead metrics
        overhead_df = pd.read_csv(f'{input_dir}/overhead.csv')
        if 'ControlRatio' in overhead_df.columns:
            metrics['MeanControlRatio'] = overhead_df['ControlRatio'].mean()
        else:
            metrics['MeanControlRatio'] = 0.0
        
        return metrics
        
    except Exception as e:
        print(f"  ✗ Error extracting metrics from {input_dir}: {e}")
        return None

def generate_statistical_summaries(results_dir='results/multi-run'):
    """Generate CSV and TXT statistical summaries from multi-run results."""
    
    print("=" * 70)
    print("  Generating Statistical Summaries")
    print("=" * 70)
    
    # Find all run directories
    run_dirs = sorted([d for d in glob.glob(f'{results_dir}/run-*') if os.path.isdir(d)])
    
    if not run_dirs:
        print(f"✗ No run directories found in {results_dir}")
        return False
    
    print(f"\n✓ Found {len(run_dirs)} run directories")
    
    # Extract metrics from each run
    all_metrics = []
    
    print("\nExtracting metrics from runs:")
    for run_dir in run_dirs:
        run_id = int(os.path.basename(run_dir).split('-')[1])
        
        metrics = extract_single_run_metrics(run_id, run_dir)
        if metrics:
            all_metrics.append(metrics)
            print(f"  ✓ Run {run_id}: FND={metrics['FND']}, LND={metrics['LND']}, PDR={metrics['MeanPDR']:.4f}")
    
    if not all_metrics:
        print("✗ Failed to extract metrics from all runs")
        return False
    
    combined_df = pd.DataFrame(all_metrics)
    num_runs = len(combined_df)
    
    print(f"\n✓ Successfully extracted metrics from {num_runs} runs")
    
    # Define metrics of interest
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
    
    print("\nComputing statistics:")
    for metric, unit in metrics_of_interest:
        if metric in combined_df.columns:
            data = combined_df[metric].dropna()
            if len(data) > 1:
                mean = np.mean(data)
                std = np.std(data, ddof=1)
                std_err = stats.sem(data)
                ci = std_err * stats.t.ppf(0.975, len(data) - 1)  # 95% CI
                
                result = {
                    'Metric': metric,
                    'Mean': mean,
                    'Std': std,
                    'Min': np.min(data),
                    'Max': np.max(data),
                    'CV%': (std / mean * 100) if mean != 0 else 0,
                    'CI_95': ci,
                    'Unit': unit
                }
                results.append(result)
                
                print(f"  ✓ {metric}: {mean:.4f} ± {ci:.4f} {unit}")
    
    # Save CSV summary
    results_df = pd.DataFrame(results)
    csv_file = f'{results_dir}/statistical_summary_new.csv'
    results_df.to_csv(csv_file, index=False)
    print(f"\n✓ Saved: {csv_file}")
    
    # Save TXT summary
    txt_file = f'{results_dir}/statistical_summary_new.txt'
    with open(txt_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("  UAV-WSN Multi-Run Validation - Statistical Summary\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total Runs: {num_runs}\n")
        f.write(f"Confidence Level: 95%\n\n")
        
        for _, row in results_df.iterrows():
            metric = row['Metric']
            mean = row['Mean']
            ci = row['CI_95']
            unit = row['Unit']
            std = row['Std']
            min_val = row['Min']
            max_val = row['Max']
            cv = row['CV%']
            
            f.write(f"{metric}:\n")
            f.write(f"  Mean ± 95% CI: {mean:.4f} ± {ci:.4f} {unit}\n")
            f.write(f"  Std Dev: {std:.4f}\n")
            f.write(f"  Range: [{min_val:.4f}, {max_val:.4f}]\n")
            f.write(f"  CV: {cv:.2f}%\n\n")
    
    print(f"✓ Saved: {txt_file}")
    
    # Generate summary_stat_new.txt for S0-Baseline results directory
    generate_baseline_summary(results_df)
    
    return True

def generate_baseline_summary(results_df):
    """Generate summary_stat_new.txt for results/scenarios/S0-Baseline/."""
    
    output_file = 'results/scenarios/S0-Baseline/summary_stat_new.txt'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Get mean values
    metrics_dict = {row['Metric']: row for _, row in results_df.iterrows()}
    
    with open(output_file, 'w') as f:
        f.write("```plaintext\n")
        f.write("Scenario: S0-Baseline (Multi-Run Statistics)\n")
        f.write("=" * 50 + "\n\n")
        f.write("Description:\n")
        f.write("Baseline - Multi-run statistics (30 runs with different seeds)\n")
        f.write("Parameters: P=0.1, N=100, v=10m/s, E=0.5J, Size=2000b\n\n")
        
        f.write("Network Lifetime:\n")
        f.write("-" * 50 + "\n")
        
        if 'FND' in metrics_dict:
            row = metrics_dict['FND']
            f.write(f"FND (First Node Death):\n")
            f.write(f"  Mean: {row['Mean']:.0f} rounds\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f} rounds\n")
            f.write(f"  Std Dev: {row['Std']:.2f} rounds\n")
            f.write(f"  Range: [{row['Min']:.0f}, {row['Max']:.0f}] rounds\n\n")
        
        if 'LND' in metrics_dict:
            row = metrics_dict['LND']
            f.write(f"LND (Last Node Death):\n")
            f.write(f"  Mean: {row['Mean']:.0f} rounds\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f} rounds\n")
            f.write(f"  Std Dev: {row['Std']:.2f} rounds\n")
            f.write(f"  Range: [{row['Min']:.0f}, {row['Max']:.0f}] rounds\n\n")
        
        if 'Lifetime' in metrics_dict:
            row = metrics_dict['Lifetime']
            f.write(f"Lifetime (LND - FND):\n")
            f.write(f"  Mean: {row['Mean']:.0f} rounds\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f} rounds\n")
            f.write(f"  Std Dev: {row['Std']:.2f} rounds\n")
            f.write(f"  Range: [{row['Min']:.0f}, {row['Max']:.0f}] rounds\n\n")
        
        f.write("Energy:\n")
        f.write("-" * 50 + "\n")
        
        if 'TotalEnergy_J' in metrics_dict:
            row = metrics_dict['TotalEnergy_J']
            f.write(f"Total Energy Consumed:\n")
            f.write(f"  Mean: {row['Mean']:.4f} J\n")
            f.write(f"  95% CI: ± {row['CI_95']:.6f} J\n")
            f.write(f"  Std Dev: {row['Std']:.6f} J\n")
            f.write(f"  Range: [{row['Min']:.4f}, {row['Max']:.4f}] J\n\n")
        
        f.write("Performance Metrics:\n")
        f.write("-" * 50 + "\n")
        
        if 'MeanPDR' in metrics_dict:
            row = metrics_dict['MeanPDR']
            f.write(f"Mean PDR:\n")
            f.write(f"  Mean: {row['Mean']:.4f}\n")
            f.write(f"  95% CI: ± {row['CI_95']:.6f}\n")
            f.write(f"  Std Dev: {row['Std']:.6f}\n")
            f.write(f"  Range: [{row['Min']:.4f}, {row['Max']:.4f}]\n\n")
        
        if 'MeanDelay_s' in metrics_dict:
            row = metrics_dict['MeanDelay_s']
            f.write(f"Mean Delay:\n")
            f.write(f"  Mean: {row['Mean']:.2f} s\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f} s\n")
            f.write(f"  Std Dev: {row['Std']:.2f} s\n")
            f.write(f"  Range: [{row['Min']:.2f}, {row['Max']:.2f}] s\n\n")
        
        if 'MedianDelay_s' in metrics_dict:
            row = metrics_dict['MedianDelay_s']
            f.write(f"Median Delay:\n")
            f.write(f"  Mean: {row['Mean']:.2f} s\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f} s\n")
            f.write(f"  Std Dev: {row['Std']:.2f} s\n")
            f.write(f"  Range: [{row['Min']:.2f}, {row['Max']:.2f}] s\n\n")
        
        if 'MeanThroughput_bps' in metrics_dict:
            row = metrics_dict['MeanThroughput_bps']
            f.write(f"Mean Throughput:\n")
            f.write(f"  Mean: {row['Mean']:.2f} bps ({row['Mean']/1000:.4f} kbps)\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f} bps\n")
            f.write(f"  Std Dev: {row['Std']:.2f} bps\n")
            f.write(f"  Range: [{row['Min']:.2f}, {row['Max']:.2f}] bps\n\n")
        
        f.write("Clustering Metrics:\n")
        f.write("-" * 50 + "\n")
        
        if 'MeanCHs' in metrics_dict:
            row = metrics_dict['MeanCHs']
            f.write(f"Mean Cluster Heads:\n")
            f.write(f"  Mean: {row['Mean']:.2f}\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f}\n")
            f.write(f"  Std Dev: {row['Std']:.2f}\n")
            f.write(f"  Range: [{row['Min']:.2f}, {row['Max']:.2f}]\n\n")
        
        if 'UnclusteredPercent' in metrics_dict:
            row = metrics_dict['UnclusteredPercent']
            f.write(f"Unclustered Nodes Percentage:\n")
            f.write(f"  Mean: {row['Mean']:.2f}%\n")
            f.write(f"  95% CI: ± {row['CI_95']:.2f}%\n")
            f.write(f"  Std Dev: {row['Std']:.2f}%\n")
            f.write(f"  Range: [{row['Min']:.2f}, {row['Max']:.2f}]%\n\n")
        
        f.write("Contact Performance:\n")
        f.write("-" * 50 + "\n")
        
        if 'ContactSuccessRate' in metrics_dict:
            row = metrics_dict['ContactSuccessRate']
            f.write(f"Contact Success Rate:\n")
            f.write(f"  Mean: {row['Mean']:.4f}\n")
            f.write(f"  Range: [{row['Min']:.4f}, {row['Max']:.4f}]\n\n")
        
        f.write("Control Overhead:\n")
        f.write("-" * 50 + "\n")
        
        if 'MeanControlRatio' in metrics_dict:
            row = metrics_dict['MeanControlRatio']
            f.write(f"Mean Control Ratio:\n")
            f.write(f"  Mean: {row['Mean']:.4f}\n")
            f.write(f"  95% CI: ± {row['CI_95']:.4f}\n")
            f.write(f"  Std Dev: {row['Std']:.4f}\n")
            f.write(f"  Range: [{row['Min']:.4f}, {row['Max']:.4f}]\n\n")
        
        f.write("```\n")
    
    print(f"✓ Saved: {output_file}")

if __name__ == '__main__':
    success = generate_statistical_summaries()
    exit(0 if success else 1)
