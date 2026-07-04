import os
import pyreadr
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = os.path.expanduser('~/Downloads')

normal = pd.read_csv(os.path.join(DATA_DIR, 'TEP_FaultFree_Testing.csv'))
normal = normal[normal['faultNumber'] == 0]

result = pyreadr.read_r(os.path.join(DATA_DIR, 'TEP_Faulty_Testing.RData'))
faulty = result['faulty_testing']

fault12 = faulty[faulty['faultNumber'] == 12]

run1_normal = normal[normal['simulationRun'] == 1].reset_index(drop=True)
run1_fault12 = fault12[fault12['simulationRun'] == 1].reset_index(drop=True)

fig, axes = plt.subplots(4, 1, figsize=(14, 12))

sensors = ['xmeas_11', 'xmeas_22', 'xmeas_12', 'xmeas_13']
titles  = [
    'Separator Temperature (deg C)',
    'Separator CW Outlet Temp (deg C)',
    'Separator Level (%)',
    'Separator Pressure (kPa)'
]

for i, (sensor, title) in enumerate(zip(sensors, titles)):
    axes[i].plot(run1_normal[sensor], label='Normal', color='blue', linewidth=0.8)
    axes[i].plot(run1_fault12[sensor], label='Fault 12', color='red', linewidth=0.8)
    axes[i].axvline(x=160, color='orange', linestyle='--', label='Fault introduced (8hr)')
    axes[i].set_title(title)
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('fault12_comparison.png', dpi=150)
plt.show()
print("Saved: fault12_comparison.png")