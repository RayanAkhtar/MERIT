import os
import pandas as pd
import matplotlib.pyplot as plt

ICL_NAVY = '#003E74'
ICL_LIGHT_BLUE = '#00AEEF'

def generate_accuracy_plots():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(current_dir, "output/accuracy_summary.csv")
    
    if not os.path.exists(summary_path):
        print("Error: Accuracy summary not found. Run the test first.")
        return

    df = pd.read_csv(summary_path)
    averages = df.drop(columns=["File"]).mean() * 100

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    colors = [ICL_NAVY] * len(averages)
    bars = ax.bar(averages.index, averages.values, color=colors, alpha=0.8, edgecolor='black')
    
    ax.set_title('IR Parser Performance Metrics (Study 04)', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Accuracy Score (%)', fontsize=12)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    
    # labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2, f'{height:.1f}%', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(current_dir, "output/ir_parser_accuracy.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    print(f"[SUCCESS] IR Parser Accuracy plot saved to {output_path}")

if __name__ == "__main__":
    generate_accuracy_plots()
