#!/usr/bin/env python3
"""Extract key metrics from a single simulation run."""

import pandas as pd
import argparse
import os
import sys

def extract_single_run_metrics(run_id, input_dir, output_file):
    """Extract metrics from one run and save to CSV."""
    
    metrics = {'run_id': run_id}
    
    try:
        # Network lifetime metrics
        network_df = pd.read_csv(f'{input_dir}/network.csv')
        # Use dynamic threshold: FND is when nodes drop below initial count
        initial_nodes = network_df['AliveNodes'].iloc[0]
        fnd_row = network_df[network_df['AliveNodes'] < initial_nodes]
        
        if not fnd_row.empty:
            fnd_row = fnd_row.iloc[0]
            metrics['FND'] = int(fnd_row['Round'])
        else:
            metrics['FND'] = -1  # No node deaths
        
        lnd_row = network_df[network_df['AliveNodes'] == 0]
        if not lnd_row.empty:
            lnd_row = lnd_row.iloc[0]
            metrics['LND'] = int(lnd_row['Round'])
        else:
            metrics['LND'] = len(network_df)  # Simulation ended before LND
        
        metrics['Lifetime'] = metrics['LND'] - metrics['FND'] if metrics['FND'] > 0 else metrics['LND']
        
        # Calculate HNA (Half Nodes Alive) - dynamic threshold
        hna_threshold = initial_nodes // 2
        hna_df = network_df[network_df['AliveNodes'] <= hna_threshold]
        metrics['HNA'] = int(hna_df.iloc[0]['Round']) if not hna_df.empty else metrics['LND']
        
        # Energy metrics
        energy_df = pd.read_csv(f'{input_dir}/energy.csv')
        metrics['TotalEnergy_J'] = energy_df['EnergyConsumed'].sum()
        metrics['MeanEnergyPerRound_J'] = energy_df['EnergyConsumed'].mean()
        metrics['StdEnergyPerRound_J'] = energy_df['EnergyConsumed'].std()
        
        # PDR metrics
        pdr_df = pd.read_csv(f'{input_dir}/pdr.csv')
        metrics['MeanPDR'] = pdr_df['PDR'].mean()
        metrics['StdPDR'] = pdr_df['PDR'].std()
        metrics['MinPDR'] = pdr_df['PDR'].min()
        metrics['MaxPDR'] = pdr_df['PDR'].max()
        
        # Delay metrics
        delay_df = pd.read_csv(f'{input_dir}/delay.csv')
        metrics['MeanDelay_s'] = delay_df['Delay_s'].mean()
        metrics['MedianDelay_s'] = delay_df['Delay_s'].median()
        metrics['StdDelay_s'] = delay_df['Delay_s'].std()
        metrics['P95Delay_s'] = delay_df['Delay_s'].quantile(0.95)
        
        # Clustering metrics
        clustering_df = pd.read_csv(f'{input_dir}/clustering.csv')
        chs_per_round = clustering_df.groupby('Round')['ClusterID'].count()
        unclustered_per_round = clustering_df.groupby('Round')['UnclusteredNodes'].first()
        
        metrics['MeanCHs'] = chs_per_round.mean()
        metrics['StdCHs'] = chs_per_round.std()
        metrics['MeanUnclusteredNodes'] = unclustered_per_round.mean()
        metrics['UnclusteredPercent'] = (unclustered_per_round.mean() / 100) * 100
        
        # Throughput metrics
        throughput_df = pd.read_csv(f'{input_dir}/throughput.csv')
        metrics['MeanThroughput_bps'] = throughput_df['Throughput_bps'].mean()
        metrics['PeakThroughput_bps'] = throughput_df['Throughput_bps'].max()
        metrics['ZeroThroughputRounds'] = (throughput_df['Throughput_bps'] == 0).sum()
        metrics['ZeroThroughputPercent'] = (metrics['ZeroThroughputRounds'] / len(throughput_df)) * 100
        
        # UAV contact metrics
        contact_df = pd.read_csv(f'{input_dir}/contact.csv')
        metrics['TotalContacts'] = len(contact_df)
        metrics['ContactSuccessRate'] = (contact_df['Successful'] == 'Yes').sum() / len(contact_df) if len(contact_df) > 0 else 0
        metrics['MeanContactDuration_s'] = contact_df['Duration_s'].mean()
        metrics['StdContactDuration_s'] = contact_df['Duration_s'].std()
        
        # Overhead metrics
        overhead_df = pd.read_csv(f'{input_dir}/overhead.csv')
        metrics['MeanControlRatio'] = overhead_df['ControlRatio'].mean()
        metrics['TotalControlPackets'] = overhead_df['ControlPackets'].sum()
        metrics['TotalDataPackets'] = overhead_df['DataPackets'].sum()
        
        # Save to CSV
        df = pd.DataFrame([metrics])
        df.to_csv(output_file, index=False)
        
        print(f"✓ Metrics extracted for run {run_id}")
        print(f"  FND: {metrics['FND']}, LND: {metrics['LND']}, PDR: {metrics['MeanPDR']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error extracting metrics for run {run_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Backward compatible CLI behavior:
    # - New style: --run-id --input-dir --output
    # - Legacy style: extract_metrics.py <input_dir>
    if len(sys.argv) == 2 and not sys.argv[1].startswith('--'):
        input_dir = sys.argv[1]
        output_file = os.path.join(input_dir, 'metrics_summary.csv')
        success = extract_single_run_metrics(0, input_dir, output_file)
        sys.exit(0 if success else 1)

    parser = argparse.ArgumentParser(description='Extract metrics from simulation run')
    parser.add_argument('--run-id', type=int, required=True, help='Run ID number')
    parser.add_argument('--input-dir', required=True, help='Directory with result CSVs')
    parser.add_argument('--output', required=True, help='Output CSV file')

    args = parser.parse_args()
    success = extract_single_run_metrics(args.run_id, args.input_dir, args.output)
    sys.exit(0 if success else 1)
