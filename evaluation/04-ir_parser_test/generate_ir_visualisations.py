import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ICL_NAVY = '#003E74'
ICL_LIGHT_BLUE = '#00AEEF'

def generate_accuracy_plots():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(current_dir, "output/accuracy_summary.csv")
    
    if not os.path.exists(summary_path):
        print("Error: Accuracy summary not found. Run the test first.")
        return

    df = pd.read_csv(summary_path)
    
    # Classify files based on explicit manifest (keeps repo structure as source-of-truth)
    manifest_path = os.path.join(current_dir, "test_data", "layout_manifest.csv")
    if os.path.exists(manifest_path):
        manifest = pd.read_csv(manifest_path)
        layout_map = dict(zip(manifest["File"], manifest["Layout"]))
        df["Layout"] = df["File"].map(layout_map).fillna("Unknown")
    else:
        df["Layout"] = "Unknown"
    
    # Compute averages grouped by Layout
    metrics = ["Skill Precision", "Skill Recall", "Skill F1", "Experience Recall", "Name Match", "Email Match"]
    grouped = df.groupby('Layout')[metrics].mean() * 100
    
    # Reindex to ensure order if both are present
    preferred = ['Single-Column (Linear)', 'Multi-Column (Asymmetrical)', 'Unknown']
    grouped = grouped.reindex([x for x in preferred if x in grouped.index])
    
    x = np.arange(len(metrics))
    width = 0.35  # width of the bars
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    
    single_vals = grouped.loc['Single-Column (Linear)'].values
    multi_vals = grouped.loc['Multi-Column (Asymmetrical)'].values
    
    n_single = int((df["Layout"] == "Single-Column (Linear)").sum())
    n_multi = int((df["Layout"] == "Multi-Column (Asymmetrical)").sum())
    rects1 = ax.bar(x - width/2, single_vals, width, label=f'Single-Column (Linear) [N={n_single}]', color=ICL_NAVY, alpha=0.9, edgecolor='black', linewidth=0.8)
    rects2 = ax.bar(x + width/2, multi_vals, width, label=f'Multi-Column (Asymmetrical) [N={n_multi}]', color=ICL_LIGHT_BLUE, alpha=0.9, edgecolor='black', linewidth=0.8)
    
    ax.set_title('CV Ingestion Performance: Single-Column vs. Multi-Column Layouts (Study 04)', fontsize=14, fontweight='bold', pad=25)
    ax.set_ylabel('Accuracy Score (%)', fontsize=12, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11, fontweight='semibold')
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    
    # Labels on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height + 2,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
            
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    output_path = os.path.join(current_dir, "output/ir_parser_accuracy.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    print(f"[SUCCESS] Grouped IR Parser Accuracy plot saved to {output_path}")

if __name__ == "__main__":
    generate_accuracy_plots()
