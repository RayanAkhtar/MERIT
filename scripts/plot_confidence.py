import matplotlib.pyplot as plt
import numpy as np
import os

# Data
candidates = [
    "Full\nNegative\n(All Evidence)",
    "Full\nData\n(Max Evidence)", 
    "Negative\n(Claimed\nOnly)",
    "Contradicting\n(Claimed\nOnly)", 
    "Contradicting\n(Demonstrated\nOnly)",
    "Strong\nConflict\n(Max Demonstrated)",
    "Claims\nOnly\n(Max Score)",
    "Negative\nClaim\n(Single Source)",
    "Average\nClaim\n(Single Source)"
]
sigma_values = [0.144, 0.206, 0.236, 0.287, 0.296, 0.300, 0.321, 0.368, 0.382]

colors = []
for val in sigma_values:
    if val <= 0.275:
        colors.append('#2ecc71')
    elif val <= 0.35:
        colors.append('#f39c12')
    else:
        colors.append('#e74c3c')

fig, ax = plt.subplots(figsize=(20, 8))

# Plot bars
bars = ax.bar(candidates, sigma_values, color=colors, edgecolor='black', zorder=3, width=0.6)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, f'{yval:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

# Confidence ranges (Uncertainty inverse)
# High Confidence -> 0.0 to 0.275
# Medium Confidence -> 0.275 to 0.35
# Low Confidence -> 0.35 to 0.40

ax.axhspan(0.0, 0.275, color='#2ecc71', alpha=0.15, zorder=1)
ax.axhspan(0.275, 0.35, color='#f1c40f', alpha=0.15, zorder=1)
ax.axhspan(0.35, 0.40, color='#e74c3c', alpha=0.15, zorder=1)

# Text labels for the ranges (placed on the right side)
ax.text(8.6, 0.1375, 'High Confidence\nRegion ($\sigma \leq 0.275$)', color='#27ae60', fontsize=11, va='center', ha='left', fontweight='bold', alpha=0.9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
ax.text(8.6, 0.3125, 'Medium Confidence\nRegion ($0.275 < \sigma \leq 0.35$)', color='#d35400', fontsize=11, va='center', ha='left', fontweight='bold', alpha=0.9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
ax.text(8.6, 0.375, 'Low Confidence\nRegion ($\sigma > 0.35$)', color='#c0392b', fontsize=11, va='center', ha='left', fontweight='bold', alpha=0.9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

ax.set_title('Study 12: Final Standard Deviation ($\sigma$) by Candidate Profile', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('Final Standard Deviation ($\sigma$)', fontsize=14, fontweight='bold')
ax.set_ylim(0, 0.40)
ax.set_xlim(-0.5, 8.5) # Adjust xlim to make room for labels on the right
ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=2)

# Adjust layout to fit text on the right
plt.subplots_adjust(right=0.75)

output_path = os.path.join(os.getcwd(), 'scripts', 'confidence_chart.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved {output_path}")
