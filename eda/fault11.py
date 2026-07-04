import os
import pyreadr
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = os.path.expanduser('~/Downloads')

normal = pd.read_csv(os.path.join(DATA_DIR, 'TEP_FaultFree_Testing.csv'))
normal = normal[normal['faultNumber'] == 0]

result = pyreadr.read_r(os.path.join(DATA_DIR, 'TEP_Faulty_Testing.RData'))
faulty = result['faulty_testing']

fault11 = faulty[faulty['faultNumber'] == 11]

run1_normal = normal[normal['simulationRun'] == 1].reset_index(drop=True)
run1_fault11 = fault11[fault11['simulationRun'] == 1].reset_index(drop=True)

fig, axes = plt.subplots(4, 1, figsize=(14, 12))

sensors = ['xmeas_9', 'xmeas_21', 'xmeas_7', 'xmv_10']
titles  = [
    'Reactor Temperature (deg C)',
    'Reactor CW Outlet Temp (deg C)',
    'Reactor Pressure (kPa)',
    'Reactor CW Valve (%open)'
]

for i, (sensor, title) in enumerate(zip(sensors, titles)):
    axes[i].plot(run1_normal[sensor], label='Normal', color='blue', linewidth=0.8)
    axes[i].plot(run1_fault11[sensor], label='Fault 11', color='red', linewidth=0.8)
    axes[i].axvline(x=160, color='orange', linestyle='--', label='Fault introduced (8hr)')
    axes[i].set_title(title)
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('fault11_comparison.png', dpi=150)
plt.show()
print("Saved: fault11_comparison.png")