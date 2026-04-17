#!/usr/bin/env python3
"""
UAV-WSN-BM Simulation Results Plotter
Generates all required plots from CSV output files
"""

import pandas as pd
import matplotlib.pyplot as plt
from contextlib import contextmanager
import numpy as np
from matplotlib.patches import Rectangle
import os
import sys


# Set style for publication-quality plots
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
plt.rcParams['agg.path.chunksize'] = 10000
plt.rcParams['path.simplify'] = True
plt.rcParams['path.simplify_threshold'] = 0.5


def get_lnd_round():
    """Get Last Node Death round from stability data"""
    try:
        stability_df = pd.read_csv('results/stability.csv')
        lnd_row = stability_df[stability_df['AliveNodes'] == 0]
        if len(lnd_row) > 0:
            return int(lnd_row['Round'].iloc[0])
    except:
        pass
    return None


def plot_topology_map(topology_df, bs_pos=(-100, 250), area_x=500, area_y=500, sensor_comm_radius=100, ch_comm_radius=50, uav_comm_radius=150):
    """
    Simplified topology plot showing:
    - Initial deployment of sensor nodes
    - UAV positioned between BS and network center (outside network)
    - UAV communication range circle
    - Sample sensor nodes with communication range circles
    - Distance between BS and network center
    - Entire network area visible
    """
    print("📊 Generating Topology map...")

    center_x, center_y = area_x / 2.0, area_y / 2.0
    bs_center_dist = np.hypot(bs_pos[0] - center_x, bs_pos[1] - center_y)
    
    # Position UAV at BS position (will be drawn on top)
    uav_x = bs_pos[0]
    uav_y = bs_pos[1]

    fig, ax = plt.subplots(figsize=(13, 12))
    
    # === White background for whole area ===
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    # === Network field boundary with light cyan background ===
    field_rect = Rectangle((0, 0), area_x, area_y, linewidth=2.5, edgecolor='#2d3436', 
                           facecolor='#e0f7ff', alpha=0.4, linestyle='-', zorder=1)
    ax.add_patch(field_rect)
    ax.text(area_x/2, -25, f'WSN Field: {int(area_x)}m × {int(area_y)}m', ha='center', 
            fontsize=11, fontweight='bold', color='#2d3436')
    ax.text(-30, area_y/2, f'{int(area_y)}m', ha='right', va='center', fontsize=10, 
            color='#2d3436', rotation=90)
    ax.text(area_x/2, -50, f'{int(area_x)}m', ha='center', fontsize=10, color='#2d3436')

    # === Grid lines for the network area (light gray) ===
    grid_spacing = 50  # 50m grid
    for x in np.arange(0, area_x + 1, grid_spacing):
        ax.axvline(x=x, color='#b0b0b0', linewidth=1.0, linestyle=':', alpha=0.8, zorder=1)
    for y in np.arange(0, area_y + 1, grid_spacing):
        ax.axhline(y=y, color='#b0b0b0', linewidth=1.0, linestyle=':', alpha=0.8, zorder=1)

    # === Sensor nodes ===
    ax.scatter(topology_df['X'], topology_df['Y'], s=20, c='#4c6ef5', alpha=0.65, 
               marker='o', label='Sensor Nodes', zorder=3, edgecolors='#1e3a8a', linewidths=0.5)

    # === Select 4 well-distributed sensor nodes to show communication range ===
    # Divide network into quadrants and select one node from each
    sample_indices = []
    quadrants = [
        (topology_df['X'] < center_x) & (topology_df['Y'] < center_y),  # Bottom-left
        (topology_df['X'] >= center_x) & (topology_df['Y'] < center_y),  # Bottom-right
        (topology_df['X'] < center_x) & (topology_df['Y'] >= center_y),  # Top-left
        (topology_df['X'] >= center_x) & (topology_df['Y'] >= center_y)  # Top-right
    ]
    
    np.random.seed(456)  # For reproducibility
    for quadrant_mask in quadrants:
        quadrant_nodes = topology_df[quadrant_mask]
        if len(quadrant_nodes) > 0:
            idx = np.random.choice(quadrant_nodes.index)
            sample_indices.append(idx)
    
    for idx in sample_indices:
        node_x = topology_df.loc[idx, 'X']
        node_y = topology_df.loc[idx, 'Y']
        
        # Draw communication range circle
        node_circle = plt.Circle((node_x, node_y), sensor_comm_radius, color='#4c6ef5', 
                                fill=False, linestyle=':', linewidth=1.5, alpha=0.5, zorder=4)
        ax.add_patch(node_circle)
        
        # Draw radius line (horizontal to the right for clarity)
        ax.plot([node_x, node_x + sensor_comm_radius], [node_y, node_y], 
               color='#4c6ef5', linewidth=2, alpha=0.7, zorder=5)
        
        # Add radius label at midpoint
        mid_x = node_x + sensor_comm_radius / 2
        ax.text(mid_x, node_y + 10, f'{sensor_comm_radius}m', ha='center', 
               fontsize=9, fontweight='bold', color='#1e3a8a',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='#4c6ef5', linewidth=1))
    
    # Add legend entry for sensor comm range (only once)
    sensor_circle_legend = plt.Circle((0, 0), 1, color='#4c6ef5', fill=False, 
                                     linestyle=':', linewidth=1.5, alpha=0.5)
    ax.add_patch(sensor_circle_legend)

    # === Base station ===
    ax.scatter(bs_pos[0], bs_pos[1], s=420, c='#2b8a3e', marker='s', edgecolors='#1b4620', 
               linewidths=2.5, zorder=7, label='Base Station')
    ax.text(bs_pos[0], bs_pos[1] - 40, f'BS\n({int(bs_pos[0])},{int(bs_pos[1])})', ha='center', fontsize=10, 
            fontweight='bold', color='#2b8a3e', bbox=dict(boxstyle='round,pad=0.4', 
            facecolor='#d4edda', alpha=0.95, edgecolor='#1b4620', linewidth=1.5))

    # === UAV position with comm range circle ===
    ax.scatter(uav_x, uav_y, s=340, c='#ffd43b', marker='^', edgecolors='#f08c00', 
              linewidths=2.5, zorder=8, label='UAV')
    uav_circle = plt.Circle((uav_x, uav_y), uav_comm_radius, color='#ffd43b', fill=False, 
                            linestyle='-.', linewidth=2.2, alpha=0.7, zorder=4, 
                            label=f'UAV Comm Range ({uav_comm_radius}m)')
    ax.add_patch(uav_circle)
    ax.text(uav_x, uav_y + 35, f'UAV\n({int(uav_x)},{int(uav_y)})', ha='center', fontsize=9, fontweight='bold', 
           color='#f08c00', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff9e6', alpha=0.95, edgecolor='#f08c00', linewidth=1.5))

    # === Network center and BS-center distance ===
    ax.scatter(center_x, center_y, s=160, c='#5f3dc4', marker='+', linewidths=3.5, zorder=4, 
              label='Network Center')
    ax.text(center_x, center_y + 30, 'Center\n(250,250)', ha='center', fontsize=9, 
           fontweight='bold', color='#5f3dc4', bbox=dict(boxstyle='round,pad=0.3', 
           facecolor='#f3e5ff', alpha=0.95, edgecolor='#5f3dc4', linewidth=1.5))
    
    # Line from BS to center
    ax.plot([bs_pos[0], center_x], [bs_pos[1], center_y], 'k--', alpha=0.5, linewidth=1.8, zorder=2)
    
    # Distance annotation
    mid_x, mid_y = (bs_pos[0] + center_x) / 2, (bs_pos[1] + center_y) / 2
    ax.annotate(f'BS-Center\nDistance:\n{bs_center_dist:.1f}m', 
               xy=(mid_x, mid_y), xytext=(mid_x + 90, mid_y - 50),
               fontsize=10, fontweight='bold', color='#000000',
               bbox=dict(boxstyle='round,pad=0.6', facecolor='#ffeb3b', alpha=0.98, edgecolor='#f57f17', linewidth=2),
               arrowprops=dict(arrowstyle='->', lw=2.5, color='#000000'))
    
    # Add sensor comm range to legend
    ax.plot([], [], color='#4c6ef5', linestyle=':', linewidth=1.5, alpha=0.5, 
            label=f'Sensor Comm Range ({sensor_comm_radius}m)')

    # === Labels and styling ===
    ax.set_xlabel('X Position (meters)', fontsize=20, fontweight='bold')
    ax.set_ylabel('Y Position (meters)', fontsize=20, fontweight='bold')
    ax.set_title('UAV-WSN Network Topology: Initial Deployment', 
                fontsize=22, fontweight='bold', pad=20)
    
    # Increase tick label sizes
    ax.tick_params(axis='both', which='major', labelsize=18)
    
    # Legend
    ax.legend(loc='upper left', fontsize=18, framealpha=0.98, edgecolor='#2d3436', 
             fancybox=True, shadow=True, markerscale=1.1)
    
    # Aspect and limits - show entire network area
    ax.set_aspect('equal', adjustable='box')
    margin = 60
    ax.set_xlim(bs_pos[0] - margin, area_x + margin)
    ax.set_ylim(-margin, area_y + margin)
    
    plt.tight_layout()
    plt.savefig('plots/network_topology_map.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("   ✓ Saved: plots/network_topology_map.png")



def plot_round_topology(topology_df, clustering_df, network_df, round_num=1, bs_pos=(-50, 250), area_x=500, area_y=500, uav_comm_radius=150, ch_comm_radius=100, only_alive_and_chs=False):
    """Round-specific topology map highlighting CHs for the selected round with Random Waypoint UAV model.
    If only_alive_and_chs is True, plot only alive nodes and CHs for the round."""
    round_clusters = clustering_df[clustering_df['Round'] == round_num]
    if len(round_clusters) == 0:
        print(f"   ⚠️ No clustering data for round {round_num}; skipping round topology map")
        return

    ch_ids = [int(c) for c in round_clusters['ClusterID'].unique() if str(c) != 'nan']
    unclustered = int(round_clusters['UnclusteredNodes'].iloc[0]) if 'UnclusteredNodes' in round_clusters else None

    # Filter alive nodes if requested
    plot_df = topology_df.copy()
    if only_alive_and_chs and network_df is not None:
        alive_row = network_df[network_df['Round'] == round_num]
        if not alive_row.empty:
            alive_count = int(alive_row['AliveNodes'].iloc[0])
            # Assume alive nodes are NodeID 0 to alive_count-1 (if no per-node status is available)
            plot_df = plot_df[plot_df['NodeID'] < alive_count]
        else:
            print(f"   ⚠️ No network data for round {round_num}; cannot filter alive nodes.")

    fig, ax = plt.subplots(figsize=(12, 11))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    # WSN work area (Random Waypoint model: [0, 500] x [0, 500])
    field_rect = Rectangle((0, 0), area_x, area_y, linewidth=2.5, edgecolor='#2d3436', facecolor='#e0f7ff', alpha=0.35, zorder=1)
    ax.add_patch(field_rect)
    ax.text(area_x/2, -25, f'UAV Work Area: {int(area_x)}m × {int(area_y)}m (Random Waypoint Model)', ha='center', 
            fontsize=11, fontweight='bold', color='#2d3436')

    # Grid overlay for spatial reference
    grid_spacing = 50  # 50m grid
    for x in np.arange(0, area_x + 1, grid_spacing):
        ax.axvline(x=x, color='#b0b0b0', linewidth=0.8, linestyle=':', alpha=0.6, zorder=1)
    for y in np.arange(0, area_y + 1, grid_spacing):
        ax.axhline(y=y, color='#b0b0b0', linewidth=0.8, linestyle=':', alpha=0.6, zorder=1)

    # Sensor nodes (filtered)
    ax.scatter(plot_df['X'], plot_df['Y'], s=18, c='#4c6ef5', alpha=0.7, marker='o', label='Alive Sensors' if only_alive_and_chs else 'Sensors', zorder=2, edgecolors='#1e3a8a', linewidths=0.5)

    # Cluster heads for this round
    ch_positions = plot_df[plot_df['NodeID'].isin(ch_ids)]
    if len(ch_positions) > 0:
        ax.scatter(ch_positions['X'], ch_positions['Y'], s=260, c='#ff6b6b', marker='*', edgecolors='#c92a2a', linewidths=2.0, zorder=4, label=f'CHs (round {round_num})')
        # CH coverage circles
        for _, row in ch_positions.iterrows():
            circle = plt.Circle((row['X'], row['Y']), ch_comm_radius, color='#ff6b6b', fill=False, linestyle=':', linewidth=1.5, alpha=0.65, zorder=3)
            ax.add_patch(circle)

    # UAV communication range (for reference)
    uav_range = plt.Circle((area_x/2, area_y/2), uav_comm_radius, color='#1c7ed6', fill=False, linestyle='--', linewidth=1.5, alpha=0.4, zorder=2, label=f'UAV range ({uav_comm_radius}m)')
    ax.add_patch(uav_range)

    # Base Station
    ax.scatter(bs_pos[0], bs_pos[1], s=380, c='#2b8a3e', marker='s', edgecolors='#1b4620', linewidths=2.2, zorder=5, label='Base Station')
    ax.text(bs_pos[0], bs_pos[1] - 30, f'BS\n({int(bs_pos[0])},{int(bs_pos[1])})', ha='center', fontsize=9, fontweight='bold', color='#2b8a3e', bbox=dict(boxstyle='round,pad=0.3', facecolor='#d4edda', alpha=0.95, edgecolor='#1b4620', linewidth=1.2))

    # Unclustered annotation
    if unclustered is not None:
        ax.text(area_x - 20, area_y + 20, f'Unclustered nodes: {unclustered}', ha='right', fontsize=10, fontweight='bold', color='#2d3436')

    ax.set_xlabel('X Position (m)', fontsize=20, fontweight='bold')
    ax.set_ylabel('Y Position (m)', fontsize=20, fontweight='bold')
    ax.set_title(f'Round {round_num} Topology: Alive Nodes & CHs', fontsize=22, fontweight='bold', pad=15) if only_alive_and_chs else ax.set_title(f'Round {round_num} Topology: Cluster Heads & Random Waypoint UAV Model', fontsize=22, fontweight='bold', pad=15)
    margin = 60
    ax.set_xlim(bs_pos[0] - margin, area_x + margin)
    ax.set_ylim(-margin, area_y + margin)
    ax.set_aspect('equal', adjustable='box')
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='upper left', fontsize=18, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle=':')

    plt.tight_layout()
    out_path = f'plots/network_topology_round{round_num}.png' if not only_alive_and_chs else f'plots/network_topology_round{round_num}_alive.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✓ Saved: {out_path}")


def plot_uav_trajectory_round(topology_df, network_df, clustering_df=None, round_num=1, bs_pos=(-100, 250), area_x=500, area_y=500, uav_comm_radius=150, ch_comm_radius=100):
    """Plot UAV trajectory for the round, showing actual path with sampled contact points."""
    if network_df is None or len(network_df) == 0:
        print(f"   ⚠️ No network timing data available for round {round_num}; skipping UAV trajectory plot")
        return

    if not os.path.exists('results/uav_trajectory.csv'):
        print("   ⚠️ UAV trajectory file not found; skipping round-specific trajectory plot")
        return

    sorted_net = network_df.sort_values('Round')
    round_row = sorted_net[sorted_net['Round'] == round_num]
    if round_row.empty:
        print(f"   ⚠️ No network data for round {round_num}; skipping UAV trajectory plot")
        return

    end_time = float(round_row.iloc[0]['Time'])
    prev_rows = sorted_net[sorted_net['Round'] < round_num]
    start_time = float(prev_rows.iloc[-1]['Time']) if len(prev_rows) > 0 else 0.0

    try:
        traj = pd.read_csv('results/uav_trajectory.csv')
    except Exception as e:
        print(f"   ⚠️ Could not load UAV trajectory: {e}")
        return

    if not {'Time', 'X', 'Y'}.issubset(traj.columns):
        print("   ⚠️ UAV trajectory file missing required columns; skipping")
        return

    traj = traj.dropna(subset=['Time', 'X', 'Y'])
    round_traj = traj[(traj['Time'] >= start_time) & (traj['Time'] <= end_time)]
    if len(round_traj) == 0:
        print(f"   ⚠️ No UAV trajectory samples within round {round_num} window ({start_time:.2f}s-{end_time:.2f}s)")
        return

    # Filter to WAYPOINT and ENTER_NETWORK events for the actual path (no CH contacts which spam every ~0.5-1s)
    path_events = round_traj[round_traj['Event'].fillna('').str.contains('WAYPOINT|ENTER_NETWORK', case=False, na=False)].copy()
    if len(path_events) == 0:
        print(f"   ⚠️ No WAYPOINT/ENTER_NETWORK samples in round {round_num}; showing all trajectory events")
        path_events = round_traj.copy()
    else:
        # Use all WAYPOINT/ENTER_NETWORK events within the round window (don't truncate)
        pass
    
    # Add BS starting position at the beginning (UAV starts at BS before entering network)
    bs_start = pd.DataFrame({'Time': [start_time - 1], 'X': [bs_pos[0]], 'Y': [bs_pos[1]], 'Z': [30], 'Event': ['START_AT_BASE']})
    path_events = pd.concat([bs_start, path_events], ignore_index=True).sort_values('Time').reset_index(drop=True)
    
    # Add BS ending position at the end (UAV returns to BS after leaving network)
    bs_end = pd.DataFrame({'Time': [end_time + 1], 'X': [bs_pos[0]], 'Y': [bs_pos[1]], 'Z': [30], 'Event': ['RETURN_TO_BASE']})
    path_events = pd.concat([path_events, bs_end], ignore_index=True).sort_values('Time').reset_index(drop=True)

    path_length = float(np.sum(np.sqrt(np.diff(path_events['X'])**2 + np.diff(path_events['Y'])**2))) if len(path_events) > 1 else 0.0

    # Sample contact points at most every 5 seconds to avoid clutter
    contact_points = []
    if 'Event' in round_traj.columns:
        ch_contacts = round_traj[round_traj['Event'].fillna('').str.contains('CH_', case=False, na=False)].copy()
        if len(path_events) > 0:
            visit_end = path_events['Time'].max()
            ch_contacts = ch_contacts[ch_contacts['Time'] <= visit_end]
        if len(ch_contacts) > 0:
            # Subsample to every 5 seconds to reduce clutter
            ch_contacts['TimeRounded'] = (ch_contacts['Time'] / 5.0).astype(int) * 5.0
            contact_points = ch_contacts.drop_duplicates(subset='TimeRounded')[['X', 'Y']].values.tolist()

    # Prepare CH overlays
    ch_positions = None
    if clustering_df is not None:
        round_clusters = clustering_df[clustering_df['Round'] == round_num]
        ch_ids = [int(c) for c in round_clusters['ClusterID'].unique() if str(c) != 'nan']
        ch_positions = topology_df[topology_df['NodeID'].isin(ch_ids)] if len(ch_ids) > 0 else None

    fig, ax = plt.subplots(figsize=(12, 11))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    # Field boundary (work area for random waypoint model)
    field_rect = Rectangle((0, 0), area_x, area_y, linewidth=2.0, edgecolor='#2d3436', facecolor='#e0f7ff', alpha=0.35, zorder=1)
    ax.add_patch(field_rect)

    # Grid overlay for spatial reference
    grid_spacing = 50  # 50m grid
    for x in np.arange(0, area_x + 1, grid_spacing):
        ax.axvline(x=x, color='#b0b0b0', linewidth=0.7, linestyle=':', alpha=0.5, zorder=1)
    for y in np.arange(0, area_y + 1, grid_spacing):
        ax.axhline(y=y, color='#b0b0b0', linewidth=0.7, linestyle=':', alpha=0.5, zorder=1)

    # Sensor backdrop for context
    ax.scatter(topology_df['X'], topology_df['Y'], s=14, c='#4c6ef5', alpha=0.35, marker='o', label='Sensors', zorder=2, edgecolors='#1e3a8a', linewidths=0.4)

    # UAV coverage circles (sampled at waypoints to reduce clutter)
    waypoint_samples = []
    seen = set()
    for _, row in path_events.iterrows():
        key = (round(row['X'], 2), round(row['Y'], 2))
        if key in seen:
            continue
        seen.add(key)
        waypoint_samples.append((row['X'], row['Y']))
        if len(waypoint_samples) >= 8:
            break
    for x_c, y_c in waypoint_samples:
        circ = plt.Circle((x_c, y_c), uav_comm_radius, color='#1c7ed6', fill=False, linestyle=':', linewidth=1.2, alpha=0.45, zorder=2)
        ax.add_patch(circ)

    # UAV random waypoint path (smooth trajectory following waypoints, with BS start/end)
    if len(path_events) > 1:
        ax.plot(path_events['X'], path_events['Y'], color='#1c7ed6', linewidth=2.2, alpha=0.9, label='Random Waypoint Path', zorder=4)

    # Add directional arrows every 200m along the path
    cumulative_dist = 0.0
    arrow_interval = 200.0
    arrow_points = []
    for i in range(len(path_events) - 1):
        x1, y1 = path_events.iloc[i][['X', 'Y']]
        x2, y2 = path_events.iloc[i+1][['X', 'Y']]
        segment_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        cumulative_dist += segment_length
        if cumulative_dist >= arrow_interval:
            arrow_points.append((x2, y2, x2 - x1, y2 - y1))
            cumulative_dist -= arrow_interval
    
    for x, y, dx, dy in arrow_points:
        ax.arrow(x, y, dx*0.01, dy*0.01, head_width=8, head_length=6, fc='#2f9e44', ec='#1b4620', alpha=0.7, zorder=5)

    # Add sampled contact points (CH encounters, downsampled to every 5s)
    if len(contact_points) > 0:
        contact_arr = np.array(contact_points)
        ax.scatter(contact_arr[:, 0], contact_arr[:, 1], s=40, c='#2f9e44', alpha=0.85, marker='o', edgecolors='#1b4620', linewidths=1.2, zorder=5, label='CH Contact (sampled)')

    # Start/end markers
    ax.scatter(path_events.iloc[0]['X'], path_events.iloc[0]['Y'], s=130, c='#2f9e44', marker='^', edgecolors='#14532d', linewidths=1.4, zorder=5, label='Round start')
    ax.scatter(path_events.iloc[-1]['X'], path_events.iloc[-1]['Y'], s=130, c='#ffd43b', marker='^', edgecolors='#b57600', linewidths=1.4, zorder=5, label='Round end')

    # Cluster heads overlay
    if ch_positions is not None and len(ch_positions) > 0:
        ax.scatter(ch_positions['X'], ch_positions['Y'], s=200, c='#ff6b6b', marker='*', edgecolors='#c92a2a', linewidths=1.8, zorder=6, label='Round CHs')
        for _, row in ch_positions.iterrows():
            ax.add_patch(plt.Circle((row['X'], row['Y']), ch_comm_radius, color='#ff6b6b', fill=False, linestyle='--', linewidth=1.0, alpha=0.5, zorder=5))

    # Base station
    ax.scatter(bs_pos[0], bs_pos[1], s=320, c='#2b8a3e', marker='s', edgecolors='#1b4620', linewidths=2.0, zorder=7, label='Base Station')
    ax.text(bs_pos[0], bs_pos[1] - 30, f"BS\n({int(bs_pos[0])},{int(bs_pos[1])})", ha='center', fontsize=9, fontweight='bold', color='#2b8a3e', bbox=dict(boxstyle='round,pad=0.3', facecolor='#d4edda', alpha=0.95, edgecolor='#1b4620', linewidth=1.2))

    ax.set_xlabel('X Position (m)', fontsize=20, fontweight='bold')
    ax.set_ylabel('Y Position (m)', fontsize=20, fontweight='bold')
    ax.set_title(
        f'UAV Random Waypoint Trajectory - Round {round_num}\nTime window: {start_time:.2f}s to {end_time:.2f}s | Path length: {path_length:.1f} m',
        fontsize=22, fontweight='bold', pad=16)
    margin = 60
    ax.set_xlim(bs_pos[0] - margin, area_x + margin)
    ax.set_ylim(-margin, area_y + margin)
    ax.set_aspect('equal', adjustable='box')
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='upper left', fontsize=18, framealpha=0.95)
    ax.grid(True, alpha=0.35, linestyle=':')

    plt.tight_layout()
    out_path = f'plots/uav_trajectory_round{round_num}.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✓ Saved: {out_path}")

