import os
import sys

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from spearman_utils import run_spearman_analysis

def execute_study():
    human_rank_file = os.path.join(current_dir, "human_rankings.txt")
    output_dir = os.path.join(current_dir, "output")
    
    run_spearman_analysis(current_dir, human_rank_file, output_dir)

if __name__ == "__main__":
    execute_study()
