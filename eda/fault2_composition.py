import os
import pandas as pd
import matplotlib.pyplot as plt
from plot_fault import load_data, IMG_DIR

print("Loading data...")
normal, faulty = load_data()

fault2 = faulty[faulty['faultNumber'] == 2]

run1_normal = normal[normal['simulationRun'] == 1].reset_index(drop=True)
run1_fault2 = fault2[fault2['simulationRun'] == 1].reset_index(drop=True)

sensors = ['xmeas_24', 'xmeas_30', 'xmeas_35', 'xmeas_40']
titles = [
    'Reactor Feed B Composition (mol%)',
    'Purge B Composition (mol%)',
    'Purge G Composition (mol%)',
    'Product G Composition (mol%)'
]

# --- Plot ---
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

for i, (sensor, title) in enumerate(zip(sensors, titles)):
    axes[i].plot(run1_normal[sensor], label='Normal', color='blue', linewidth=0.8)
    axes[i].plot(run1_fault2[sensor], label='Fault 2', color='red', linewidth=0.8)
    axes[i].axvline(x=160, color='orange', linestyle='--', label='Fault introduced (8hr)')
    axes[i].set_title(title)
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
save_path = os.path.join(IMG_DIR, 'fault2_composition_comparison.png')
plt.savefig(save_path, dpi=150)
plt.close(fig)
print(f"Saved: {save_path}")

# --- Numerical summary + CSV ---
summary_rows = []

for sensor, name in zip(sensors, titles):
    normal_mean = run1_normal[sensor].mean()
    normal_std = run1_normal[sensor].std()

    fault_after = run1_fault2[run1_fault2['sample'] >= 160][sensor]
    fault_mean = fault_after.mean()
    fault_std = fault_after.std()

    pct_change = (fault_mean - normal_mean) / normal_mean * 100 if normal_mean != 0 else float('nan')
    std_ratio = fault_std / normal_std if normal_std > 0 else float('nan')

    summary_rows.append({
        'fault': 2,
        'sensor': sensor,
        'sensor_name': name,
        'normal_mean': round(normal_mean, 4),
        'normal_std': round(normal_std, 4),
        'fault_mean': round(fault_mean, 4),
        'fault_std': round(fault_std, 4),
        'pct_change_mean': round(pct_change, 2),
        'std_ratio': round(std_ratio, 2),
    })

summary_df = pd.DataFrame(summary_rows)

output_path = os.path.join(os.path.dirname(__file__), 'fault2_composition_summary.csv')
summary_df.to_csv(output_path, index=False)

print("\n=== Numerical Summary ===")
print(summary_df.to_string(index=False))
print(f"\nSaved: {output_path}")