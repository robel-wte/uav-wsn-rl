#!/usr/bin/env python3
"""
Run 30 baseline scenario simulations with different seeds and generate statistical summaries.
"""

import subprocess
import os
import sys
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

def run_baseline_multirun(num_runs=30, results_dir='results/multi-run'):
    """Run baseline scenario with multiple seeds."""
    
    print("=" * 70)
    print("  UAV-WSN Baseline Multi-Run Simulation")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  - Scenario: S0-Baseline (P=0.1, N=100, v=10m/s, E=0.5J)")
    print(f"  - Number of runs: {num_runs}")
    print(f"  - Output directory: {results_dir}")
    print(f"  - Each run uses a different seed (1-{num_runs})")
    
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(f'{results_dir}/logs', exist_ok=True)
    
    # Build the project first
    print("\n" + "=" * 70)
    print("  Building OMNeT++ project...")
    print("=" * 70)
    
    try:
        result = subprocess.run(['make', 'clean'], cwd='/workspaces/uav-wsn-bm', 
                              capture_output=True, text=True, timeout=60)
        result = subprocess.run(['make'], cwd='/workspaces/uav-wsn-bm', 
                              capture_output=True, text=True, timeout=300)
        print("✓ Build successful")
    except Exception as e:
        print(f"✗ Build failed: {e}")
        return False
    
    # Run each simulation
    print("\n" + "=" * 70)
    print("  Running 30 Baseline Simulations")
    print("=" * 70)
    
    failed_runs = []
    
    for run_id in range(num_runs):
        print(f"\n[{run_id + 1}/{num_runs}] Running baseline simulation (seed={run_id + 1})...")
        
        run_dir = f'{results_dir}/run-{run_id}'
        os.makedirs(run_dir, exist_ok=True)
        
        log_file = f'{results_dir}/logs/run-{run_id}.log'
        
        try:
            # Run the simulation with specific seed
            cmd = [
                './uav-wsn-bm',
                '-u', 'Cmdenv',
                '-c', 'General',  # Using General config from omnetpp.ini (baseline)
                '-r', str(run_id),
                '-s', str(run_id + 1),  # Seed from 1 to 30
                'omnetpp.ini'
            ]
            
            result = subprocess.run(cmd, cwd='/workspaces/uav-wsn-bm',
                                  capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                print(f"  ✗ Simulation failed with return code {result.returncode}")
                failed_runs.append(run_id)
                with open(log_file, 'w') as f:
                    f.write(result.stderr)
                continue
            
            # Save output logs
            with open(log_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nSTDERR:\n")
                    f.write(result.stderr)
            
            # Copy generated CSV files to run directory
            out_dir = '/workspaces/uav-wsn-bm/out/General/'
            if os.path.exists(out_dir):
                csv_files = glob.glob(f'{out_dir}/*.csv')
                for csv_file in csv_files:
                    dest_file = os.path.join(run_dir, os.path.basename(csv_file))
                    if os.path.exists(csv_file):
                        import shutil
                        shutil.copy(csv_file, dest_file)
                
                # Also copy .sca files
                sca_files = glob.glob(f'{out_dir}/*.sca')
                for sca_file in sca_files:
                    dest_file = os.path.join(run_dir, os.path.basename(sca_file))
                    if os.path.exists(sca_file):
                        import shutil
                        shutil.copy(sca_file, dest_file)
            
            print(f"  ✓ Completed - Results saved to {run_dir}")
            
        except subprocess.TimeoutExpired:
            print(f"  ✗ Simulation timeout")
            failed_runs.append(run_id)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed_runs.append(run_id)
    
    if failed_runs:
        print(f"\n⚠️  {len(failed_runs)} runs failed: {failed_runs}")
    
    print("\n" + "=" * 70)
    print("  Extracting Metrics from All Runs")
    print("=" * 70)
    
    # Extract metrics from each run
    from extract_metrics import extract_single_run_metrics
    
    for run_id in range(num_runs):
        if run_id in failed_runs:
            continue
        
        run_dir = f'{results_dir}/run-{run_id}'
        output_file = f'{results_dir}/run-{run_id}-summary.csv'
        
        try:
            extract_single_run_metrics(run_id, run_dir, output_file)
            print(f"  ✓ Extracted metrics for run-{run_id}")
        except Exception as e:
            print(f"  ✗ Failed to extract metrics for run-{run_id}: {e}")
            failed_runs.append(run_id)
    
    # Generate statistical summaries
    print("\n" + "=" * 70)
    print("  Generating Statistical Summaries")
    print("=" * 70)
    
    generate_statistical_summaries(results_dir)
    
    print("\n" + "=" * 70)
    print("  Multi-Run Complete!")
    print("=" * 70)
    
    return len(failed_runs) == 0

def generate_statistical_summaries(results_dir='results/multi-run'):
    """Generate CSV and TXT statistical summaries."""
    
    # Load all run summaries
    summary_files = glob.glob(f'{results_dir}/run-*-summary.csv')
    
    if not summary_files:
        print(f"✗ No summary files found in {results_dir}")
        return False
    
    print(f"\n✓ Found {len(summary_files)} summary files")
    
    # Combine all runs
    all_runs = []
    for file in sorted(summary_files):
        try:
            df = pd.read_csv(file)
            all_runs.append(df)
        except Exception as e:
            print(f"  ⚠️  Could not read {file}: {e}")
    
    if not all_runs:
        print("✗ No valid summary files could be read")
        return False
    
    combined_df = pd.concat(all_runs, ignore_index=True)
    num_runs = len(combined_df)
    
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
    generate_baseline_summary(results_df, combined_df)
    
    return True

def generate_baseline_summary(results_df, combined_df):
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
    success = run_baseline_multirun(num_runs=30)
    sys.exit(0 if success else 1)
