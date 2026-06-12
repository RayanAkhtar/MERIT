import matplotlib.pyplot as plt
import numpy as np
import os

# Data
candidates = [
    "No Data\n(Zero Evidence)", 
    "Full Data\n(Max Evidence)", 
    "Contradicting\n(Claimed Only)", 
    "Contradicting\n(Demonstrated Only)"
]
sigma_values = [0.144, 0.206, 0.287, 0.296]
colors = ['#95a5a6', '#2ecc71', '#f39c12', '#e74c3c']

fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars
bars = ax.bar(candidates, sigma_values, color=colors, edgecolor='black', zorder=3, width=0.6)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, f'{yval:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

# Confidence ranges (Uncertainty inverse)
# High Confidence -> 0.0 to 0.22
# Medium Confidence -> 0.22 to 0.29
# Low Confidence -> 0.29 to 0.35

ax.axhspan(0.0, 0.22, color='#2ecc71', alpha=0.15, zorder=1)
ax.axhspan(0.22, 0.29, color='#f1c40f', alpha=0.15, zorder=1)
ax.axhspan(0.29, 0.35, color='#e74c3c', alpha=0.15, zorder=1)

# Text labels for the ranges (placed on the right side)
ax.text(3.4, 0.11, 'High Confidence\nRegion ($\sigma \leq 0.22$)', color='#27ae60', fontsize=10, va='center', ha='left', fontweight='bold', alpha=0.9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
ax.text(3.4, 0.255, 'Medium Confidence\nRegion ($0.22 < \sigma \leq 0.29$)', color='#d35400', fontsize=10, va='center', ha='left', fontweight='bold', alpha=0.9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
ax.text(3.4, 0.32, 'Low Confidence\nRegion ($\sigma > 0.29$)', color='#c0392b', fontsize=10, va='center', ha='left', fontweight='bold', alpha=0.9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

ax.set_title('Study 12: Final Standard Deviation ($\sigma$) by Candidate Profile', fontsize=14, fontweight='bold', pad=20)
ax.set_ylabel('Final Standard Deviation ($\sigma$)', fontsize=12, fontweight='bold')
ax.set_ylim(0, 0.35)
ax.set_xlim(-0.5, 3.5) # Adjust xlim to make room for labels on the right
ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=2)

# Adjust layout to fit text on the right
plt.subplots_adjust(right=0.75)

output_path = os.path.join(os.getcwd(), 'scripts', 'confidence_chart.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved {output_path}")
