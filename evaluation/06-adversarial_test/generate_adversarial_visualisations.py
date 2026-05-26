import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Imperial College London Official Palette
ICL_NAVY = '#003E74'
ICL_LIGHT_BLUE = '#00AEEF'
ICL_RED = '#E40046' # To highlight adversarial impact
ICL_WARNING_YELLOW = '#F4B942'  # Smart Squatter bypass (0.0% delta vs honest)

CV_ONLY_COLOR = "#888888"
FULL_MERIT_COLOR = ICL_NAVY


def visualize_cv_vs_full_comparison():
    """Grouped bar chart: CV-only vs Full MERIT score per adversarial scenario."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(current_dir, "output/multi_source_adversarial_matrix.csv")
    if not os.path.exists(summary_path):
        print("Error: Adversarial results not found.")
        return

    df = pd.read_csv(summary_path)
    scenarios = df["Scenario"].tolist()
    cv_scores = df["ATS Score (CV Only)"].values
    full_scores = df["MERIT Score (Multi-Source)"].values

    x = np.arange(len(scenarios))
    width = 0.36

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    bars_cv = ax.bar(x - width / 2, cv_scores, width, label="MERIT (CV Only)", color=CV_ONLY_COLOR)
    bars_full = ax.bar(x + width / 2, full_scores, width, label="MERIT (Full multi-source)", color=FULL_MERIT_COLOR)

    ax.set_title(
        "Study 06: CV-Only vs Full MERIT by Adversarial Scenario",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_ylabel("Match score (%)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=10, rotation=25, ha="right")
    ax.set_ylim(0, 72)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    honest_full = df.loc[df["Scenario"] == "Honest", "MERIT Score (Multi-Source)"].iloc[0]
    ax.axhline(
        honest_full,
        color=ICL_RED,
        linestyle="--",
        linewidth=1.2,
        alpha=0.85,
        label=f"Honest Full MERIT ({honest_full:.1f}%)",
    )

    for b_cv, b_full in zip(bars_cv, bars_full):
        for bar in (b_cv, b_full):
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.8,
                f"{h:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    plt.tight_layout()
    out = os.path.join(current_dir, "output/adversarial_cv_vs_full.png")
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[SUCCESS] CV vs Full comparison plot saved to {out}")


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

    baseline = df[df['Scenario'] == 'Honest']['MERIT Score (Multi-Source)'].values[0]

    reasons = {
        "honest": "Baseline",
        "ghost": "Density\nAudit",
        "fraud": "Evidence\nConflict",
        "stale": "Skill\nDecay",
        "gamer": "Recency\nGaming",
        "squatter": "Identity\nVeto",
        "smart_squatter": "Successful\nName Squat",
        "shadow": "Zero\nVerification",
        "inflater": "Project\nDilution",
    }

    def scenario_key(name: str) -> str:
        return str(name).lower().replace(" ", "_")

    bars_merit = ax.bar(
        x,
        df["MERIT Score (Multi-Source)"],
        width,
        label='MERIT (Multi-Source)',
        color=ICL_NAVY,
    )

    ax.set_title('MERIT Adversarial Robustness Profile', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Candidate Match Score (%)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df["Scenario"], fontsize=11)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', linestyle=':', alpha=0.6)

    # Add bar labels and deltas
    for i, bar in enumerate(bars_merit):
        yval = bar.get_height()
        raw_label = str(df.iloc[i]['Scenario'])
        key = scenario_key(raw_label)
        delta = yval - baseline
        reason = reasons.get(key, "")

        # Main Score
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}%",
                 ha='center', va='bottom', fontweight='bold', fontsize=10)

        # Delta and Reason (Stacked vertically)
        if raw_label != "Honest":
            sign = "+" if delta > 0 else ""
            color = '#d63031' if delta < 0 else '#27ae60'

            # Successful integrity bypass: warn in annotation only (bar stays navy)
            if key == "smart_squatter" and abs(delta) < 0.1:
                color = ICL_WARNING_YELLOW

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

def visualize_all():
    visualize_adversarial_results()
    visualize_cv_vs_full_comparison()


if __name__ == "__main__":
    visualize_all()