def create_output_dir():
    """Create plots directory if it doesn't exist"""
    os.makedirs('plots', exist_ok=True)
    print("📁 Output directory: plots/")

@contextmanager
def _savefig_to(out_dir: str):
    """Temporarily redirect plt.savefig() to a scenario-specific output folder."""
    orig_savefig = plt.savefig
    def _wrapped_savefig(fname, *a, **k):
        return orig_savefig(os.path.join(out_dir, os.path.basename(fname)), *a, **k)
    plt.savefig = _wrapped_savefig
    try:
        yield
    finally:
        plt.savefig = orig_savefig

def plot_network_lifetime(stability_df):
    """Plot network lifetime (Alive Nodes vs Rounds) extending to a reasonable max round"""
    print("📊 Generating Network Lifetime plot...")
    
    # Get last known values
    last_round = stability_df['Round'].max()
    last_alive = stability_df[stability_df['Round'] == last_round]['AliveNodes'].values[0]
    last_dead = stability_df[stability_df['Round'] == last_round]['DeadNodes'].values[0]

    plot_max_round = max(1500, int(last_round))
    
    # Extend data to plot_max_round using last known values
    if last_round < plot_max_round:
        extended_rounds = np.arange(last_round + 1, plot_max_round + 1)
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
    plt.savefig('plots/network_lifetime.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/network_lifetime.png")

def plot_energy_consumption(energy_df):
    """Plot energy consumption over rounds"""
    print("📊 Generating Energy Consumption plot...")
    
    # Filter to LND
    lnd_round = get_lnd_round()
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
    plt.savefig('plots/energy_consumption.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/energy_consumption.png")

def plot_pdr(pdr_df):
    """Plot Packet Delivery Ratio"""
    print("📊 Generating PDR plot...")
    
    # Filter to LND
    lnd_round = get_lnd_round()
    if lnd_round:
        pdr_df = pdr_df[pdr_df['Round'] <= lnd_round].copy()
    
    # Filter to meaningful data
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
    plt.savefig('plots/pdr.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/pdr.png")

def plot_throughput(throughput_df):
    """Plot network throughput with moving average"""
    print("📊 Generating Throughput plot...")
    
    # Filter to LND time
    lnd_round = get_lnd_round()
    if lnd_round:
        # Get actual LND time from stability data
        try:
            stability_df = pd.read_csv('results/stability.csv')
            lnd_row = stability_df[stability_df['AliveNodes'] == 0]
            if len(lnd_row) > 0:
                lnd_time = float(lnd_row['Time'].iloc[0])
                throughput_df = throughput_df[throughput_df['Time'] <= lnd_time].copy()
        except:
            # Fallback to approximation
            max_time = lnd_round * 774  # 774s per round
            throughput_df = throughput_df[throughput_df['Time'] <= max_time].copy()
    
    # Calculate 20-round moving average for smoothed trend
    window_size = 20
    throughput_df['MA_Throughput'] = throughput_df['Throughput_kbps'].rolling(window=window_size, center=True, min_periods=1).mean()
    
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
    
    # Use scientific notation for x-axis (powers of 10)
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    ax.xaxis.get_offset_text().set_fontsize(16)
    
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='upper right', fontsize=16)
    ax.grid(True, alpha=0.4, linewidth=0.8)
    plt.tight_layout()
    plt.savefig('plots/throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/throughput.png")

def _estimate_round_duration(network_df: pd.DataFrame | None) -> float:
    """Estimate round duration dynamically from network.csv (fallback to 150s)."""
    try:
        if network_df is not None and 'Time' in network_df.columns:
            times = network_df['Time'].astype(float).values
            if len(times) >= 2:
                diffs = np.diff(times)
                # Use median to be robust to occasional anomalies
                rd = float(np.median(diffs))
                if rd > 0:
                    return rd
    except Exception:
        pass
    return 150.0

def _assign_round(times: np.ndarray, network_df: pd.DataFrame | None, default_rd: float = 150.0) -> np.ndarray:
    """Map arbitrary times to round numbers using network.csv times for accuracy.
    Falls back to floor(t/round_duration). Rounds are 1-based.
    """
    try:
        if network_df is not None and {'Round', 'Time'}.issubset(network_df.columns):
            round_times = network_df[['Round', 'Time']].dropna().sort_values('Time')
            times_arr = round_times['Time'].astype(float).values
            rounds_arr = round_times['Round'].astype(int).values
            # searchsorted gives insertion index; subtract 1 to get containing round
            idx = np.searchsorted(times_arr, times, side='right') - 1
            idx = np.clip(idx, 0, len(rounds_arr) - 1)
            return rounds_arr[idx]
    except Exception:
        pass
    # Fallback to duration-based
    rd = default_rd
    return (times / rd).astype(int) + 1

def plot_delay_distribution(delay_df, network_df=None):
    """Plot end-to-end delay distribution"""
    print("📊 Generating Delay Distribution plot...")
    
    # Filter valid delays: all delivered packets (no window restriction)
    valid_delays = delay_df[delay_df['Delay_s'] > 0].copy()

    if valid_delays.empty:
        print("   ⚠️  Skipped: no delivered packets with positive delay")
        return
    
    # Calculate delay percentiles for annotations
    p25 = valid_delays['Delay_s'].quantile(0.25)
    p75 = valid_delays['Delay_s'].quantile(0.75)
    p95 = valid_delays['Delay_s'].quantile(0.95)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Use logarithmic bins for better visualization of wide delay range
    delays = valid_delays['Delay_s'].values
    bins = np.logspace(np.log10(delays.min()), np.log10(delays.max()), 80)
    
    ax.hist(delays, bins=bins, color='#7209B7', alpha=0.7, edgecolor='#3c0ca3', linewidth=0.5)
    ax.set_xlabel('End-to-End Delay (s)', fontweight='bold', fontsize=20)
    ax.set_ylabel('Frequency', fontweight='bold', fontsize=20)
    ax.set_title(f'End-to-End Delay Distribution ({len(valid_delays):,} delivered packets)', fontweight='bold', fontsize=22)
    ax.set_xscale('log')
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8, which='both')
    
    # Add statistical markers
    ax.axvline(x=valid_delays['Delay_s'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {valid_delays["Delay_s"].mean():.1f}s')
    ax.axvline(x=valid_delays['Delay_s'].median(), color='orange', linestyle='--', linewidth=2, label=f'Median: {valid_delays["Delay_s"].median():.1f}s')
    ax.axvline(x=p95, color='darkred', linestyle=':', linewidth=1.5, label=f'95th percentile: {p95:.1f}s')
    ax.legend(loc='upper right', fontsize=18)
    
    plt.tight_layout()
    plt.savefig('plots/delay_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: plots/delay_distribution.png ({len(valid_delays):,} packets delivered)")

def plot_average_delay_per_round(delay_df, network_df):
    """Plot average end-to-end delay vs round number"""
    print("📊 Generating Average Delay per Round plot...")
    
    # Filter valid delays
    valid_delays = delay_df[delay_df['Delay_s'] > 0].copy()
    round_duration = _estimate_round_duration(network_df)
    # FIXED: Use ReceptionTime instead of GenerationTime for accurate packet reception counting
    rec_times = valid_delays['ReceptionTime'].astype(float).values
    valid_delays['RecRound'] = _assign_round(rec_times, network_df, default_rd=round_duration)
    
    # Filter to LND
    lnd_round = get_lnd_round()
    if lnd_round:
        valid_delays = valid_delays[valid_delays['RecRound'] <= lnd_round].copy()
    
    # Group by reception round (when packets were actually delivered)
    delay_by_round = valid_delays.groupby('RecRound').agg({
        'Delay_s': ['mean', 'count']
    }).reset_index()
    delay_by_round.columns = ['Round', 'AvgDelay', 'PacketCount']
    
    # Filter to rounds with sufficient packets
    delay_by_round = delay_by_round[delay_by_round['PacketCount'] >= 5]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9))
    
    # Plot 1: Average delay
    ax1.plot(delay_by_round['Round'], delay_by_round['AvgDelay'],
             linewidth=2.5, color='#0B7285', marker='o', markersize=4, markevery=20)
    ax1.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax1.set_ylabel('Average E2E Delay (s)', fontweight='bold', fontsize=20)
    ax1.set_title('Average Network Delay vs Round', fontweight='bold', fontsize=22)
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
    plt.savefig('plots/average_delay_per_round.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/average_delay_per_round.png")

def plot_clustering_metrics(clustering_df):
    """Plot clustering metrics"""
    print("📊 Generating Clustering Metrics plot...")
    
    # Filter to LND
    lnd_round = get_lnd_round()
    if lnd_round:
        clustering_df = clustering_df[clustering_df['Round'] <= lnd_round].copy()
    
    # Aggregate by round to get unique values
    agg_fields = {
        'TotalClusters': 'first',
        'AvgMembersPerCluster': 'first',
        'UnclusteredNodes': 'first'
    }

    if 'AggregationCompletion' in clustering_df.columns:
        agg_fields['AggregationCompletion'] = 'mean'
    if 'ExpectedMembers' in clustering_df.columns:
        agg_fields['ExpectedMembers'] = 'sum'
    if 'ReceivedMembers' in clustering_df.columns:
        agg_fields['ReceivedMembers'] = 'sum'

    clustering_agg = clustering_df.groupby('Round').agg(agg_fields).reset_index()
    
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
    plt.savefig('plots/clustering_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/clustering_metrics.png")
    print("   ✓ Saved: plots/clustering_metrics.png")

def plot_overhead(overhead_df):
    """Plot control packet overhead"""
    print("📊 Generating Overhead plot...")
    
    # Filter to rounds with meaningful packet activity (at least 50 total packets)
    # to avoid high variance noise in late rounds with network degradation
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
    ax.legend(loc='best', fontsize=10)
    
    # Add annotation for network degradation period
    if len(valid_rounds) < len(overhead_df):
        last_valid_round = valid_rounds['Round'].max()
        ax.axvline(x=last_valid_round, color='red', linestyle='--', linewidth=1.5, alpha=0.6, label='Network Degradation Begins')
        ax.text(last_valid_round, 0.95, f'  Network\n  Degradation\n  ({int(last_valid_round)}+)', 
               fontsize=9, verticalalignment='top', color='red', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/control_overhead.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: plots/control_overhead.png ({len(valid_rounds)}/{len(overhead_df)} rounds with stable activity)")


def plot_packet_counts(overhead_df):
    """Plot control and data packets per round"""
    print("📊 Generating Control/Data packets plot...")
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(overhead_df['Round'], overhead_df['ControlPackets'], label='Control Packets', color='#d9480f', linewidth=1.8)
    ax.plot(overhead_df['Round'], overhead_df['DataPackets'], label='Data Packets', color='#1c7ed6', linewidth=1.8)
    ax.set_xlabel('Round', fontweight='bold', fontsize=20)
    ax.set_ylabel('Packets', fontweight='bold', fontsize=20)
    ax.set_title('Control vs Data Packets per Round', fontweight='bold', fontsize=22)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(fontsize=18)
    ax.grid(True, alpha=0.8, linewidth=1.0)
    plt.tight_layout()
    plt.savefig('plots/packet_counts.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/packet_counts.png")

def plot_packet_generation_aggregation(pdr_df, clustering_df):
    """Plot packets generated vs packets aggregated per round"""
    print("📊 Generating Packet Generation vs Aggregation plot...")
    
    # Calculate aggregated packets per round
    agg_by_round = clustering_df.groupby('Round').agg({
        'ReceivedMembers': 'sum',  # Total member packets received by CHs
        'TotalClusters': 'first'   # Number of CHs per round
    }).reset_index()
    
    # Aggregated packets = ReceivedMembers + TotalClusters (each CH contributes its own packet)
    agg_by_round['AggregatedPackets'] = agg_by_round['ReceivedMembers'] + agg_by_round['TotalClusters']
    
    # Merge with PDR data
    merged_df = pd.merge(pdr_df, agg_by_round, on='Round', how='left')
    
    # Filter to LND
    lnd_round = get_lnd_round()
    if lnd_round:
        merged_df = merged_df[merged_df['Round'] <= lnd_round].copy()
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    # Plot packets
    ax.plot(merged_df['Round'], merged_df['PacketsGenerated'], 
             linewidth=2.5, color='#2E86AB', label='Packets Generated', marker='o', markersize=4, markevery=30)
    ax.plot(merged_df['Round'], merged_df['AggregatedPackets'], 
             linewidth=2.5, color='#ff6b6b', label='Packets Aggregated', marker='s', markersize=4, markevery=30)
    ax.plot(merged_df['Round'], merged_df['PacketsReceived'], 
             linewidth=2.5, color='#2f9e44', label='Packets Received by UAV', marker='^', markersize=4, markevery=30)
    
    ax.set_xlabel('Round Number', fontweight='bold', fontsize=20)
    ax.set_ylabel('Number of Packets', fontweight='bold', fontsize=20)
    ax.set_title('Packet Generation vs Aggregation vs Reception', fontweight='bold', fontsize=22)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.legend(loc='best', fontsize=18)
    ax.grid(True, alpha=0.4, linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig('plots/packet_generation_aggregation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/packet_generation_aggregation.png")

def plot_contact_success(contact_df):
    """Plot UAV contact success rate"""
    print("📊 Generating UAV Contact Success plot...")
    if len(contact_df) == 0:
        print("   ⚠️  No contact events to plot.")
        return
    
    # Calculate success rate over time (rolling window)
    contact_df['SuccessNum'] = contact_df['Successful'].apply(lambda x: 1 if x == 'Yes' else 0)
    contact_df['CumulativeSuccess'] = contact_df['SuccessNum'].cumsum()
    contact_df['CumulativeTotal'] = range(1, len(contact_df) + 1)
    contact_df['SuccessRate'] = contact_df['CumulativeSuccess'] / contact_df['CumulativeTotal']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    ax1.plot(contact_df['Instance'], contact_df['SuccessRate'], 
           linewidth=2, color='#2A9D8F')
    ax1.set_xlabel('Contact Instance', fontweight='bold', fontsize=20)
    ax1.set_ylabel('Cumulative Success Rate', fontweight='bold', fontsize=20)
    ax1.set_title('UAV-CH Contact Success Rate', fontweight='bold', fontsize=22)
    ax1.set_ylim([0, 1.05])
    ax1.tick_params(axis='both', which='major', labelsize=18)
    ax1.grid(True, alpha=0.6, linewidth=0.9)

    if 'Duration_s' in contact_df.columns:
        ax2.plot(contact_df['Instance'], contact_df['Duration_s'], color='#264653', linewidth=1.5, label='Contact Duration (s)')
        # Highlight failures to see if short contacts correlate
        failed = contact_df[contact_df['Successful'] != 'Yes']
        if not failed.empty:
            ax2.scatter(failed['Instance'], failed['Duration_s'], color='#e63946', label='Failed Contacts', zorder=3)
        ax2.set_ylabel('Contact Duration (s)', fontweight='bold', fontsize=20)
        ax2.set_xlabel('Contact Instance', fontweight='bold', fontsize=20)
        ax2.tick_params(axis='both', which='major', labelsize=18)
        ax2.set_title('Per-Contact Duration (hover-enforced)', fontweight='bold', fontsize=22)
        ax2.grid(True, alpha=0.6, linewidth=0.9)
        ax2.legend(fontsize=18)
    else:
        ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig('plots/uav_contact_success.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: plots/uav_contact_success.png")

def generate_summary_statistics():
    """Generate summary statistics from all CSV files"""
    print("\n📊 Generating Summary Statistics...")
    
    stats = {}
    
    try:
        # Network lifetime
        stability_df = pd.read_csv('results/stability.csv')
        fnd_round = stability_df[stability_df['DeadNodes'] > 0]['Round'].iloc[0] if len(stability_df[stability_df['DeadNodes'] > 0]) > 0 else None
        hna_round = stability_df[stability_df['AliveNodes'] <= 200]['Round'].iloc[0] if len(stability_df[stability_df['AliveNodes'] <= 200]) > 0 else None
        lnd_round = stability_df[stability_df['AliveNodes'] == 0]['Round'].iloc[0] if len(stability_df[stability_df['AliveNodes'] == 0]) > 0 else None
        
        stats['FND (First Node Death)'] = f"Round {int(fnd_round)}" if fnd_round else "N/A"
        stats['HNA (Half Nodes Alive)'] = f"Round {int(hna_round)}" if hna_round else "N/A"
        stats['LND (Last Node Death)'] = f"Round {int(lnd_round)}" if lnd_round else "N/A"
        
        # PDR
        pdr_df = pd.read_csv('results/pdr.csv')
        stats['Mean PDR'] = f"{pdr_df['PDR'].mean():.4f}"
        stats['Final PDR'] = f"{pdr_df['PDR'].iloc[-1]:.4f}"
        
        # Energy
        energy_df = pd.read_csv('results/energy.csv')
        stats['Total Energy Consumed'] = f"{energy_df['EnergyConsumed'].sum():.2f} J"
        stats['Avg Energy per Round'] = f"{energy_df['EnergyConsumed'].mean():.4f} J"
        
        # Delay
        delay_df = pd.read_csv('results/delay.csv')
        stats['Mean Delay'] = f"{delay_df['Delay_s'].mean():.2f} s"
        stats['Median Delay'] = f"{delay_df['Delay_s'].median():.2f} s"
        stats['Max Delay'] = f"{delay_df['Delay_s'].max():.2f} s"
        
        # Clustering
        clustering_df = pd.read_csv('results/clustering.csv')
        clustering_agg = clustering_df.groupby('Round')['TotalClusters'].first()
        stats['Mean CHs per Round'] = f"{clustering_agg.mean():.1f}"
        stats['Mean Unclustered Nodes'] = f"{clustering_df.groupby('Round')['UnclusteredNodes'].first().mean():.2f}"
        if 'AggregationCompletion' in clustering_df.columns:
            stats['Avg Aggregation Completion'] = f"{clustering_df['AggregationCompletion'].mean():.3f}"
        if 'ExpectedMembers' in clustering_df.columns and 'ReceivedMembers' in clustering_df.columns:
            total_expected = clustering_df['ExpectedMembers'].sum()
            total_received = clustering_df['ReceivedMembers'].sum()
            delivery_rate = (total_received / total_expected) if total_expected > 0 else 1.0
            stats['Member Delivery Rate'] = f"{delivery_rate:.3f}"
        if 'DeadlineHit' in clustering_df.columns:
            stats['Aggregation Deadlines Hit'] = f"{int(clustering_df['DeadlineHit'].sum())}"
        
        # Contact success
        contact_df = pd.read_csv('results/contact.csv')
        if len(contact_df) > 0:
            success_rate = (contact_df['Successful'] == 'Yes').sum() / len(contact_df)
            stats['UAV Contact Success Rate'] = f"{success_rate:.4f}"
            if 'Duration_s' in contact_df.columns:
                stats['Avg Contact Duration'] = f"{contact_df['Duration_s'].mean():.2f} s"
        else:
            stats['UAV Contact Success Rate'] = "N/A"
        
        # Write summary
        with open('plots/summary_statistics.txt', 'w') as f:
            f.write("="*60 + "\n")
            f.write("UAV-WSN-BM Simulation Results Summary (S_Ideal Scenario)\n")
            f.write("="*60 + "\n\n")
            f.write("Network Configuration:\n")
            f.write("  - 100 sensor nodes\n")
            f.write("  - 500m × 500m area\n")
            f.write("  - Initial energy: 0.5 J per node\n")
            f.write("  - CH probability: 0.1\n\n")
            f.write("Simulation Results:\n")
            f.write("-" * 60 + "\n")
            for key, value in stats.items():
                f.write(f"{key:.<40} {value}\n")
            f.write("="*60 + "\n")
        
        print("\n" + "="*60)
        print("SIMULATION SUMMARY STATISTICS")
        print("="*60)
        for key, value in stats.items():
            print(f"{key:.<40} {value}")
        print("="*60)
        print("\n✓ Summary saved to: plots/summary_statistics.txt")
        
    except Exception as e:
        print(f"⚠️  Error generating summary statistics: {e}")

def main():
    """Main plotting function"""
    print("\n" + "="*60)
    print("UAV-WSN-BM RESULTS PLOTTER")
    print("="*60 + "\n")
    
    # Check if results directory exists
    if not os.path.exists('results'):
        print("❌ Error: 'results' directory not found!")
        print("   Please run the simulation first.")
        sys.exit(1)
    
    # Create output directory
    create_output_dir()
    

    # --- Main (default) results ---
    try:
        network_df = None
        if os.path.exists('results/network.csv'):
            network_df = pd.read_csv('results/network.csv')

        # (existing code for main results, unchanged)
        # ...

        # --- Scenario-specific plots ---
        scenarios_dir = 'results/scenarios/'
        plots_scenarios_dir = 'plots/scenarios/'
        os.makedirs(plots_scenarios_dir, exist_ok=True)
        scenario_names = [d for d in os.listdir(scenarios_dir) if os.path.isdir(os.path.join(scenarios_dir, d))]
        for scenario in scenario_names:
            scenario_path = os.path.join(scenarios_dir, scenario)
            out_dir = os.path.join(plots_scenarios_dir, scenario)
            os.makedirs(out_dir, exist_ok=True)
            # For each metric, if the CSV exists, generate the plot in the scenario's plot folder
            try:
                # Lifetime
                stab_path = os.path.join(scenario_path, 'stability.csv')
                if os.path.exists(stab_path):
                    stability_df = pd.read_csv(stab_path)
                    plt.switch_backend('Agg')
                    with _savefig_to(out_dir):
                        plot_network_lifetime(stability_df)
                # Energy
                energy_path = os.path.join(scenario_path, 'energy.csv')
                if os.path.exists(energy_path):
                    energy_df = pd.read_csv(energy_path)
                    plt.switch_backend('Agg')
                    with _savefig_to(out_dir):
                        plot_energy_consumption(energy_df)
                # PDR
                pdr_path = os.path.join(scenario_path, 'pdr.csv')
                if os.path.exists(pdr_path):
                    pdr_df = pd.read_csv(pdr_path)
                    plt.switch_backend('Agg')
                    with _savefig_to(out_dir):
                        plot_pdr(pdr_df)
                # Throughput
                thr_path = os.path.join(scenario_path, 'throughput.csv')
                if os.path.exists(thr_path):
                    throughput_df = pd.read_csv(thr_path)
                    plt.switch_backend('Agg')
                    with _savefig_to(out_dir):
                        plot_throughput(throughput_df)
                # Delay
                delay_path = os.path.join(scenario_path, 'delay.csv')
                if os.path.exists(delay_path):
                    delay_df = pd.read_csv(delay_path)
                    plt.switch_backend('Agg')
                    with _savefig_to(out_dir):
                        plot_delay_distribution(delay_df)
            except Exception as se:
                print(f"[Scenario {scenario}] Error generating scenario plots: {se}")

        # --- Parameter sensitivity plot for S5 (packet size) ---
        # Collect S5-A and S5-B results
        s5a_dir = os.path.join(scenarios_dir, 'S5-A')
        s5b_dir = os.path.join(scenarios_dir, 'S5-B')
        s5a_pdr = os.path.join(s5a_dir, 'pdr.csv')
        s5b_pdr = os.path.join(s5b_dir, 'pdr.csv')
        if os.path.exists(s5a_pdr) and os.path.exists(s5b_pdr):
            df_a = pd.read_csv(s5a_pdr)
            df_b = pd.read_csv(s5b_pdr)
            # Assume both have 'Round' and 'PDR' columns
            mean_pdr_a = df_a['PDR'].mean()
            mean_pdr_b = df_b['PDR'].mean()
            plt.switch_backend('Agg')
            fig, ax = plt.subplots(figsize=(8,6))
            ax.bar(['500 bits', '4000 bits'], [mean_pdr_a, mean_pdr_b], color=['#4c6ef5', '#ff6b6b'])
            ax.set_ylabel('Mean PDR')
            ax.set_title('Parameter Sensitivity: Packet Size (S5)')
            ax.set_ylim(0, 1.05)
            for i, v in enumerate([mean_pdr_a, mean_pdr_b]):
                ax.text(i, v+0.02, f"{v:.3f}", ha='center', fontsize=14, fontweight='bold')
            os.makedirs('plots/parameter_sensitivity', exist_ok=True)
            plt.tight_layout()
            plt.savefig('plots/parameter_sensitivity/S5_packet_size.png', dpi=300)
            plt.close()
            print('   ✓ Saved: plots/parameter_sensitivity/S5_packet_size.png')

    except Exception as e:
        print(f"\n❌ Error generating plots: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
