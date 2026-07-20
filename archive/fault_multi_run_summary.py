import os

import numpy as np
import pandas as pd

from config import FAULT_CONFIGS
from plot_fault import load_data


print("Loading data...")
normal, faulty = load_data()

# Keep the original 10-run descriptive validation set.
SAMPLE_RUNS = [
    1,
    25,
    50,
    100,
    150,
    200,
    250,
    300,
    400,
    500,
]

WINDOWS = {
    "early": (160, 260),
    "late": (300, 960),
    "full": (160, 960),
}


normal_by_run = {
    run: normal[normal["simulationRun"] == run]
    for run in SAMPLE_RUNS
}

summary_rows = []

for fault_number, config in FAULT_CONFIGS.items():
    print(f"Processing Fault {fault_number}...")

    fault_data = faulty[
        faulty["faultNumber"] == fault_number
    ]

    fault_by_run = {
        run: fault_data[
            fault_data["simulationRun"] == run
        ]
        for run in SAMPLE_RUNS
    }

    for sensor in config["sensors"]:
        for window_name, (start, end) in WINDOWS.items():
            run_metrics = []

            for run in SAMPLE_RUNS:
                run_normal = normal_by_run[run]
                run_fault = fault_by_run[run]

                if run_normal.empty or run_fault.empty:
                    continue

                # Normal and faulty data use the same sample window.
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

                if (
                    not np.isfinite(normal_std)
                    or normal_std <= 0
                ):
                    continue

                # A zero fault standard deviation is valid and may
                # indicate a constant or saturated post-fault state.
                if not np.isfinite(fault_std):
                    continue

                mean_difference = (
                    fault_mean - normal_mean
                )

                if normal_mean != 0:
                    pct_change = (
                        mean_difference
                        / normal_mean
                        * 100
                    )
                else:
                    pct_change = np.nan

                std_ratio = (
                    fault_std / normal_std
                )

                run_metrics.append({
                    "run": run,
                    "pct_change": pct_change,
                    "std_ratio": std_ratio,
                })

            if not run_metrics:
                continue

            metrics_df = pd.DataFrame(run_metrics)

            positive_rate = (
                metrics_df["pct_change"] > 0
            ).mean()

            negative_rate = (
                metrics_df["pct_change"] < 0
            ).mean()

            mean_direction_consistency = max(
                positive_rate,
                negative_rate,
            )

            if positive_rate > negative_rate:
                mean_direction = "increase"
            elif negative_rate > positive_rate:
                mean_direction = "decrease"
            else:
                mean_direction = "mixed"

            variance_increase_rate = (
                metrics_df["std_ratio"] > 1
            ).mean()

            summary_rows.append({
                "fault": fault_number,
                "sensor": sensor,
                "window": window_name,
                "sample_range": f"{start}-{end}",
                "n_runs": len(metrics_df),

                "pct_change_mean_avg": round(
                    metrics_df["pct_change"].mean(),
                    4,
                ),
                "pct_change_mean_std": round(
                    metrics_df["pct_change"].std(),
                    4,
                ),
                "pct_change_abs_avg": round(
                    metrics_df["pct_change"]
                    .abs()
                    .mean(),
                    4,
                ),

                "mean_direction": mean_direction,
                "mean_direction_consistency": round(
                    mean_direction_consistency,
                    4,
                ),

                "std_ratio_avg": round(
                    metrics_df["std_ratio"].mean(),
                    4,
                ),
                "std_ratio_std": round(
                    metrics_df["std_ratio"].std(),
                    4,
                ),
                "variance_increase_rate": round(
                    variance_increase_rate,
                    4,
                ),
            })


summary_df = pd.DataFrame(summary_rows)

window_order = {
    "early": 0,
    "late": 1,
    "full": 2,
}

summary_df["_window_order"] = (
    summary_df["window"].map(window_order)
)

summary_df = (
    summary_df
    .sort_values(
        by=[
            "fault",
            "sensor",
            "_window_order",
        ]
    )
    .drop(columns="_window_order")
    .reset_index(drop=True)
)

output_path = os.path.join(
    os.path.dirname(__file__),
    "fault_multi_run_summary.csv",
)

summary_df.to_csv(
    output_path,
    index=False,
)

print("\n=== Multi-Run Descriptive Summary ===")
print(summary_df.to_string(index=False))
print(f"\nRows generated: {len(summary_df)}")
print(f"Saved: {output_path}")