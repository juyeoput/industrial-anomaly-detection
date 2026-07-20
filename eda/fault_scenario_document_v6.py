"""Refresh the quantitative tables in fault_scenario_document_v6.md.

The reviewed narrative stays in the Markdown template. This script reads the
latest run-level CSV outputs and replaces only the two auto-generated evidence
tables, preventing copied numbers from drifting away from the analysis.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DOCUMENT = SCRIPT_DIR / "fault_scenario_document_v6.md"
DEFAULT_PROCESS_CSV = SCRIPT_DIR / "fault_run_level_validation.csv"
DEFAULT_COMPOSITION_CSV = (
    SCRIPT_DIR / "fault2_composition_multi_run_summary.csv"
)

PROCESS_START = "<!-- AUTO:PROCESS_SUMMARY START -->"
PROCESS_END = "<!-- AUTO:PROCESS_SUMMARY END -->"
COMPOSITION_START = "<!-- AUTO:COMPOSITION_SUMMARY START -->"
COMPOSITION_END = "<!-- AUTO:COMPOSITION_SUMMARY END -->"

PROCESS_COLUMNS = {
    "fault",
    "sensor",
    "window",
    "n_runs",
    "pct_change_avg",
    "normalized_mean_effect_avg",
    "std_ratio_avg",
}
COMPOSITION_COLUMNS = {
    "fault",
    "sensor",
    "window",
    "n_runs",
    "pct_change_mean_avg",
    "std_ratio_avg",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh the auto-generated tables in the TEP v6 document."
    )
    parser.add_argument(
        "--document",
        type=Path,
        default=DEFAULT_DOCUMENT,
        help="V6 Markdown template/output path.",
    )
    parser.add_argument(
        "--process-csv",
        type=Path,
        default=DEFAULT_PROCESS_CSV,
        help="50-run process validation CSV.",
    )
    parser.add_argument(
        "--composition-csv",
        type=Path,
        default=DEFAULT_COMPOSITION_CSV,
        help="Fault 2 composition multi-run summary CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Defaults to overwriting --document.",
    )
    return parser.parse_args()


def require_columns(
    dataframe: pd.DataFrame,
    required: set[str],
    source: Path,
) -> None:
    missing = required.difference(dataframe.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{source} is missing columns: {missing_text}")


def get_row(
    dataframe: pd.DataFrame,
    fault: int,
    sensor: str,
    window: str,
) -> pd.Series:
    rows = dataframe[
        (dataframe["fault"] == fault)
        & (dataframe["sensor"] == sensor)
        & (dataframe["window"] == window)
    ]
    if len(rows) != 1:
        raise ValueError(
            "Expected exactly one row for "
            f"fault={fault}, sensor={sensor}, window={window}; "
            f"found {len(rows)}."
        )
    return rows.iloc[0]


def signed(value: float, digits: int = 2) -> str:
    return f"{value:+.{digits}f}"


def render_process_table(dataframe: pd.DataFrame) -> str:
    row = lambda fault, sensor, window="full": get_row(  # noqa: E731
        dataframe, fault, sensor, window
    )

    f1_x1 = row(1, "xmeas_1")
    f1_x4 = row(1, "xmeas_4")
    f2_x1 = row(2, "xmeas_1")
    f2_x4 = row(2, "xmeas_4")
    f4_xmv10 = row(4, "xmv_10")
    f6_x1 = row(6, "xmeas_1")
    f6_x7 = row(6, "xmeas_7")
    f7_early = row(7, "xmeas_4", "early")
    f7_late = row(7, "xmeas_4", "late")
    f8_x1 = row(8, "xmeas_1")
    f8_x4 = row(8, "xmeas_4")
    f8_x7 = row(8, "xmeas_7")
    f11_x9 = row(11, "xmeas_9")
    f11_xmv10 = row(11, "xmv_10")
    f12_x11 = row(12, "xmeas_11")
    f12_x13 = row(12, "xmeas_13")
    f12_x22 = row(12, "xmeas_22")
    f13_x7 = row(13, "xmeas_7")
    f13_x6 = row(13, "xmeas_6")
    f14_x9 = row(14, "xmeas_9")
    f14_x21 = row(14, "xmeas_21")

    lines = [
        PROCESS_START,
        "| Fault | Main observed evidence | v6 interpretation |",
        "|-------|------------------------|-------------------|",
        (
            "| 1 | xmeas_1 persistent mean "
            f"{signed(f1_x1['pct_change_avg'], 1)}%; xmeas_4 "
            f"{signed(f1_x4['pct_change_avg'], 1)}% | "
            "Strong persistent mean-shift pattern |"
        ),
        (
            "| 2 | xmeas_1 "
            f"{signed(f2_x1['pct_change_avg'], 1)}%; xmeas_4 "
            f"{signed(f2_x4['pct_change_avg'], 2)}%; xmeas_7 response fades | "
            "Process variables respond, but composition features improve diagnosis |"
        ),
        (
            "| 4 | xmv_10 persistent mean "
            f"{signed(f4_xmv10['pct_change_avg'], 2)}%, normalized effect "
            f"{f4_xmv10['normalized_mean_effect_avg']:.1f}; reactor temperature "
            "and pressure remain near normal | Compensating controller action "
            "creates a clear valve mean shift |"
        ),
        (
            "| 6 | xmeas_1 "
            f"{signed(f6_x1['pct_change_avg'], 1)}%; xmeas_7 "
            f"{signed(f6_x7['pct_change_avg'], 1)}%; several late signals become "
            "fixed or zero-variance | Strong feed-loss/saturated-state pattern; "
            "fixed values are abnormal, not recovery |"
        ),
        (
            "| 7 | xmeas_4 early mean "
            f"{signed(f7_early['pct_change_avg'], 2)}% with std ratio "
            f"{f7_early['std_ratio_avg']:.1f}; late mean approaches zero but "
            f"std ratio remains {f7_late['std_ratio_avg']:.2f} | "
            "Early transient plus residual variability |"
        ),
        (
            "| 8 | Mean direction varies by run; persistent std ratios are "
            f"{f8_x1['std_ratio_avg']:.1f} for xmeas_1, "
            f"{f8_x4['std_ratio_avg']:.1f} for xmeas_4, and "
            f"{f8_x7['std_ratio_avg']:.1f} for xmeas_7 | "
            "Variance-dominant multivariable pattern |"
        ),
        (
            "| 11 | xmeas_9 std ratio "
            f"{f11_x9['std_ratio_avg']:.1f} and xmv_10 "
            f"{f11_xmv10['std_ratio_avg']:.1f}; mean effects are small or "
            "inconsistent | Variance/irregular oscillation pattern |"
        ),
        (
            "| 12 | xmeas_11, xmeas_13, and xmeas_22 std ratios are "
            f"{f12_x11['std_ratio_avg']:.1f}, {f12_x13['std_ratio_avg']:.1f}, "
            f"and {f12_x22['std_ratio_avg']:.1f} | Separator-side mixed response, "
            "dominated by variability |"
        ),
        (
            "| 13 | xmeas_7 std ratio "
            f"{f13_x7['std_ratio_avg']:.1f} with normalized late/full mean effect "
            f"{f13_x7['normalized_mean_effect_avg']:.1f}; xmeas_6 std ratio "
            f"{f13_x6['std_ratio_avg']:.2f} | Mixed pressure response, variance "
            "dominant |"
        ),
        (
            "| 14 | xmeas_9 std ratio "
            f"{f14_x9['std_ratio_avg']:.1f} and xmeas_21 "
            f"{f14_x21['std_ratio_avg']:.1f}; mean effects are practically zero | "
            "Persistent reactor cooling-side oscillation pattern |"
        ),
        PROCESS_END,
    ]
    return "\n".join(lines)


def render_composition_table(dataframe: pd.DataFrame) -> str:
    names = {
        "xmeas_24": "Reactor Feed B",
        "xmeas_30": "Purge B",
        "xmeas_35": "Purge G",
        "xmeas_40": "Product G",
    }
    interpretations = {
        "xmeas_24": "Strong initial composition response that largely fades",
        "xmeas_30": "Strongest early variability response among the four tested sensors",
        "xmeas_35": "Persistent late mean increase; useful complement to xmeas_30",
        "xmeas_40": "No material difference observed in the sampled runs",
    }

    lines = [
        COMPOSITION_START,
        "| Sensor | Early window | Late window | Interpretation |",
        "|--------|--------------|-------------|----------------|",
    ]
    for sensor, name in names.items():
        early = get_row(dataframe, 2, sensor, "early")
        late = get_row(dataframe, 2, sensor, "late")
        lines.append(
            f"| {sensor}, {name} | "
            f"Mean {signed(early['pct_change_mean_avg'])}%; "
            f"std ratio {early['std_ratio_avg']:.2f} | "
            f"Mean {signed(late['pct_change_mean_avg'])}%; "
            f"std ratio {late['std_ratio_avg']:.2f} | "
            f"{interpretations[sensor]} |"
        )
    lines.append(COMPOSITION_END)
    return "\n".join(lines)


def replace_block(
    document: str,
    start_marker: str,
    end_marker: str,
    replacement: str,
) -> str:
    if document.count(start_marker) != 1 or document.count(end_marker) != 1:
        raise ValueError(
            f"Document must contain one {start_marker!r} and one {end_marker!r}."
        )
    start = document.index(start_marker)
    end = document.index(end_marker, start) + len(end_marker)
    return document[:start] + replacement + document[end:]


def main() -> None:
    args = parse_args()
    output_path = args.output or args.document

    process_df = pd.read_csv(args.process_csv)
    composition_df = pd.read_csv(args.composition_csv)
    require_columns(process_df, PROCESS_COLUMNS, args.process_csv)
    require_columns(composition_df, COMPOSITION_COLUMNS, args.composition_csv)

    if process_df["n_runs"].min() < 50:
        raise ValueError("Process validation must contain at least 50 runs per row.")
    if composition_df["n_runs"].min() < 10:
        raise ValueError("Composition validation must contain at least 10 runs per row.")

    document = args.document.read_text(encoding="utf-8")
    document = replace_block(
        document,
        PROCESS_START,
        PROCESS_END,
        render_process_table(process_df),
    )
    document = replace_block(
        document,
        COMPOSITION_START,
        COMPOSITION_END,
        render_composition_table(composition_df),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
