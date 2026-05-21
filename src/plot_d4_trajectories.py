import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def main():
    # 1. Load the simulation data from archive/iter_226/results/d4_spacetime_report.json
    json_path = "archive/iter_226/results/d4_spacetime_report.json"
    print(f"Loading data from {json_path}...")
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # 2. Extract the 3D spatial coordinates (X, Y, Z) for the first 50 steps of the three worldlines
    # Stationary, Moving Massive, and Massless
    trajectories = {}
    key_mapping = {
        'stationary': 'Stationary Worldline (v=0)',
        'moving_massive': 'Moving Massive Worldline (v=0.5c)',
        'massless': 'Massless Worldline (v=c)'
    }
    
    for key in ['stationary', 'moving_massive', 'massless']:
        if key not in data['simulations']:
            raise KeyError(f"Key '{key}' not found in simulations data.")
            
        sim = data['simulations'][key]
        steps = sim['steps'][:50]
        
        X = [step['X'] for step in steps]
        Y = [step['Y'] for step in steps]
        Z = [step['Z'] for step in steps]
        
        trajectories[key] = {
            'X': X,
            'Y': Y,
            'Z': Z,
            'label': key_mapping[key],
            'raw_name': sim.get('name', key)
        }
        print(f"Extracted {len(steps)} steps for {key_mapping[key]}:")
        print(f"  X-range: [{min(X):.2f}, {max(X):.2f}]")
        print(f"  Y-range: [{min(Y):.2f}, {max(Y):.2f}]")
        print(f"  Z-range: [{min(Z):.2f}, {max(Z):.2f}]")

    # 3. Generate a 3D line plot using matplotlib (3D projection) showing the three trajectories.
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Styles for each trajectory to highlight their characteristics and the discrete lattice steps
    styles = {
        'stationary': {
            'color': '#1f77b4',  # Steel blue
            'marker': 'o',       # Circle
            'markersize': 5,
            'linewidth': 2.0,
            'linestyle': '-'
        },
        'moving_massive': {
            'color': '#2ca02c',  # Forest green
            'marker': 's',       # Square
            'markersize': 4,
            'linewidth': 2.0,
            'linestyle': '-'
        },
        'massless': {
            'color': '#d62728',  # Crimson red
            'marker': '^',       # Triangle up
            'markersize': 5,
            'linewidth': 1.5,
            'linestyle': '--'
        }
    }
    
    for key, traj in trajectories.items():
        style = styles[key]
        ax.plot(
            traj['X'], traj['Y'], traj['Z'],
            label=traj['label'],
            color=style['color'],
            marker=style['marker'],
            markersize=style['markersize'],
            linewidth=style['linewidth'],
            linestyle=style['linestyle'],
            alpha=0.85
        )
        
        # Highlight start and end of each trajectory
        ax.scatter(traj['X'][0], traj['Y'][0], traj['Z'][0], color='black', s=40, zorder=5)
        ax.text(traj['X'][0], traj['Y'][0], traj['Z'][0], ' Start', color='black', fontsize=9)
        
        ax.scatter(traj['X'][-1], traj['Y'][-1], traj['Z'][-1], color='black', s=40, zorder=5)
        ax.text(traj['X'][-1], traj['Y'][-1], traj['Z'][-1], ' End', color='black', fontsize=9)

    # 4. Configure clean axis labels, titles, and a legend.
    ax.set_xlabel('Spatial X', fontsize=11, labelpad=10)
    ax.set_ylabel('Spatial Y', fontsize=11, labelpad=10)
    ax.set_zlabel('Spatial Z', fontsize=11, labelpad=10)
    
    ax.set_title('D4 Lattice Spacetime Trajectories (First 50 Steps)\n'
                 'Visualizing Zitterbewegung (Zig-Zag Paths) for Stationary and Moving Massive Particles', 
                 fontsize=14, pad=20, weight='bold')
    
    # Place a nice legend
    ax.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)
    
    # Customize grid and view angle to clearly display the 3D paths
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.view_init(elev=25, azim=30)
    
    # 5. Save the generated figure as archive/iter_226/results/d4_trajectories.png
    output_dir = "archive/iter_226/results"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "d4_trajectories.png")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Successfully generated and saved 3D plot to: {output_path}")

if __name__ == "__main__":
    main()
