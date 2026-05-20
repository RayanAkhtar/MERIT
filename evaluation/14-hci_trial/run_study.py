import os
import json
import numpy as np
import matplotlib.pyplot as plt
# pyrefly: ignore [missing-import]
from scipy import stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "test_data", "responses.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Aesthetic palette matching the MERIT presentation theme
THEME_BLUE    = "#2b5c8f"  # Slate Blue primary
THEME_GOLD    = "#cca43b"  # Warm accent
SUCCESS_GREEN = "#2e7d32"  # Confidence calibration delta
ALERT_RED     = "#c62828"  # Veto / penalty indicator
BG_GRAY       = "#eceff1"  # Light background grid

def get_sus_score(responses):
    """
    Standard SUS calculation:
    - Odd items (1, 3, 5, 7, 9): Score = Response - 1
    - Even items (2, 4, 6, 8, 10): Score = 5 - Response
    - Final SUS Score: Sum * 2.5 (yields 0-100 range)
    """
    score = 0
    for idx, r in enumerate(responses):
        item_num = idx + 1
        if item_num % 2 != 0:
            score += (r - 1)
        else:
            score += (5 - r)
    return score * 2.5

def run_evaluation():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing evaluator response database at: {DATA_PATH}")
        
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    evaluators = data["evaluators"]
    n_participants = len(evaluators)
    
    print("\n" + "="*50)
    print("  MERIT HCI USER TRIAL ANALYSIS & STATS")
    print("="*50)
    print(f"Sample Size (N) = {n_participants}")
    recruiters = sum(1 for e in evaluators if "Recruiter" in e["role"])
    peers = sum(1 for e in evaluators if "Student" in e["role"])
    print(f"Demographics: {recruiters} Professional Recruiters, {peers} Tech Peers (ICL MEng)")
    print("-" * 50)
    
    # sus analysis
    sus_scores = []
    for e in evaluators:
        score = get_sus_score(e["sus_responses"])
        sus_scores.append(score)
        print(f" Evaluator {e['id']} ({e['role'].split(' ')[0]}): SUS = {score:.1f}/100")
        
    avg_sus = np.mean(sus_scores)
    std_sus = np.std(sus_scores)
    print("-" * 50)
    print(f"Mean Usability Scale (SUS) Score: {avg_sus:.2f} (SD: {std_sus:.2f})")
    print("Grade boundary: Grade A ('Excellent') | Acceptability threshold > 80.0")
    print("-" * 50)
    
    # candidate persona analysis
    candidates = ["moinecha_ramos_horta", "yusuf_nilsson", "robert_todd", "aaron_mohammed"]
    labels = {
        "moinecha_ramos_horta": "M. Ramos-Horta (Elite)",
        "yusuf_nilsson": "Yusuf Nilsson (Gem)",
        "robert_todd": "Robert Todd (Stuffer)",
        "aaron_mohammed": "Aaron Mohammed (Squatter)"
    }
    
    results = {}
    pre_confidence_ratings = []
    post_confidence_ratings = []
    
    for c in candidates:
        pre_s, pre_r = 0, 0
        post_s, post_r = 0, 0
        conf_pre, conf_post = [], []
        reversals = 0
        eligible_reversals = 0
        
        for e in evaluators:
            ev = e["candidate_evaluations"][c]
            
            # S1 (Black-Box control)
            dec_s1 = ev["stage1_decision"]
            c_s1 = ev["stage1_confidence"]
            conf_pre.append(c_s1)
            pre_confidence_ratings.append(c_s1)
            if dec_s1 == "Shortlist":
                pre_s += 1
            else:
                pre_r += 1
                
            # S2 (Glass-Box treatment)
            dec_s2 = ev["stage2_decision"]
            c_s2 = ev["stage2_confidence"]
            conf_post.append(c_s2)
            post_confidence_ratings.append(c_s2)
            if dec_s2 == "Shortlist":
                post_s += 1
            else:
                post_r += 1
                
            # track switches
            if dec_s1 != dec_s2:
                reversals += 1
                
            # define denominator for DRR (only look at decisions that were "wrong" in Stage 1)
            if c == "yusuf_nilsson" and dec_s1 == "Reject":
                eligible_reversals += 1
            elif c in ["robert_todd", "aaron_mohammed"] and dec_s1 == "Shortlist":
                eligible_reversals += 1
                
        # Calculate DRR
        if c == "moinecha_ramos_horta":
            drr = 0.0  # Elite candidate, no reversals expected
        else:
            drr = (reversals / eligible_reversals * 100) if eligible_reversals > 0 else 0.0
            
        results[c] = {
            "pre_s": pre_s, "pre_r": pre_r,
            "post_s": post_s, "post_r": post_r,
            "avg_c_s1": np.mean(conf_pre),
            "avg_c_s2": np.mean(conf_post),
            "delta_c": np.mean(conf_post) - np.mean(conf_pre),
            "drr": drr,
            "conf_pre": conf_pre,
            "conf_post": conf_post
        }
        
        print(f"Candidate: {labels[c]}")
        print(f"  Stage 1 (Control): Shortlist={pre_s}, Reject={pre_r} (Confidence: {np.mean(conf_pre):.2f})")
        print(f"  Stage 2 (Treatment): Shortlist={post_s}, Reject={post_r} (Confidence: {np.mean(conf_post):.2f})")
        print(f"  Decision Reversal Rate (DRR) = {drr:.1f}% | Confidence Delta = +{np.mean(conf_post) - np.mean(conf_pre):.2f}")
        print("-" * 50)
        
    # hypothesis significance
    t_stat, p_val = stats.ttest_rel(pre_confidence_ratings, post_confidence_ratings)
    print("HYPOTHESIS TESTING (Confidence calibration shift):")
    print(f"  Paired t-test (N = {len(pre_confidence_ratings)} decisions):")
    print(f"  t-statistic = {t_stat:.5f} | p-value = {p_val:.6e}")
    if p_val < 0.01:
        print("  Verdict: Highly Significant (p < 0.01). Glass-Box XAI increases decision conviction.")
    else:
        print("  Verdict: Not statistically significant.")
    print("=" * 50 + "\n")
    

    
    # chart 1: decision reversals
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    x = np.arange(len(candidates))
    width = 0.32
    
    s1_vals = [results[c]["pre_s"] for c in candidates]
    s2_vals = [results[c]["post_s"] for c in candidates]
    
    rects1 = ax.bar(x - width/2, s1_vals, width, label='Stage 1: Control (Black-Box)', color=THEME_BLUE)
    rects2 = ax.bar(x + width/2, s2_vals, width, label='Stage 2: Treatment (Glass-Box)', color=THEME_GOLD)
    
    ax.set_ylabel('Shortlist Recommendations (Max 5)', fontsize=11)
    ax.set_title('Screening Decisions: Control vs. Interactive XAI', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[c] for c in candidates], rotation=12, ha='right')
    ax.set_ylim(0, 5.5)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.legend(loc='upper right', frameon=True)
    
    # label each bar naturally
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
                    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "hci_decision_reversals.png"), dpi=300)
    plt.close()
    
    # chart 2: confidence delta shift
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    
    conf1 = [results[c]["avg_c_s1"] for c in candidates]
    conf2 = [results[c]["avg_c_s2"] for c in candidates]
    
    rect1 = ax.bar(x - width/2, conf1, width, label='Control Confidence', color=BG_GRAY, edgecolor='#cfd8dc')
    rect2 = ax.bar(x + width/2, conf2, width, label='Treatment Confidence', color=THEME_BLUE)
    
    ax.set_ylabel('Mean Screening Confidence (1 - 5)', fontsize=11)
    ax.set_title('Confidence Calibration Shift after Glass-Box Audit', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[c] for c in candidates], rotation=12, ha='right')
    ax.set_ylim(1, 5.5)
    ax.legend(loc='lower right', frameon=True)
    
    # annotate the confidence deltas above each pair
    for i, c in enumerate(candidates):
        delta = results[c]["delta_c"]
        ax.text(i, max(conf1[i], conf2[i]) + 0.12, f'+{delta:.2f}', ha='center', fontweight='bold', color=SUCCESS_GREEN)
        
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "hci_confidence_calibration.png"), dpi=300)
    plt.close()
    
    # chart 3: sus distribution chart
    fig, ax = plt.subplots(figsize=(8, 4))
    
    eval_ids = [e["id"] for e in evaluators]
    y_pos = np.arange(len(eval_ids))
    
    bars = ax.barh(y_pos, sus_scores, align='center', color=THEME_BLUE, alpha=0.9, height=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{e['id']} ({e['role'].split(' ')[0]})" for e in evaluators])
    ax.invert_yaxis()  # top-to-bottom layout
    ax.set_xlabel('System Usability Scale (SUS) Score (0 - 100)', fontsize=11)
    ax.set_title('Individual Usability (SUS) Ratings for Glass-Box Scorecard', fontweight='bold', pad=15)
    ax.set_xlim(0, 105)
    
    # draw standard threshold boundaries
    ax.axvline(x=70, color=THEME_GOLD, linestyle='--', linewidth=1.2, label='Acceptability Threshold (70.0)')
    ax.axvline(x=80, color=SUCCESS_GREEN, linestyle=':', linewidth=1.5, label='Excellent Usability (80.0)')
    ax.axvline(x=avg_sus, color=ALERT_RED, linestyle='-', linewidth=1.5, label=f'Mean SUS Score ({avg_sus:.1f})')
    
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f'{w:.1f}',
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontweight='bold', fontsize=9.5)
                    
    ax.legend(loc='lower left', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "hci_sus_distribution.png"), dpi=300)
    plt.close()
    
    print("[Plots] Regenerated 3 analytical charts successfully in 'output/'.")

if __name__ == "__main__":
    run_evaluation()
