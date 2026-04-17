Network Topology Visualization - Realistic Scenario
Generates a map showing the distribution of nodes in the UAV-WSN network
with IEEE 802.15.4 sensor nodes and IEEE 802.11 UAV
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def visualize_network_topology():
    """Create a comprehensive visualization of the network topology"""
    
    # Network parameters - S0 BASELINE SCENARIO (Realistic)
    num_nodes = 100
    area_x = 500  # meters (realistic for discovery algorithms)
    area_y = 500  # meters
    sensor_comm_radius = 100  # meters (Extended range)
    uav_comm_radius = 150  # meters (Extended WiFi range)
    uav_altitude = 30  # meters
    
    # Base station position (outside the sensor field)
    bs_x = -100  # meters
    bs_y = -100  # meters
    
    # Calculate distance from network center to base station
    center_x, center_y = area_x/2, area_y/2
    distance_to_bs = np.sqrt((bs_x - center_x)**2 + (bs_y - center_y)**2)
    
    # UAV initial position (starts near BS, entering the field)
    uav_x = 0  # meters
    uav_y = 0  # meters
    
    # Generate sensor node positions - random uniform distribution
    np.random.seed(42)  # For reproducibility
    node_x = np.random.uniform(0, area_x, num_nodes)
    node_y = np.random.uniform(0, area_y, num_nodes)
    
    # Create comprehensive single plot
    fig, ax = plt.subplots(figsize=(16, 14))
    
    ax.set_title('UAV-WSN Network Topology: S0 Baseline Scenario\n' + 
                 'Sensor Nodes: Extended Range (100m) | UAV: Extended WiFi (150m)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # === Plot sensor field boundary ===
    field_rect = patches.Rectangle((0, 0), area_x, area_y, 
                                   linewidth=3, edgecolor='darkgreen', 
                                   facecolor='lightgreen', alpha=0.15, 
                                   label=f'WSN Field ({area_x}m × {area_y}m)', 
                                   zorder=1)
    ax.add_patch(field_rect)
    
    # Add field annotations
    ax.text(area_x/2, -30, f'{area_x}m', ha='center', va='top', 
            fontsize=12, fontweight='bold', color='darkgreen')
    ax.text(-30, area_y/2, f'{area_y}m', ha='right', va='center', 
            fontsize=12, fontweight='bold', color='darkgreen', rotation=90)
    
    # === Plot sensor nodes ===
    ax.scatter(node_x, node_y, c='blue', s=80, alpha=0.7, 
               marker='o', label=f'Sensor Nodes (n={num_nodes}, IEEE 802.15.4)', 
               zorder=3, edgecolors='darkblue', linewidths=1)
    
    # Show sensor communication links (for a few sample nodes)
    sample_nodes = [10, 30, 60, 80]
    for sample_idx in sample_nodes:
        if sample_idx < len(node_x):
            sample_x, sample_y = node_x[sample_idx], node_y[sample_idx]
            # Draw communication radius
            circle = patches.Circle((sample_x, sample_y), sensor_comm_radius, 
                                    color='blue', fill=False, 
                                    linestyle='--', alpha=0.25, linewidth=1.5, 
                                    zorder=2)
            ax.add_patch(circle)
            
            # Draw links to neighbors within range
            for i in range(num_nodes):
                if i != sample_idx:
                    dist = np.sqrt((node_x[i] - sample_x)**2 + 
                                  (node_y[i] - sample_y)**2)
                    if dist <= sensor_comm_radius:
                        ax.plot([sample_x, node_x[i]], [sample_y, node_y[i]], 
                               'b-', alpha=0.15, linewidth=0.8, zorder=2)
    
    # Highlight one sample node
    sample_idx = 30
    ax.scatter(node_x[sample_idx], node_y[sample_idx], c='cyan', s=200, 
               marker='o', edgecolors='blue', linewidths=3, zorder=4, 
               label=f'Sample Node (50m comm range)')
    
    # === Plot UAV initial position ===
    ax.scatter(uav_x, uav_y, c='red', s=400, marker='^', 
               label=f'UAV Initial Position (IEEE 802.11, h={uav_altitude}m)', 
               zorder=6, edgecolors='darkred', linewidths=3)
    
    # UAV communication radius (footprint on ground)
    uav_circle = patches.Circle((uav_x, uav_y), uav_comm_radius, 
                                color='red', fill=False, 
                                linestyle='-.', alpha=0.4, linewidth=3,
                                label=f'UAV Coverage (100m radius)', 
                                zorder=5)
    ax.add_patch(uav_circle)
    
    # === Plot UAV raster scan path ===
    raster_width = 100  # meters (~2/3 of UAV commRadius)
    num_passes = int(area_x / raster_width) + 1
    
    for i in range(num_passes):
        x_pos = i * raster_width
        if x_pos <= area_x:
            if i % 2 == 0:  # Even pass: bottom to top
                ax.arrow(x_pos, 0, 0, area_y-20, head_width=8, head_length=15, 
                        fc='orange', ec='darkorange', alpha=0.5, linewidth=2, 
                        zorder=2)
            else:  # Odd pass: top to bottom
                ax.arrow(x_pos, area_y, 0, -(area_y-20), head_width=8, head_length=15, 
                        fc='orange', ec='darkorange', alpha=0.5, linewidth=2, 
                        zorder=2)
    
    # Add raster path label
    ax.plot([], [], color='orange', linewidth=2, label='UAV Raster Scan Path (40m spacing)')
    
    # === Plot base station ===
    ax.scatter(bs_x, bs_y, c='purple', s=500, marker='s', 
               label='Base Station (Remote)', 
               zorder=7, edgecolors='darkviolet', linewidths=3)
    
    # === Add distance annotations ===
    # Line from field center to BS
    ax.plot([center_x, bs_x], [center_y, bs_y], 'k--', alpha=0.5, linewidth=2, 
            zorder=2)
    
    # Distance label with arrow
    mid_x, mid_y = (center_x + bs_x)/2, (center_y + bs_y)/2
    ax.annotate(f'Distance: {distance_to_bs:.1f}m', 
                xy=(center_x, center_y), xytext=(mid_x - 50, mid_y - 30),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Mark field center
    ax.scatter(center_x, center_y, c='green', s=150, marker='x', 
               linewidths=3, zorder=4, label='Field Center')
    
    # === Styling ===
    ax.set_xlabel('X Position (meters)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Y Position (meters)', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.95, 
             edgecolor='black', fancybox=True)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=1)
    ax.set_aspect('equal')
    
    # Set axis limits to show full network area and base station
    margin = 50
    ax.set_xlim(bs_x - margin, area_x + margin)
    ax.set_ylim(bs_y - margin, area_y + margin)
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'network_topology_map.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Network topology map saved to: {output_file}")
    
    return output_file

if __name__ == '__main__':
    print("="*70)
    print("Generating UAV-WSN Network Topology Visualization")
    print("Scenario: S0 Baseline (Realistic)")
    print("="*70)
    output_file = visualize_network_topology()
    print(f"\n✓ Visualization complete!")
    print(f"✓ Image file: {output_file}")
    print(f"\nKey Features:")
    print(f"  • 500m × 500m sensor field with 100 randomly distributed nodes")
    print(f"  • IEEE 802.15.4 sensor nodes (50m range, 250 kbps)")
    print(f"  • IEEE 802.11 UAV (100m range, 2+ Mbps)")
    print(f"  • Base station at (-100, -100), ~707m from field center")
    print(f"  • Demonstrates need for UAV as data mule")
    print("="*70)