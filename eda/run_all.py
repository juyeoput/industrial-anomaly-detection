from plot_fault import load_data, plot_fault
from config import FAULT_CONFIGS

normal, faulty = load_data()

for fault_number in FAULT_CONFIGS.keys():
    plot_fault(fault_number, normal, faulty)

print("All fault plots generated.")