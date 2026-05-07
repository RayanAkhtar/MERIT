import json
import os
import shutil

def apply_nuclear_sabotage():

    base_dir = "."
    if os.path.basename(os.getcwd()) == "evaluation":
        study_dir = "10-spearman_signal_dissonance_failure_case"
    else:
        study_dir = "evaluation/10-spearman_signal_dissonance_failure_case"
        
    github_dir = os.path.join(study_dir, "test_data/candidates/github")
    linkedin_dir = os.path.join(study_dir, "test_data/candidates/linkedin")
    
    if not os.path.exists(github_dir):
        print(f"[ERROR] Could not find study directory at: {os.path.abspath(study_dir)}")
        exit(1)
    
    # candidates in order of human ranking (1-10)
    # we want to swap signals between top 3 and bottom 3
    top_3 = [
        "012_Moinecha_Ramos-Horta_Mid-Level_Backend_Engineer.json",
        "0103_Aaron_Mohammed_Mid-Level_Backend_Engineer.json",
        "011_Yusuf_Nilsson_Junior_Backend_Engineer.json"
    ]
    
    bottom_3 = [
        "0108_Jude_Washington_Junior_iOS_Developer.json",
        "0109_XiuYing_Loh_Mid-Level_Android_Developer.json",
        "0112_Robert_Todd_Principal_QA_Engineer.json"
    ]
    
    print(f"[NUCLEAR SABOTAGE] Breaking Study 10...")

    # swap signals 
    for i in range(3):
        top_f = top_3[i]
        bot_f = bottom_3[i]
        
        # paths
        top_gh_path = os.path.join(github_dir, top_f)
        bot_gh_path = os.path.join(github_dir, bot_f)
        top_li_path = os.path.join(linkedin_dir, top_f)
        bot_li_path = os.path.join(linkedin_dir, bot_f)
        
        # swap github
        with open(top_gh_path, 'r') as f: top_gh = json.load(f)
        with open(bot_gh_path, 'r') as f: bot_gh = json.load(f)
        
        # add ecosystem dissonance to the top candidates new (bad) profile
        bot_gh['top_languages'] = ["Swift", "Objective-C"] # backend expert now looks like an iOS dev
        bot_gh['repositories'] = bot_gh.get('repositories', [])[:1] # stripped to 1 repo
        
        # add identity dissonance (mismatch name) triggers penalty
        bot_gh['login'] = "random_user_123" 
        
        # save swapped
        with open(top_gh_path, 'w') as f: json.dump(bot_gh, f, indent=2)
        with open(bot_gh_path, 'w') as f: json.dump(top_gh, f, indent=2)
        
        # swap linkedin
        with open(top_li_path, 'r') as f: top_li = json.load(f)
        with open(bot_li_path, 'r') as f: bot_li = json.load(f)
        
        with open(top_li_path, 'w') as f: json.dump(bot_li, f, indent=2)
        with open(bot_li_path, 'w') as f: json.dump(top_li, f, indent=2)

        print(f"  - Swapped signals: {top_f} <-> {bot_f}")

    print("[SUCCESS] Study 10 is now intentionally sabotaged (Adversarial Inversion).")

if __name__ == "__main__":
    apply_nuclear_sabotage()
