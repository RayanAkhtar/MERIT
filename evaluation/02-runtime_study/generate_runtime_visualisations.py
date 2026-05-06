import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Imperial College London Official Palette
ICL_NAVY = '#003E74'
ICL_RED = '#D50032'
ICL_GREEN = '#00853F'
ICL_ORANGE = '#E87722'
ICL_PURPLE = '#5D295F'

def generate_runtime_plots():
    """
    generates publication-quality runtime performance diagrams
    for the merit dissertation
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "output/runtime_results.csv")
    
    if not os.path.exists(data_path):
        print(f"Error: Data not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    
    # --- Plot 1: Overall Latency Scaling ---
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    x = df['Candidates']
    
    ax.plot(x, df['Traditional ATS (s)'], marker='o', label='Traditional ATS', color='#888888', linestyle='--', linewidth=2)
    ax.plot(x, df['Modern AI ATS (s)'], marker='s', label='Modern AI ATS (Semantic)', color=ICL_ORANGE, linewidth=2.5)
    ax.plot(x, df['MERIT CV-Only (s)'], marker='^', label='MERIT (CV-Only Ablation)', color=ICL_GREEN, linewidth=2.5)
    ax.plot(x, df['MERIT Full (s)'], marker='D', label='MERIT (Full Multi-Source)', color=ICL_NAVY, linewidth=3)
    ax.plot(x, df['MERIT Explainable (s)'], marker='*', label='MERIT (Full + Shapley XAI)', color=ICL_RED, linewidth=3)

    ax.set_title('Runtime Complexity: Ranking Latency vs Candidate Volume', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Number of Candidates ($N$)', fontsize=12)
    ax.set_ylabel('Execution Time (seconds)', fontsize=12)
    
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(frameon=True, loc='upper left', fontsize=10)
    
    # Adding a zoom-in callout for the lower N values if necessary
    # (Leaving it standard for now to show the full trend)
    
    plt.tight_layout()
    output_plot = os.path.join(current_dir, "output/runtime_complexity_plot.png")
    plt.savefig(output_plot)
    plt.close(fig) # Prevent duplicate display in notebooks
    print(f"[SUCCESS] Runtime plot saved to {output_plot}")

    # --- Plot 2: Per-Candidate Efficiency (Normalised) ---
    fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Latency per candidate
    for col in df.columns[1:]:
        ax2.plot(x, df[col] / x * 1000, marker='o', label=col.replace(' (s)', ''), linewidth=2)

    ax2.set_title('Algorithmic Efficiency: Latency per 1000 Candidates', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('Batch Size ($N$)', fontsize=12)
    ax2.set_ylabel('Time per 1000 items (ms)', fontsize=12)
    ax2.set_yscale('log') # Use log scale for efficiency comparison
    
    ax2.grid(True, which="both", ls="-", alpha=0.2)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    output_eff = os.path.join(current_dir, "output/runtime_efficiency_log.png")
    plt.savefig(output_eff)
    plt.close(fig2) # Prevent duplicate display in notebooks
    print(f"[SUCCESS] Efficiency plot saved to {output_eff}")

if __name__ == "__main__":
    # Ensure non-interactive backend to avoid notebook auto-display
    import matplotlib
    matplotlib.use('Agg')
    generate_runtime_plots()
