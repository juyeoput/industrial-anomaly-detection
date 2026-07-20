import os

import numpy as np
import pandas as pd
from scipy import stats

from config import FAULT_CONFIGS
from plot_fault import load_data


print("Loading data...")
normal, faulty = load_data()

# 50 independent simulation runs sampled across runs 1-500
SAMPLE_RUNS = list(range(1, 501, 10))

WINDOWS = {
    "early": (160, 260),
    "late": (300, 960),
    "full": (160, 960),
}

MIN_STD_RATIO = 1e-12


def safe_ttest_1samp(values):
    """Run a one-sample t-test while handling constant arrays."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if len(values) < 2:
        return np.nan

    if np.allclose(values, 0):
        return 1.0

    # A constant non-zero effect is perfectly consistent across runs.
    if np.isclose(values.std(ddof=1), 0):
        return 0.0

    result = stats.ttest_1samp(
        values,
        popmean=0,
        nan_policy="omit",
    )

    return float(result.pvalue)


def safe_wilcoxon(values):
    """Run a Wilcoxon signed-rank test while handling zero arrays."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if len(values) < 2:
        return np.nan

    if np.allclose(values, 0):
        return 1.0

    try:
        result = stats.wilcoxon(
            values,
            zero_method="wilcox",
            alternative="two-sided",
        )
        return float(result.pvalue)
    except ValueError:
        return np.nan


# Normal data can be indexed once and reused for every fault.
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

                # A valid normal standard deviation is required for
                # normalized effects and standard-deviation ratios.
                if (
                    not np.isfinite(normal_std)
                    or normal_std <= 0
                ):
                    continue

                # A zero fault standard deviation is valid. It may
                # indicate saturation or a constant post-fault state.
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

                normalized_mean_difference = (
                    mean_difference / normal_std
                )

                std_ratio = fault_std / normal_std

                # log(0) is undefined, so zero ratios are clipped only
                # for the variance statistical test.
                safe_std_ratio = max(
                    std_ratio,
                    MIN_STD_RATIO,
                )
                log_std_ratio = np.log(
                    safe_std_ratio
                )

                run_metrics.append({
                    "run": run,
                    "mean_difference": mean_difference,
                    "pct_change": pct_change,
                    "normalized_mean_difference":
                        normalized_mean_difference,
                    "std_ratio": std_ratio,
                    "log_std_ratio": log_std_ratio,
                })

            if not run_metrics:
                continue

            metrics_df = pd.DataFrame(run_metrics)

            mean_differences = metrics_df[
                "mean_difference"
            ].to_numpy()

            log_std_ratios = metrics_df[
                "log_std_ratio"
            ].to_numpy()

            mean_t_pvalue = safe_ttest_1samp(
                mean_differences
            )
            mean_wilcoxon_pvalue = safe_wilcoxon(
                mean_differences
            )

            variance_t_pvalue = safe_ttest_1samp(
                log_std_ratios
            )
            variance_wilcoxon_pvalue = safe_wilcoxon(
                log_std_ratios
            )

            positive_rate = (
                metrics_df["mean_difference"] > 0
            ).mean()

            negative_rate = (
                metrics_df["mean_difference"] < 0
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

            variance_decrease_rate = (
                metrics_df["std_ratio"] < 1
            ).mean()

            summary_rows.append({
                "fault": fault_number,
                "sensor": sensor,
                "window": window_name,
                "sample_range": f"{start}-{end}",
                "n_runs": len(metrics_df),

                "pct_change_avg": round(
                    metrics_df["pct_change"].mean(),
                    4,
                ),
                "pct_change_std": round(
                    metrics_df["pct_change"].std(),
                    4,
                ),
                "pct_change_abs_avg": round(
                    metrics_df["pct_change"]
                    .abs()
                    .mean(),
                    4,
                ),

                "normalized_mean_effect_avg": round(
                    metrics_df[
                        "normalized_mean_difference"
                    ].mean(),
                    4,
                ),

                "mean_direction": mean_direction,
                "mean_direction_consistency": round(
                    mean_direction_consistency,
                    4,
                ),

                # Store raw p-values so very small values are not
                # incorrectly displayed as exactly 0.0.
                "mean_t_pvalue": mean_t_pvalue,
                "mean_wilcoxon_pvalue":
                    mean_wilcoxon_pvalue,

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
                "variance_decrease_rate": round(
                    variance_decrease_rate,
                    4,
                ),

                "variance_t_pvalue":
                    variance_t_pvalue,
                "variance_wilcoxon_pvalue":
                    variance_wilcoxon_pvalue,
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
    "fault_run_level_validation.csv",
)

summary_df.to_csv(
    output_path,
    index=False,
)

print("\n=== Run-Level Validation Summary ===")
print(summary_df.to_string(index=False))
print(f"\nRows generated: {len(summary_df)}")
print(f"Saved: {output_path}")