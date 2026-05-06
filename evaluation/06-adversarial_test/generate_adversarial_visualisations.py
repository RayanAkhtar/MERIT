import os
import pandas as pd
import matplotlib.pyplot as plt

# Imperial College London Official Palette
ICL_NAVY = '#003E74'
ICL_LIGHT_BLUE = '#00AEEF'
ICL_RED = '#E40046' # To highlight adversarial impact

def visualize_adversarial_results():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(current_dir, "output/multi_source_adversarial_matrix.csv")
    
    if not os.path.exists(summary_path):
        print("Error: Adversarial results not found.")
        return

    df = pd.read_csv(summary_path)

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    
    x = range(len(df))
    width = 0.6
    
    bars_merit = ax.bar(x, df["MERIT Score (Multi-Source)"], width, label='MERIT (Multi-Source)', color=ICL_NAVY)
    
    ax.set_title('MERIT Adversarial Robustness Profile', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Candidate Match Score (%)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df["Scenario"], fontsize=11)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', linestyle=':', alpha=0.6)

    baseline = df[df['Scenario'] == 'Honest']['MERIT Score (Multi-Source)'].values[0]
    
    reasons = {
        "Honest": "Baseline",
        "Ghost": "Density\nAudit",
        "Fraud": "Evidence\nConflict",
        "Stale": "Skill\nDecay",
        "Gamer": "Recency\nGaming",
        "Squatter": "Identity\nVeto",
        "Smart_squatter": "Name\nInjection",
        "Shadow": "Zero\nVerification",
        "Inflater": "Project\nDilution"
    }


    reasons_map = {k.lower(): v for k, v in reasons.items()}

    # Add bar labels and deltas
    for i, bar in enumerate(bars_merit):
        yval = bar.get_height()
        raw_label = str(df.iloc[i]['Scenario'])
        label = raw_label.lower()
        delta = yval - baseline
        reason = reasons_map.get(label, "")
        
        # Main Score
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}%", 
                 ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Delta and Reason (Stacked vertically)
        if raw_label != "Honest":
            color = '#d63031' if delta < 0 else '#27ae60'
            sign = "+" if delta > 0 else ""
            
            # Special case for the successful bypass
            if label == "smart_squatter" and abs(delta) < 0.1:
                reason = "Name\nSimilarity"
                color = '#f39c12' # Amber to show "System Warning/Bypass"
            
            display_text = f"{sign}{delta:.1f}%\n({reason})"
            
            ax.text(bar.get_x() + bar.get_width()/2, yval + 4, display_text, 
                     ha='center', va='bottom', color=color, 
                     fontsize=8.5, fontweight='semibold', linespacing=1.2)

    ax.set_ylim(0, 100)
    plt.tight_layout()
    output_path = os.path.join(current_dir, "output/adversarial_robustness.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    print(f"[SUCCESS] Adversarial Robustness plot saved to {output_path}")

if __name__ == "__main__":
    visualize_adversarial_results()
