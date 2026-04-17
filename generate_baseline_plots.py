#!/usr/bin/env python3
"""
Generate plots for baseline S0 scenario
Matches the professional style and format of generate_plots.py exactly
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# Match generate_plots.py style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 16
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['grid.color'] = '#d0d0d0'
plt.rcParams['grid.alpha'] = 0.5
plt.rcParams['grid.linewidth'] = 1.2
plt.rcParams['axes.linewidth'] = 1.8
plt.rcParams['axes.edgecolor'] = '#2d2d2d'


def plot_network_lifetime(stability_df, plots_dir):
    """Plot network lifetime with both alive and dead nodes - matching generate_plots.py"""
    print("  Generating Network Lifetime plot...")
    
    plot_max_round = int(stability_df['Round'].max())
    
    # Extend plot to show full LND period if needed
    if len(stability_df) < plot_max_round:
        last_alive = int(stability_df.iloc[-1]['AliveNodes'])
        last_dead = int(stability_df.iloc[-1]['DeadNodes'])
        extended_rounds = list(range(int(stability_df.iloc[-1]['Round']) + 1, plot_max_round + 1))
        extended_data = pd.DataFrame({
            'Round': extended_rounds,
            'AliveNodes': [last_alive] * len(extended_rounds),
            'DeadNodes': [last_dead] * len(extended_rounds)
        })
        plot_df = pd.concat([stability_df, extended_data], ignore_index=True)
    else:
        plot_df = stability_df[stability_df['Round'] <= plot_max_round].copy()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(plot_df['Round'], plot_df['AliveNodes'], 
            linewidth=2.2, color='#2E86AB', label='Alive Nodes')
    ax.plot(plot_df['Round'], plot_df['DeadNodes'], 
            linewidth=2.2, color='#A23B72', linestyle='--', label='Dead Nodes')
    
    # Mark FND and LND
    fnd_idx = stability_df[stability_df['DeadNodes'] > 0].index[0] if len(stability_df[stability_df['DeadNodes'] > 0]) > 0 else None
    lnd_idx = stability_df[stability_df['AliveNodes'] == 0].index[0] if len(stability_df[stability_df['AliveNodes'] == 0]) > 0 else None
    
    if fnd_idx is not None:
        fnd_round = stability_df.loc[fnd_idx, 'Round']
        ax.axvline(x=fnd_round, color='red', linestyle=':', alpha=0.7, linewidth=2.5, label=f'FND (Round {int(fnd_round)})')
    
    if lnd_idx is not None:
        lnd_round = stability_df.loc[lnd_idx, 'Round']
        if lnd_round <= plot_max_round:
            ax.axvline(x=lnd_round, color='black', linestyle=':', alpha=0.8, linewidth=2.5, label=f'LND (Round {int(lnd_round)})')
            ax.axvspan(lnd_round, plot_max_round, alpha=0.12, color='gray', label='Post-LND period')
    
    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Number of Nodes', fontweight='bold', fontsize=20)
    ax.set_title('Network Lifetime', fontweight='bold', fontsize=22)
    ax.set_xlim(0, plot_max_round)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='best', fontsize=18)
    ax.grid(True, alpha=0.6, linewidth=0.9)
    plt.tight_layout()
    plt.savefig(plots_dir / 'network_lifetime.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ network_lifetime.png")


def plot_energy_consumption(energy_df, plots_dir, lnd_round=None):
    """Plot energy consumption - matching generate_plots.py format"""
    print("  Generating Energy Consumption plot...")
    
    # Filter to LND if provided
    if lnd_round:
        energy_df = energy_df[energy_df['Round'] <= lnd_round + 10].copy()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10))
    
    # Total network energy
    ax1.plot(energy_df['Round'], energy_df['TotalNetworkEnergy'], 
            linewidth=2.5, color='#F18F01')
    ax1.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax1.set_ylabel('Total Network Energy (J)', fontweight='bold', fontsize=20)
    ax1.set_title('Total Residual Energy in Network', fontweight='bold', fontsize=22)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='both', which='major', labelsize=18)
    ax1.grid(True, alpha=0.4, linewidth=0.8)
    
    # Average residual energy per node
    ax2.plot(energy_df['Round'], energy_df['AvgResidualEnergy'], 
            linewidth=2.5, color='#06A77D')
    ax2.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax2.set_ylabel('Average Residual Energy (J/node)', fontweight='bold', fontsize=20)
    ax2.set_title('Average Residual Energy per Node', fontweight='bold', fontsize=22)
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)
    ax2.tick_params(axis='both', which='major', labelsize=18)
    ax2.grid(True, alpha=0.4, linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'energy_consumption.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ energy_consumption.png")


def plot_total_network_energy_consumption(energy_df, plots_dir, lnd_round=None):
    """Plot total network energy consumption per round"""
    print("  Generating Total Network Energy Consumption plot...")

    if lnd_round:
        energy_df = energy_df[energy_df['Round'] <= lnd_round + 10].copy()

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(energy_df['Round'], energy_df['EnergyConsumed'],
            linewidth=2.5, color='#C73E1D')

    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Energy Consumed per Round (J)', fontweight='bold', fontsize=20)
    ax.set_title('Total Network Energy Consumption per Round', fontweight='bold', fontsize=22)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8)

    plt.tight_layout()
    plt.savefig(plots_dir / 'total_energy_consumption_per_round.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ total_energy_consumption_per_round.png")


def plot_cumulative_energy_consumption(energy_df, plots_dir, lnd_round=None):
    """Plot cumulative energy consumption per round"""
    print("  Generating Cumulative Energy Consumption plot...")

    if lnd_round:
        energy_df = energy_df[energy_df['Round'] <= lnd_round + 10].copy()

    cumulative_energy = energy_df['EnergyConsumed'].cumsum()

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(energy_df['Round'], cumulative_energy,
            linewidth=2.5, color='#6A4C93')

    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Cumulative Energy Consumed (J)', fontweight='bold', fontsize=20)
    ax.set_title('Cumulative Network Energy Consumption', fontweight='bold', fontsize=22)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8)

    plt.tight_layout()
    plt.savefig(plots_dir / 'cumulative_energy_consumption.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ cumulative_energy_consumption.png")


def plot_pdr(pdr_df, plots_dir, lnd_round=None):
    """Plot PDR - matching generate_plots.py format"""
    print("  Generating PDR plot...")
    
    if lnd_round:
        pdr_df = pdr_df[pdr_df['Round'] <= lnd_round].copy()
    
    # Filter to meaningful data (rounds with >= 5 packets generated)
    pdr_df = pdr_df[pdr_df['PacketsGenerated'] >= 5].copy()
    
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(pdr_df['Round'], pdr_df['PDR'], 
            linewidth=2.5, color='#2E86AB')
    
    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Packet Delivery Ratio', fontweight='bold', fontsize=20)
    ax.set_title('Packet Delivery Ratio (PDR) Over Time', fontweight='bold', fontsize=22)
    ax.set_xlim(left=0)
    ax.set_ylim([0, 1.05])
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8)
    plt.tight_layout()
    plt.savefig(plots_dir / 'pdr.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ pdr.png")


def plot_throughput(throughput_df, plots_dir, lnd_time=None):
    """Plot network throughput with moving average - matching generate_plots.py"""
    print("  Generating Throughput plot...")
    
    # Filter to LND time if provided
    if lnd_time:
        throughput_df = throughput_df[throughput_df['Time'] <= lnd_time].copy()
    
    # Calculate 20-round moving average for smoothed trend
    window_size = 20
    throughput_df = throughput_df.copy()
    throughput_df['MA_Throughput'] = throughput_df['Throughput_kbps'].rolling(
        window=window_size, center=True, min_periods=1).mean()
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    # Plot raw data (faded)
    ax.plot(throughput_df['Time'], throughput_df['Throughput_kbps'], 
           linewidth=1.2, color='#C73E1D', alpha=0.3, label='Raw throughput')
    
    # Plot moving average (prominent)
    ax.plot(throughput_df['Time'], throughput_df['MA_Throughput'], 
           linewidth=3.0, color='#C73E1D', label=f'{window_size}-round moving average')
    
    ax.set_xlabel('Simulation Time (s)', fontweight='bold', fontsize=20)
    ax.set_ylabel('Throughput (kbps)', fontweight='bold', fontsize=20)
    ax.set_title('Network Throughput Over Time (with Moving Average)', fontweight='bold', fontsize=22)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    # Use scientific notation for x-axis
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    ax.xaxis.get_offset_text().set_fontsize(16)
    
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='best', fontsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8)
    plt.tight_layout()
    plt.savefig(plots_dir / 'throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ throughput.png")


def plot_delay_distribution(delay_df, plots_dir):
    """Plot delay distribution - matching generate_plots.py format"""
    print("  Generating Delay Distribution plot...")
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    # Histogram
    ax.hist(delay_df['Delay_s'], bins=50, color='#FF6B35', alpha=0.7, edgecolor='black', linewidth=1.2)
    
    ax.set_xlabel('Delay (seconds)', fontweight='bold', fontsize=20)
    ax.set_ylabel('Frequency', fontweight='bold', fontsize=20)
    ax.set_title('End-to-End Delay Distribution', fontweight='bold', fontsize=22)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8, axis='y')
    
    # Add statistics
    mean_delay = delay_df['Delay_s'].mean()
    median_delay = delay_df['Delay_s'].median()
    ax.axvline(mean_delay, color='red', linestyle='--', linewidth=2.5, label=f'Mean: {mean_delay:.1f}s')
    ax.axvline(median_delay, color='blue', linestyle='--', linewidth=2.5, label=f'Median: {median_delay:.1f}s')
    ax.legend(fontsize=18, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'delay_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ delay_distribution.png")


def plot_average_delay_per_round(delay_df, plots_dir, lnd_round=None):
    """Plot average delay per round with packet count - matching generate_plots.py"""
    print("  Generating Average Delay per Round plot...")
    
    # Group delays by round (bin by reception time)
    max_time = delay_df['ReceptionTime'].max()
    round_duration = 774  # seconds per round
    num_rounds = int(max_time / round_duration) + 1
    
    if lnd_round and num_rounds > lnd_round:
        num_rounds = lnd_round
    
    # Create round bins
    delay_df = delay_df.copy()
    delay_df['Round'] = (delay_df['ReceptionTime'] // round_duration).astype(int)
    
    # Calculate statistics by round
    delay_by_round = delay_df.groupby('Round').agg({
        'Delay_s': 'mean',
        'PacketID': 'count'
    }).reset_index()
    delay_by_round.columns = ['Round', 'MeanDelay', 'PacketCount']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10))
    
    # Plot 1: Average delay per round
    ax1.plot(delay_by_round['Round'], delay_by_round['MeanDelay'],
            linewidth=2.5, color='#9d4edd', marker='o', markersize=4, markevery=20)
    ax1.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax1.set_ylabel('Average Delay (s)', fontweight='bold', fontsize=20)
    ax1.set_title('Average End-to-End Delay per Round', fontweight='bold', fontsize=22)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='both', which='major', labelsize=18)
    ax1.grid(True, alpha=0.4, linewidth=0.8)
    
    # Plot 2: Packet count per round
    ax2.bar(delay_by_round['Round'], delay_by_round['PacketCount'],
            width=2.0, color='#4c6ef5', alpha=0.7, edgecolor='#1e3a8a', linewidth=0.5)
    ax2.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax2.set_ylabel('Packets Delivered', fontweight='bold', fontsize=20)
    ax2.set_title('Packet Reception Count per Round', fontweight='bold', fontsize=22)
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)
    ax2.tick_params(axis='both', which='major', labelsize=18)
    ax2.grid(True, alpha=0.4, linewidth=0.8, axis='y')
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'average_delay_per_round.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ average_delay_per_round.png")


def plot_clustering_metrics(clustering_df, plots_dir, lnd_round=None):
    """Plot clustering metrics - matching generate_plots.py"""
    print("  Generating Clustering Metrics plot...")
    
    if lnd_round:
        clustering_df = clustering_df[clustering_df['Round'] <= lnd_round].copy()
    
    # Aggregate by round
    clustering_agg = clustering_df.groupby('Round').agg({
        'TotalClusters': 'first',
        'UnclusteredNodes': 'first',
        'AvgMembersPerCluster': 'first'
    }).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10))
    
    # Total clusters per round
    ax1.plot(clustering_agg['Round'], clustering_agg['TotalClusters'], 
            linewidth=2.5, color='#06A77D', marker='o', markersize=3, markevery=20)
    ax1.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax1.set_ylabel('Number of Cluster Heads', fontweight='bold', fontsize=20)
    ax1.set_title('Cluster Head Count per Round', fontweight='bold', fontsize=22)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='both', which='major', labelsize=18)
    ax1.grid(True, alpha=0.4, linewidth=0.8)
    
    # Unclustered nodes
    ax2.plot(clustering_agg['Round'], clustering_agg['UnclusteredNodes'], 
             linewidth=2.5, color='#A23B72', marker='s', markersize=3, markevery=20)
    ax2.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax2.set_ylabel('Number of Unclustered Nodes', fontweight='bold', fontsize=20)
    ax2.set_title('Unclustered Nodes per Round', fontweight='bold', fontsize=22)
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)
    ax2.tick_params(axis='both', which='major', labelsize=18)
    ax2.grid(True, alpha=0.4, linewidth=0.8)

    plt.tight_layout()
    plt.savefig(plots_dir / 'clustering_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ clustering_metrics.png")


def plot_chs_vs_uav_contacts(clustering_df, contact_df, plots_dir, lnd_round=None, round_duration=774):
    """Plot total CHs per round vs UAV-contacted CHs per round"""
    print("  Generating CHs vs UAV Contacts plot...")

    if lnd_round:
        clustering_df = clustering_df[clustering_df['Round'] <= lnd_round].copy()

    # Actual CHs per round from clustering.csv (TotalClusters is round-level)
    chs_per_round = clustering_df.groupby('Round')['TotalClusters'].first()

    # UAV contacts per round from contact.csv
    contact_df = contact_df.copy()
    contact_df = contact_df[contact_df['Successful'].str.lower() == 'yes']
    contact_df['Round'] = (contact_df['StartTime'] // round_duration).astype(int) + 1
    contacts_per_round = contact_df.groupby('Round')['CHID'].nunique()

    # Align rounds
    all_rounds = pd.Index(sorted(chs_per_round.index.unique()), name='Round')
    chs_per_round = chs_per_round.reindex(all_rounds, fill_value=0)
    contacts_per_round = contacts_per_round.reindex(all_rounds, fill_value=0)

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(all_rounds, chs_per_round.values,
            linewidth=2.5, color='#06A77D', marker='o', markersize=3, markevery=20,
            label='Actual CHs')
    ax.plot(all_rounds, contacts_per_round.values,
            linewidth=2.5, color='#1C7ED6', marker='s', markersize=3, markevery=20,
            label='CHs Contacted by UAV')

    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Number of CHs', fontweight='bold', fontsize=20)
    ax.set_title('CHs per Round vs UAV Contacts', fontweight='bold', fontsize=22)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='best', fontsize=16)
    ax.grid(True, alpha=0.4, linewidth=0.8)

    plt.tight_layout()
    plt.savefig(plots_dir / 'chs_vs_uav_contacts.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ chs_vs_uav_contacts.png")


def plot_contact_time_vs_collection_time(contact_df, clustering_df, plots_dir, target_round=4, 
                                            round_duration=774, data_rate_bps=100000, packet_size_bits=2000):
    """Plot T_c (contact time) and T_req (required collection time) for a specific round.
    
    X-axis: Cluster Head IDs
    Y-axis: Time (seconds)
    T_c: Actual contact time from contact.csv
    T_req: Analytical required transfer time based on aggregated packets
    
    NOTE: Uses 100 kbps (100000 bps) as practical CH-to-UAV data rate.
    Justification: Sensor nodes use IEEE 802.15.4 (~250 kbps max physical layer).
    Practical throughput ~100 kbps accounting for MAC overhead, collisions, retransmissions.
    NOT 2 Mbps (UAV's receiver rate) - the bottleneck is the CH's transmission, not UAV's reception.
    """
    print(f"  Generating Contact Time vs Collection Time plot (Round {target_round}, dataRate={data_rate_bps/1000:.0f}kbps)...")
    
    # Calculate round time boundaries
    round_start = (target_round - 1) * round_duration
    round_end = target_round * round_duration
    
    # Filter contact data for this round
    contacts_round = contact_df[
        (contact_df['StartTime'] >= round_start) & 
        (contact_df['StartTime'] < round_end) &
        (contact_df['Successful'].str.lower() == 'yes')
    ].copy()
    
    if len(contacts_round) == 0:
        print(f"    ⚠️ No successful contacts for round {target_round}; skipping")
        return
    
    # Filter clustering data for this round
    clustering_round = clustering_df[clustering_df['Round'] == target_round].copy()
    
    if len(clustering_round) == 0:
        print(f"    ⚠️ No clustering data for round {target_round}; skipping")
        return
    
    # Create mapping: CH ID -> ExpectedMembers
    ch_members = {}
    for _, row in clustering_round.iterrows():
        ch_members[int(row['ClusterID'])] = int(row['ExpectedMembers'])
    
    # Prepare data for plotting
    ch_ids = []
    tc_values = []
    treq_values = []
    
    for _, contact in contacts_round.iterrows():
        ch_id = int(contact['CHID'])
        tc = float(contact['Duration_s'])
        
        # Get expected members for this CH
        expected_members = ch_members.get(ch_id, 0)
        
        # Calculate T_req = (packets * packet_size) / data_rate
        # packets = expected_members (each member sends one packet)
        packet_count = expected_members
        treq = (packet_count * packet_size_bits) / data_rate_bps
        
        ch_ids.append(ch_id)
        tc_values.append(tc)
        treq_values.append(treq)
    
    # Sort by CH ID for cleaner x-axis
    sorted_indices = np.argsort(ch_ids)
    ch_ids_sorted = [ch_ids[i] for i in sorted_indices]
    tc_sorted = [tc_values[i] for i in sorted_indices]
    treq_sorted = [treq_values[i] for i in sorted_indices]
    
    # Create x-axis labels as "ch1", "ch2", etc.
    ch_labels = [f"ch{cid}" for cid in ch_ids_sorted]
    x_pos = np.arange(len(ch_labels))
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 7))
    
    width = 0.35
    bars1 = ax.bar(x_pos - width/2, tc_sorted, width, label='Contact Time (T_c)', 
                   color='#06A77D', alpha=0.8, edgecolor='#055a4f', linewidth=1.2)
    bars2 = ax.bar(x_pos + width/2, treq_sorted, width, label='Required Collection Time (T_req)', 
                   color='#1C7ED6', alpha=0.8, edgecolor='#0a47a9', linewidth=1.2)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}s',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Cluster Head ID', fontweight='bold', fontsize=20)
    ax.set_ylabel('Time (seconds)', fontweight='bold', fontsize=20)
    ax.set_title(f'Contact Time vs Required Collection Time (Round {target_round})\n' + 
                 f'Data Rate: {data_rate_bps/1000:.0f} kbps (IEEE 802.15.4 practical throughput)',
                fontweight='bold', fontsize=22)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(ch_labels, rotation=45, ha='right')
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.legend(loc='best', fontsize=16)
    ax.grid(True, alpha=0.4, linewidth=0.8, axis='y')
    
    plt.tight_layout()
    plt.savefig(plots_dir / f'contact_vs_collection_time_round{target_round}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    ✓ contact_vs_collection_time_round{target_round}.png")


def plot_control_overhead(overhead_df, plots_dir, lnd_round=None):
    """Plot control overhead - matching generate_plots.py"""
    print("  Generating Control Overhead plot...")
    
    if lnd_round:
        overhead_df = overhead_df[overhead_df['Round'] <= lnd_round].copy()
    
    # Filter to valid rounds
    valid_rounds = overhead_df[(overhead_df['ControlPackets'] + overhead_df['DataPackets']) >= 50].copy()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(overhead_df['Round'], overhead_df['ControlRatio'], 
           linewidth=1.5, color='#999999', alpha=0.4, label='All Rounds (including degradation)')
    ax.plot(valid_rounds['Round'], valid_rounds['ControlRatio'], 
           linewidth=2.2, color='#E63946', label='Stable Network (≥50 total packets/round)')
    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Control Packet Ratio', fontweight='bold', fontsize=20)
    ax.set_title('Control Packet Overhead (Ratio of Control to Total Packets)', fontweight='bold', fontsize=22)
    ax.set_ylim([0, 1])
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='best', fontsize=16)
    ax.grid(True, alpha=0.5, linewidth=0.8)
    
    # Add annotation for network degradation
    if len(valid_rounds) < len(overhead_df):
        last_valid_round = valid_rounds['Round'].max()
        ax.axvline(x=last_valid_round, color='red', linestyle='--', linewidth=1.5, alpha=0.6)
        ax.text(last_valid_round, 0.95, f'  Network\n  Degradation\n  ({int(last_valid_round)}+)', 
               fontsize=9, verticalalignment='top', color='red', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(plots_dir / 'control_overhead.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    ✓ control_overhead.png")


def generate_baseline_plots(results_dir='results/scenarios/S0-Baseline', plots_dir='plots/scenarios/S0-Baseline'):
    """Generate all plots for baseline scenario matching generate_plots.py style"""
    
    results_path = Path(results_dir)
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # Load all data
    stability = pd.read_csv(results_path / 'stability.csv')
    energy = pd.read_csv(results_path / 'energy.csv')
    pdr = pd.read_csv(results_path / 'pdr.csv')
    throughput = pd.read_csv(results_path / 'throughput.csv')
    delay = pd.read_csv(results_path / 'delay.csv')
    clustering = pd.read_csv(results_path / 'clustering.csv')
    contact = pd.read_csv(results_path / 'contact.csv')
    overhead = pd.read_csv(results_path / 'overhead.csv')
    
    # Get LND metrics for filtering
    metrics = pd.read_csv(results_path / 'metrics_summary.csv')
    m = metrics.iloc[0]
    lnd_round = int(m['LND'])
    
    # Get LND time from stability data
    lnd_row = stability[stability['AliveNodes'] == 0]
    if len(lnd_row) > 0:
        lnd_time = float(lnd_row['Time'].iloc[0])
    else:
        lnd_time = None
    
    print("\n" + "=" * 60)
    print("Baseline S0 Plot Generation")
    print("=" * 60)
    
    # Generate all plots
    plot_network_lifetime(stability, plots_dir)
    plot_energy_consumption(energy, plots_dir, lnd_round)
    plot_total_network_energy_consumption(energy, plots_dir, lnd_round)
    plot_cumulative_energy_consumption(energy, plots_dir, lnd_round)
    plot_pdr(pdr, plots_dir, lnd_round)
    plot_throughput(throughput, plots_dir, lnd_time)
    plot_delay_distribution(delay, plots_dir)
    plot_average_delay_per_round(delay, plots_dir, lnd_round)
    plot_clustering_metrics(clustering, plots_dir, lnd_round)
    plot_chs_vs_uav_contacts(clustering, contact, plots_dir, lnd_round)
    plot_contact_time_vs_collection_time(contact, clustering, plots_dir, target_round=4)
    plot_control_overhead(overhead, plots_dir, lnd_round)
    
    print("=" * 60)
    print(f"✓ All plots saved to {plots_dir}/")
    print("\nNote: Differences between S0-Baseline and old plots/ are EXPECTED:")
    print("  - S0-Baseline: Single run (seed=1)")
    print("  - Old plots/: Averaged across 30 multi-run baseline seeds")
    print("  - Variation is natural and reflects stochastic simulation behavior")
    print("=" * 60)
    

if __name__ == '__main__':
    import sys
    arg1 = sys.argv[1] if len(sys.argv) > 1 else 'results/scenarios/S0-Baseline'
    arg2 = sys.argv[2] if len(sys.argv) > 2 else None

    # Allow: python3 generate_baseline_plots.py plots
    # Treat single arg ending in 'plots' as output dir and use default results.
    if arg2 is None and Path(arg1).name == 'plots':
        generate_baseline_plots('results/scenarios/S0-Baseline', arg1)
    else:
        results_dir = arg1
        plots_dir = arg2 if arg2 is not None else 'plots/scenarios/S0-Baseline'
        generate_baseline_plots(results_dir, plots_dir)
