import os
import pandas as pd
import matplotlib.pyplot as plt

# Imperial College London Official Palette
ICL_NAVY = '#003E74'
ICL_RED = '#D50032'
ICL_GREEN = '#00853F'
ICL_ORANGE = '#E87722'
ICL_LIGHT_BLUE = '#00AEEF'

def generate_spacetime_plots():
    """
    generates two-panel memory complexity diagrams
    static footprint vs batch scaling
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scaling_data = os.path.join(current_dir, "output/spacetime_results.csv")
    static_data = os.path.join(current_dir, "output/engine_load_costs.csv")
    
    if not os.path.exists(scaling_data) or not os.path.exists(static_data):
        print("Error: Spacetime data not found. Run the study first.")
        return

    df_scaling = pd.read_csv(scaling_data)
    df_static = pd.read_csv(static_data)

    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)

    # --- Panel 1: Static Footprint (Bar Chart) ---
    engines = df_static['Engine']
    loads = df_static['Static Load (MB)']
    colors = [ICL_NAVY if 'MERIT' in e else ICL_ORANGE if 'AI' in e else '#888888' for e in engines]
    
    bars = ax1.bar(engines, loads, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax1.set_title('Static Footprint: Initialisation Cost', fontsize=11, fontweight='bold', pad=15)
    ax1.set_ylabel('Memory (MB)', fontsize=10)
    ax1.tick_params(axis='x', rotation=30, labelsize=9) # Reduced rotation for better fit
    ax1.grid(axis='y', linestyle=':', alpha=0.5)
    
    # Add labels on top of bars with a small relative offset
    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, yval + (max(loads) * 0.02), f'{yval}MB', 
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Add some headroom for labels
    ax1.set_ylim(0, max(loads) * 1.2)

    # --- Panel 2: Batch Scaling (Line Chart) ---
    x = df_scaling['Candidates']
    
    ax2.plot(x, df_scaling['Traditional ATS (MB)'], marker='o', markersize=4, label='Traditional ATS', color='#888888', linestyle='--')
    ax2.plot(x, df_scaling['Modern AI ATS (MB)'], marker='s', markersize=4, label='Modern AI ATS', color=ICL_ORANGE)
    ax2.plot(x, df_scaling['MERIT CV-Only (MB)'], marker='^', markersize=4, label='MERIT (CV-Only)', color=ICL_GREEN)
    ax2.plot(x, df_scaling['MERIT Full (MB)'], marker='D', markersize=4, label='MERIT (Full)', color=ICL_NAVY)
    ax2.plot(x, df_scaling['MERIT Explainable (MB)'], marker='*', markersize=6, label='MERIT (Explainable)', color=ICL_RED)

    ax2.set_title('Operational Scaling: Memory Overhead', fontsize=11, fontweight='bold', pad=15)
    ax2.set_xlabel('Number of Candidates ($N$)', fontsize=10)
    ax2.set_ylabel('Incremental Memory (MB)', fontsize=10)
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(fontsize=8, loc='upper left', frameon=True)

    # master title with refined spacing
    plt.suptitle('Spacetime Complexity: Resource Allocation Profile', fontsize=14, fontweight='bold', y=0.98)
    
    # rect=[left, bottom, right, top] - balanced for suptitle and rotated x-labels
    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    
    output_path = os.path.join(current_dir, "output/spacetime_complexity_composite.png")
    # Using a higher DPI for the final save, but controlled width in the notebook
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close(fig) # Prevent duplicate display in notebooks
    print(f"[SUCCESS] Spacetime composite plot saved to {output_path}")

if __name__ == "__main__":
    # Ensure we use a non-interactive backend to avoid notebook/GUI issues
    import matplotlib
    matplotlib.use('Agg')
    generate_spacetime_plots()
