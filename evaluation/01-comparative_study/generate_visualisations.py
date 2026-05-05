import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def load_csv_data(filepath):
    """
    utility to load study results from csv 
    it normalises different naming conventions used across the study scripts
    """
    data = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Candidate Name') or row.get('candidate_name')
                if not name:
                    continue
                score_val = 0.0
                # normalising the score key across different study outputs
                for key in ['Score', 'Final Score', 'Modern AI Score', 'ai_score', 'merit_score', 'MERIT CV Score (%)', 'MERIT Total Score']:
                    if key in row and row[key]:
                        try:
                            score_val = float(row[key])
                            break
                        except: pass
                
                data[name] = {
                    'rank': int(row['Rank']),
                    'score': score_val
                }
    return data

def plot_rank_displacement_chart(title, focus_candidates, filename, baseline, ai, cv_only, merit_full):
    """
    generates a bump chart visualising the rank displacement for a subset of personas
    used to support the result analysis section of the project report
    """
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    stages = ['Traditional ATS', 'Modern AI ATS', 'MERIT (CV-Only)', 'MERIT (Full)']
    candidates = list(baseline.keys())
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(20, 12), dpi=300)
    fig.patch.set_facecolor('white')
    
    # using imperial college london palette for the primary personas
    persona_styles = {
        'Alex Rivers': {'colour': '#003E74', 'label': 'The Verifiable Elite'},
        'Buzz Ward': {'colour': '#D50032', 'label': 'The Keyword Stuffer'},
        'Jordan Smith': {'colour': '#00853F', 'label': 'The Hidden Gem'},
        'Sam Old': {'colour': '#E87722', 'label': 'The Stale Pro'},
        'Carl Corp': {'colour': '#5D295F', 'label': 'The Corporate Giant'},
        'Ghost Gary': {'colour': '#4A4A4A', 'label': 'The Unverified Ghost'},
        'Felix Vance': {'colour': '#FF0000', 'label': 'The Identity Mismatch'},
        'Nadia Nomad': {'colour': '#FFD700', 'label': 'The Breadth-Only Generalist'},
        'Fiona Frost': {'colour': '#800000', 'label': 'The Evidence of Absence'},
        'Kim Junior': {'colour': '#8BC34A', 'label': 'The High-Potential Junior'}
    }
    
    x = np.arange(len(stages))
    left_labels = []
    right_labels = []

    # sort to ensure consistent z-ordering with important ones on top
    sorted_candidates = sorted(candidates, key=lambda c: merit_full.get(c, {'rank': 11})['rank'])

    for cand in sorted_candidates:
        y = [
            baseline.get(cand, {'rank': 11})['rank'],
            ai.get(cand, {'rank': 11})['rank'],
            cv_only.get(cand, {'rank': 11})['rank'],
            merit_full.get(cand, {'rank': 11})['rank']
        ]
        
        style = persona_styles.get(cand, {'colour': '#EEEEEE', 'label': 'Unknown'})
        
        # determine visibility based on focus_candidates to highlight specific trends
        if focus_candidates is None: # show all personas at full visibility
            alpha = 1.0
            colour = style['colour']
            linewidth = 4.5
            is_highlighted = True
        elif cand in focus_candidates:
            alpha = 1.0
            colour = style['colour']
            linewidth = 5.5
            is_highlighted = True
        else: # dim background personas
            alpha = 0.1
            colour = '#D0D0D0'
            linewidth = 1.5
            is_highlighted = False
        
        ax.plot(x, y, color=colour, linewidth=linewidth, alpha=alpha, zorder=10 if is_highlighted else 1, 
                marker='o', markersize=10 if is_highlighted else 0, markeredgecolor='white', markeredgewidth=2)
        
        if is_highlighted:
            # prevent label overlapping on the left axis
            ly = y[0]
            while any(abs(ly - existing) < 0.28 for existing in left_labels):
                ly += 0.15
            left_labels.append(ly)
            ax.text(-0.12, ly, cand, va='center', ha='right', color=colour, fontweight='bold', fontsize=12)
            
            # prevent label overlapping on the right axis
            ry = y[-1]
            while any(abs(ry - existing) < 0.35 for existing in right_labels):
                ry += 0.2
            right_labels.append(ry)
            
            display_text = f"{cand}\n({style['label']})"
            ax.text(3.12, ry, display_text, va='center', ha='left', color=colour, fontweight='bold', fontsize=11, linespacing=1.2)

    # styling the chart for the final report
    ax.set_ylim(10.8, 0.2) 
    ax.set_xlim(-1.5, 5.0)
    ax.set_xticks(x)
    ax.set_xticklabels(stages, fontsize=15, fontweight='bold', color='#111111')
    ax.set_yticks(range(1, 11))
    ax.set_yticklabels([f"Rank {i}" for i in range(1, 11)], color='#888888', fontsize=12)
    ax.grid(True, axis='y', color='#F5F5F5', linestyle='-', alpha=0.9, zorder=0)
    
    plt.title(title, fontsize=24, pad=50, fontweight='bold', color='#000000')
    
    # cleaning up the frame
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.spines['bottom'].set_linewidth(1.5)
    
    plt.tight_layout(pad=4.0)
    png_path = os.path.join(output_dir, filename)
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] {filename} generated.")

def generate_evaluation_visualisations():
    # load all four study stages for the comparative plots
    base_dir = os.path.dirname(__file__)
    baseline = load_csv_data(os.path.join(base_dir, 'output/baseline_rankings.csv'))
    ai = load_csv_data(os.path.join(base_dir, 'output/modern_ai_ats_rankings.csv'))
    cv_only = load_csv_data(os.path.join(base_dir, 'output/merit_cv_only_rankings.csv'))
    merit_full = load_csv_data(os.path.join(base_dir, 'output/merit_all_sources_rankings.csv'))

    all_names = list(baseline.keys())
    
    # holistic view of all personas
    plot_rank_displacement_chart("Holistic Results: Systemic Rank Displacement", all_names, "rank_displacement_holistic.png", baseline, ai, cv_only, merit_full)
    
    # highlighting candidates where multi-source fusion worked best
    success_highlights = ["Alex Rivers", "Jordan Smith", "Buzz Ward", "Sam Old", "Nadia Nomad"]
    plot_rank_displacement_chart("Systemic Successes: Discovery & Noise Filtering", success_highlights, "rank_displacement_successes.png", baseline, ai, cv_only, merit_full)
    
    # highlighting the proprietary data gap
    limitation_highlights = ["Carl Corp", "Alex Rivers", "Sam Old"]
    plot_rank_displacement_chart("Systemic Limitations: Proprietary Data Gaps", limitation_highlights, "rank_displacement_limitations.png", baseline, ai, cv_only, merit_full)
    
    # focusing on identity and attribution audits
    edge_case_highlights = ["Felix Vance", "Fiona Frost", "Ghost Gary", "Alex Rivers"]
    plot_rank_displacement_chart("Verification Edge Cases: Identity & Attribution", edge_case_highlights, "rank_displacement_edge_cases.png", baseline, ai, cv_only, merit_full)

if __name__ == "__main__":
    generate_evaluation_visualisations()
