import os
import pyreadr
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = os.path.expanduser('~/Downloads')

normal = pd.read_csv(os.path.join(DATA_DIR, 'TEP_FaultFree_Testing.csv'))
normal = normal[normal['faultNumber'] == 0]

result = pyreadr.read_r(os.path.join(DATA_DIR, 'TEP_Faulty_Testing.RData'))
faulty = result['faulty_testing']

fault2 = faulty[faulty['faultNumber'] == 2]

run1_normal = normal[normal['simulationRun'] == 1].reset_index(drop=True)
run1_fault2 = fault2[fault2['simulationRun'] == 1].reset_index(drop=True)

fig, axes = plt.subplots(4, 1, figsize=(14, 12))

sensors = ['xmeas_1', 'xmeas_4', 'xmeas_7', 'xmeas_9']
titles  = [
    'A Feed Flow (kscmh)',
    'A/C Feed Flow (kscmh)',
    'Reactor Pressure (kPa)',
    'Reactor Temperature (deg C)'
]

for i, (sensor, title) in enumerate(zip(sensors, titles)):
    axes[i].plot(run1_normal[sensor], label='Normal', color='blue', linewidth=0.8)
    axes[i].plot(run1_fault2[sensor], label='Fault 2', color='red', linewidth=0.8)
    axes[i].axvline(x=160, color='orange', linestyle='--', label='Fault introduced (8hr)')
    axes[i].set_title(title)
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('fault2_comparison.png', dpi=150)
plt.show()
print("Saved: fault2_comparison.png")