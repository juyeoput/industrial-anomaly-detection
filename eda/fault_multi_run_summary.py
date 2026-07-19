import os
import pandas as pd
from config import FAULT_CONFIGS
from plot_fault import load_data

print("데이터 불러오는 중...")
normal, faulty = load_data()

SAMPLE_RUNS = [1, 25, 50, 100, 150, 200, 250, 300, 400, 500]

summary_rows = []

for fault_number, config in FAULT_CONFIGS.items():
    fault_data = faulty[faulty['faultNumber'] == fault_number]

    for sensor in config['sensors']:
        pct_changes = []
        std_ratios = []

        for run in SAMPLE_RUNS:
            run_normal = normal[normal['simulationRun'] == run]
            run_fault = fault_data[fault_data['simulationRun'] == run]

            if run_normal.empty or run_fault.empty:
                continue

            normal_mean = run_normal[sensor].mean()
            normal_std = run_normal[sensor].std()

            fault_after = run_fault[run_fault['sample'] >= 160][sensor]
            fault_mean = fault_after.mean()
            fault_std = fault_after.std()

            if normal_mean != 0:
                pct_changes.append((fault_mean - normal_mean) / normal_mean * 100)
            if normal_std > 0:
                std_ratios.append(fault_std / normal_std)

        if pct_changes and std_ratios:
            summary_rows.append({
                'fault': fault_number,
                'sensor': sensor,
                'n_runs': len(pct_changes),
                'pct_change_mean_avg': round(sum(pct_changes) / len(pct_changes), 2),
                'pct_change_mean_std': round(pd.Series(pct_changes).std(), 2),
                'std_ratio_avg': round(sum(std_ratios) / len(std_ratios), 2),
                'std_ratio_std': round(pd.Series(std_ratios).std(), 2),
            })

summary_df = pd.DataFrame(summary_rows)
output_path = os.path.join(os.path.dirname(__file__), 'fault_multi_run_summary.csv')
summary_df.to_csv(output_path, index=False)

print(summary_df.to_string(index=False))
print(f"\nSaved: {output_path}")