import os
import pandas as pd
from config import FAULT_CONFIGS
from plot_fault import load_data

print("데이터 불러오는 중...")
normal, faulty = load_data()

run1_normal = normal[normal['simulationRun'] == 1].reset_index(drop=True)

summary_rows = []

for fault_number, config in FAULT_CONFIGS.items():
    fault_data = faulty[faulty['faultNumber'] == fault_number]
    run_fault = fault_data[fault_data['simulationRun'] == 1].reset_index(drop=True)

    for sensor in config['sensors']:
        normal_mean = run1_normal[sensor].mean()
        normal_std = run1_normal[sensor].std()

        fault_after = run_fault[run_fault['sample'] >= 160][sensor]
        fault_mean = fault_after.mean()
        fault_std = fault_after.std()

        pct_change_mean = (fault_mean - normal_mean) / normal_mean * 100
        std_ratio = fault_std / normal_std if normal_std > 0 else None

        summary_rows.append({
            'fault': fault_number,
            'sensor': sensor,
            'normal_mean': round(normal_mean, 4),
            'normal_std': round(normal_std, 4),
            'fault_mean': round(fault_mean, 4),
            'fault_std': round(fault_std, 4),
            'pct_change_mean': round(pct_change_mean, 2),
            'std_ratio': round(std_ratio, 2) if std_ratio else None,
        })

summary_df = pd.DataFrame(summary_rows)

output_path = os.path.join(os.path.dirname(__file__), 'fault_sensor_summary.csv')
summary_df.to_csv(output_path, index=False)

print(summary_df.to_string(index=False))
print(f"\nSaved: {output_path}")