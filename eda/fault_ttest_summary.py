import os
import pandas as pd
from scipy import stats
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
        normal_vals = run1_normal[sensor].dropna()
        fault_vals = run_fault[run_fault['sample'] >= 160][sensor].dropna()

        t_stat, p_value = stats.ttest_ind(normal_vals, fault_vals, equal_var=False)

        if p_value < 0.001:
            significance = "매우 유의함 (p<0.001)"
        elif p_value < 0.05:
            significance = "유의함 (p<0.05)"
        else:
            significance = "유의하지 않음"

        summary_rows.append({
            'fault': fault_number,
            'sensor': sensor,
            't_statistic': round(t_stat, 3),
            'p_value': round(p_value, 6),
            'significance': significance,
        })

summary_df = pd.DataFrame(summary_rows)

output_path = os.path.join(os.path.dirname(__file__), 'fault_ttest_summary.csv')
summary_df.to_csv(output_path, index=False)

print(summary_df.to_string(index=False))
print(f"\nSaved: {output_path}")