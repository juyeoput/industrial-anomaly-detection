import os
import pandas as pd
from plot_fault import load_data

print("Loading data...")
normal, faulty = load_data()

SAMPLE_RUNS = [1, 25, 50, 100, 150, 200, 250, 300, 400, 500]
SENSORS = ["xmeas_24", "xmeas_30", "xmeas_35", "xmeas_40"]

WINDOWS = {
    "early": (160, 260),
    "late": (300, 960),
    "full": (160, 960),
}

fault2 = faulty[faulty["faultNumber"] == 2]
summary_rows = []

for sensor in SENSORS:
    for window_name, (start, end) in WINDOWS.items():
        run_metrics = []

        for run in SAMPLE_RUNS:
            run_normal = normal[normal["simulationRun"] == run]
            run_fault = fault2[fault2["simulationRun"] == run]

            if run_normal.empty or run_fault.empty:
                continue

            normal_window = run_normal[
                run_normal["sample"].between(start, end)
            ][sensor].dropna()

            fault_window = run_fault[
                run_fault["sample"].between(start, end)
            ][sensor].dropna()

            if normal_window.empty or fault_window.empty:
                continue

            normal_mean = normal_window.mean()
            normal_std = normal_window.std()
            fault_mean = fault_window.mean()
            fault_std = fault_window.std()

            if normal_mean == 0 or normal_std == 0:
                continue

            pct_change = (
                (fault_mean - normal_mean) / normal_mean * 100
            )
            std_ratio = fault_std / normal_std

            run_metrics.append({
                "run": run,
                "pct_change": pct_change,
                "std_ratio": std_ratio,
            })

        if not run_metrics:
            continue

        metrics_df = pd.DataFrame(run_metrics)

        summary_rows.append({
            "fault": 2,
            "sensor": sensor,
            "window": window_name,
            "sample_range": f"{start}-{end}",
            "n_runs": len(metrics_df),
            "pct_change_mean_avg": round(
                metrics_df["pct_change"].mean(), 2
            ),
            "pct_change_mean_std": round(
                metrics_df["pct_change"].std(), 2
            ),
            "pct_change_abs_avg": round(
                metrics_df["pct_change"].abs().mean(), 2
            ),
            "pct_change_positive_rate": round(
                (metrics_df["pct_change"] > 0).mean(), 2
            ),
            "std_ratio_avg": round(
                metrics_df["std_ratio"].mean(), 2
            ),
            "std_ratio_std": round(
                metrics_df["std_ratio"].std(), 2
            ),
            "std_ratio_gt_1_rate": round(
                (metrics_df["std_ratio"] > 1).mean(), 2
            ),
        })

summary_df = pd.DataFrame(summary_rows)

summary_df = summary_df.sort_values(
    by=["sensor", "window"]
).reset_index(drop=True)

output_path = os.path.join(
    os.path.dirname(__file__),
    "fault2_composition_multi_run_summary.csv",
)

summary_df.to_csv(output_path, index=False)

print(summary_df.to_string(index=False))
print(f"\nSaved: {output_path}")