import os
import pyreadr
import pandas as pd
import matplotlib.pyplot as plt
from config import FAULT_CONFIGS

DATA_DIR = os.path.expanduser('~/Downloads')
IMG_DIR = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(IMG_DIR, exist_ok=True)


def load_data():
    normal = pd.read_csv(os.path.join(DATA_DIR, 'TEP_FaultFree_Testing.csv'))
    normal = normal[normal['faultNumber'] == 0]

    result = pyreadr.read_r(os.path.join(DATA_DIR, 'TEP_Faulty_Testing.RData'))
    faulty = result['faulty_testing']

    return normal, faulty


def plot_fault(fault_number, normal, faulty, run=1):
    config = FAULT_CONFIGS[fault_number]
    sensors = config['sensors']
    titles = config['titles']

    fault_data = faulty[faulty['faultNumber'] == fault_number]

    run_normal = normal[normal['simulationRun'] == run].reset_index(drop=True)
    run_fault = fault_data[fault_data['simulationRun'] == run].reset_index(drop=True)

    fig, axes = plt.subplots(len(sensors), 1, figsize=(14, 3 * len(sensors)))
    if len(sensors) == 1:
        axes = [axes]

    for i, (sensor, title) in enumerate(zip(sensors, titles)):
        axes[i].plot(run_normal[sensor], label='Normal', color='blue', linewidth=0.8)
        axes[i].plot(run_fault[sensor], label=f'Fault {fault_number}', color='red', linewidth=0.8)
        axes[i].axvline(x=160, color='orange', linestyle='--', label='Fault introduced (8hr)')
        axes[i].set_title(title)
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(IMG_DIR, f'fault{fault_number}_comparison.png')
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {save_path}")