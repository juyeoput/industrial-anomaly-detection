# TEP Fault Scenario Document — Selected Faults v5
## Prepared by: Yoonseo (Chemical Engineering, University at Buffalo)
## For: Juyeop (ML Model Development)

**Scope note**: This document covers 10 of the 20 TEP faults, based on EDA
across simulationRun 1 (graphical + composition analysis) and 10 sampled runs
(process-variable statistical validation). v3 was single-run graphical EDA.
v4 added multi-run consistency checks and Welch's t-test for process variables.
v5 adds composition sensor verification for Fault 2, closing the last major
gap flagged since v3. Faults not covered: 3, 5, 9, 10, 15, 16, 17, 18, 19, 20.

---

## 1. Process Overview

The Tennessee Eastman Process (TEP) is a benchmark chemical process simulation
developed by Eastman Chemical Company. It is widely used for fault detection research.

### Five Operating Units
- **Reactor**: Exothermic reactions occur here. Temperature and pressure are tightly controlled.
- **Condenser**: Cools reactor overhead vapor before entering the separator.
- **Vapor-Liquid Separator**: Separates gas (recycle) from liquid (to stripper).
- **Recycle Compressor**: Compresses gas from separator back to reactor.
- **Product Stripper**: Purifies liquid product by stripping light components with steam.

### Chemical Components
- **A, C**: Gaseous reactants
- **D, E**: Liquid reactants
- **B**: Inert gaseous component (accumulates, removed via purge)
- **G, H**: Liquid products (desired)
- **F**: Liquid byproduct

### Simplified Reaction Overview
Note: this is a simplified overview for team reference, not a rigorous kinetic model.
- A(g) + C(g) + D(liq) -> G(liq)  [product]
- A(g) + C(g) + E(liq) -> H(liq)  [product]
- A(g) + E(liq) -> F(liq)  [byproduct]

### Dataset Structure
- Sampling interval: 3 minutes
- FaultFree Training: 500 runs x 500 samples = 250,000 rows (normal only)
- FaultFree Testing: 500 runs x 960 samples = 480,000 rows (normal only)
- Faulty Testing: 20 faults x 500 runs x 960 samples = 9,600,000 rows
- Fault introduction time: 8 hours = sample 160 (testing set), sample 20 (training set)
- Total variables: 55 columns (3 metadata + 41 XMEAS + 11 XMV)

---

## 2. Complete Variable Definitions

### Metadata Columns

| Column | Description |
|--------|-------------|
| faultNumber | 0 = normal, 1-20 = fault type |
| simulationRun | Random seed run number (1-500) |
| sample | Time step index (1-500 training, 1-960 testing) |

### Measured Variables — Process (xmeas_1 ~ xmeas_22)

| Variable | Name | Unit | Normal Mean | Normal Min | Normal Max | Physical Meaning |
|----------|------|------|-------------|------------|------------|-----------------|
| xmeas_1 | A Feed Flow | kscmh | 0.251 | 0.123 | 0.390 | A component flow rate into reactor. |
| xmeas_2 | D Feed Flow | kg/hr | 3663.8 | 3503.3 | 3824.7 | Liquid reactant D flow into reactor. |
| xmeas_3 | E Feed Flow | kg/hr | 4508.9 | 4338.2 | 4689.2 | Liquid reactant E flow into reactor. |
| xmeas_4 | A/C Feed Flow | kscmh | 9.347 | 8.936 | 9.749 | Mixed A and C stream total flow. Sensitive to feed ratio changes. |
| xmeas_5 | Recycle Flow | kscmh | 26.902 | 26.018 | 27.822 | Gas recycle loop flow rate from compressor. |
| xmeas_6 | Reactor Feed Rate | kscmh | 42.338 | 41.441 | 43.250 | Total volumetric flow entering reactor. |
| xmeas_7 | Reactor Pressure | kPa | 2705.0 | 2667.8 | 2736.9 | Reactor operating pressure. |
| xmeas_8 | Reactor Level | % | 75.0 | 72.441 | 77.386 | Liquid level inside reactor vessel. |
| xmeas_9 | Reactor Temperature | deg C | 120.40 | 120.31 | 120.49 | Core reaction state indicator. Very narrow normal range (about 0.18 deg C). |
| xmeas_10 | Purge Rate | kscmh | 0.337 | 0.278 | 0.392 | Flow rate of purge stream removing inert B component. |
| xmeas_11 | Separator Temperature | deg C | 80.107 | 79.05 | 81.217 | Vapor-liquid separator operating temperature. |
| xmeas_12 | Separator Level | % | 50.0 | 45.411 | 54.258 | Liquid level in separator. |
| xmeas_13 | Separator Pressure | kPa | 2633.7 | 2594.7 | 2666.7 | Separator operating pressure. |
| xmeas_14 | Separator Underflow | m3/hr | 25.161 | 20.707 | 29.961 | Liquid flow from separator to stripper. |
| xmeas_15 | Stripper Level | % | 50.0 | 45.601 | 54.245 | Liquid level in product stripper. |
| xmeas_16 | Stripper Pressure | kPa | 3102.2 | 3071.5 | 3132.5 | Stripper column operating pressure. |
| xmeas_17 | Stripper Underflow | m3/hr | 22.947 | 20.265 | 26.045 | Final product flow rate out of stripper. |
| xmeas_18 | Stripper Temperature | deg C | 65.803 | 63.845 | 67.652 | Stripper bottom temperature. |
| xmeas_19 | Stripper Steam Flow | kg/hr | 232.215 | 184.61 | 278.28 | Steam flow supplying heat to stripper reboiler. |
| xmeas_20 | Compressor Work | kW | 341.418 | 333.51 | 349.33 | Energy consumption of recycle compressor. |
| xmeas_21 | Reactor CW Outlet Temp | deg C | 94.601 | 93.979 | 95.227 | Reactor cooling water outlet temperature. |
| xmeas_22 | Separator CW Outlet Temp | deg C | 77.294 | 76.005 | 78.554 | Separator cooling water outlet temperature. |

### Measured Variables — Composition Analyzers (xmeas_23 ~ xmeas_41)

| Variable | Name | Unit | Stream | Status as of v5 |
|----------|------|------|--------|------------------|
| xmeas_23 | Reactor Feed A Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_24 | Reactor Feed B Composition | mol% | Reactor inlet | **VERIFIED (v5)** — responds to Fault 2, std_ratio 2.42x |
| xmeas_25 | Reactor Feed C Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_26 | Reactor Feed D Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_27 | Reactor Feed E Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_28 | Reactor Feed F Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_29 | Purge A Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_30 | Purge B Composition | mol% | Purge stream | **VERIFIED (v5)** — strongest signal for Fault 2, std_ratio 3.67x |
| xmeas_31 | Purge C Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_32 | Purge D Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_33 | Purge E Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_34 | Purge F Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_35 | Purge G Composition | mol% | Purge stream | **VERIFIED (v5)** — largest mean shift for Fault 2, 4.14% |
| xmeas_36 | Purge H Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_37 | Product D Composition | mol% | Product stream | Not yet plotted or tested |
| xmeas_38 | Product E Composition | mol% | Product stream | Not yet plotted or tested |
| xmeas_39 | Product F Composition | mol% | Product stream | Not yet plotted or tested |
| xmeas_40 | Product G Composition | mol% | Product stream | **VERIFIED (v5)** — confirmed NOT significantly affected by Fault 2, 0.05% change |
| xmeas_41 | Product H Composition | mol% | Product stream | Not yet plotted or tested |

### Manipulated Variables — Control Valves (xmv_1 ~ xmv_11)

| Variable | Name | Unit | Normal Mean | Normal Min | Normal Max | Control Purpose |
|----------|------|------|-------------|------------|------------|----------------|
| xmv_1 | D Feed Valve | %open | 63.047 | 60.401 | 65.741 | Controls D liquid feed flow rate |
| xmv_2 | E Feed Valve | %open | 53.974 | 51.818 | 56.103 | Controls E liquid feed flow rate |
| xmv_3 | A Feed Valve | %open | 24.644 | 11.985 | 38.449 | Controls A gas feed flow rate |
| xmv_4 | A/C Feed Valve | %open | 61.296 | 55.762 | 66.494 | Controls A/C mixed gas feed |
| xmv_5 | Compressor Recycle Valve | %open | 22.212 | 19.847 | 24.654 | Controls recycle loop pressure |
| xmv_6 | Purge Valve | %open | 40.058 | 32.596 | 46.758 | Controls inert B removal rate |
| xmv_7 | Separator Underflow Valve | %open | 38.099 | 24.594 | 50.631 | Controls separator liquid level |
| xmv_8 | Stripper Level Valve | %open | 46.534 | 36.354 | 56.357 | Controls stripper liquid level |
| xmv_9 | Stripper Steam Valve | %open | 47.975 | 35.587 | 60.160 | Controls heat input to stripper |
| xmv_10 | Reactor CW Valve | %open | 41.103 | 38.557 | 43.601 | Controls reactor cooling water flow |
| xmv_11 | Separator CW Valve | %open | 18.122 | 10.856 | 24.524 | Controls separator cooling water flow |

---

## 3. Statistical Validation Summary

### A. Process-variable validation (from v4, unchanged)

Two validation steps beyond v3's single-run graphical EDA: (1) multi-run
consistency check across 10 simulation runs (1, 25, 50, 100, 150, 200, 250,
300, 400, 500), and (2) Welch's t-test (mean-based, run 1, alpha=0.05).

| Fault | Type | t-test result (mean-based) | Multi-run consistency | Conclusion |
|-------|------|------------------------------|------------------------|------------|
| 1 | A/C feed ratio | Significant (p<0.001) on xmeas_1, xmeas_4, xmeas_7 | Stable | Mean-shift fault — reliably detectable via mean threshold |
| 2 | B composition | Significant (p<0.001) on xmeas_1, xmeas_4, xmeas_7 in process variables | Stable | Detectable via process variables; composition sensors now also verified (see 3B) |
| 4 | Reactor CW inlet temp (step) | Significant (p<0.001) on xmv_10 only | Stable | Must use xmv_10, not reactor temperature |
| 6 | A feed loss | Significant (p<0.001) on all four key sensors | Very stable | Clearest, most reliably detectable fault |
| 7 | C feed pressure disturbance | NOT significant over full window | Stable | Transient, needs short time-window detection |
| 8 | A/B/C composition change | Significant on xmeas_1, xmeas_4; NOT on xmeas_7, xmeas_9 | UNSTABLE on xmeas_1 mean-shift across runs | Use variance-based features instead of xmeas_1 mean-shift |
| 11 | Reactor CW inlet temp (random) | NOT significant on any sensor | Stable | Pure oscillation fault, variance-based detection required |
| 12 | Separator cooling disturbance | Significant only on xmeas_11 (p<0.05) | Moderate variability in magnitude | Direction confirmed, magnitude approximate |
| 13 | Reaction kinetics change | Significant only on xmeas_7 (p<0.01) | Moderate variability | Variance-based feature preferred over mean alone |
| 14 | Reactor CW valve stuck | NOT significant on any sensor | Very stable, very high std_ratio | Textbook oscillation-type fault, variance is the only reliable signal |

### Key modeling implication (from v4)

Faults split into two detection regimes. Mean-shift faults (detectable by
simple threshold): 1, 2, 6, and partially 8, 13. Variance/oscillation faults
(need rolling std or similar): 4, 7, 11, 14, and partially 12. Recommend the
model include both mean-based and variance-based features per sensor.

### B. NEW in v5 — Fault 2 Composition Sensor Verification

v3 and v4 flagged Fault 2 as the one fault where the expected primary
indicator (xmeas_30, Purge B Composition) had not been directly tested. This
gap is now closed. Four composition sensors were plotted and compared (normal
vs Fault 2, simulationRun 1, post-fault window sample >= 160):

| Sensor | Normal mean | Fault mean | Pct change (mean) | Std ratio | Interpretation |
|--------|-------------|------------|--------------------|-----------|----------------|
| xmeas_24 (Reactor Feed B) | 8.8965 | 9.0397 | 1.61% | 2.42x | B composition disturbed at reactor inlet |
| xmeas_30 (Purge B) | 13.8233 | 13.9722 | 1.08% | **3.67x** | Strongest signal — confirms B accumulates in purge stream, as hypothesized since v3 |
| xmeas_35 (Purge G) | 4.8583 | 5.0595 | 4.14% | 2.14x | Largest mean shift — mild product loss to purge, consistent with reduced reactor efficiency |
| xmeas_40 (Product G) | 53.7567 | 53.7840 | 0.05% | 1.03x | Essentially unaffected — final product purity not yet degraded at this stage |

**Conclusion**: Composition sensors, especially xmeas_30, provide a
substantially clearer signal for Fault 2 than the process variables used in
v3/v4 (xmeas_4, xmeas_7), which showed only a weak, marginally-significant
shift. This confirms the hypothesis carried since v3: Fault 2 is fundamentally
a composition-domain fault, and detection models should prioritize xmeas_30
(and secondarily xmeas_24, xmeas_35) over reactor pressure/flow alone. The
fact that xmeas_40 (final product purity) is NOT yet affected suggests Fault 2
could be caught upstream before it reaches product quality — an early-warning
opportunity.

---

## 4. Fault Scenario Mapping Table

| Fault | Type | Category | Key Sensors | Pattern Summary | Detection Regime | Severity |
|-------|------|----------|-------------|-----------------|-------------------|----------|
| 1 | A/C feed ratio disturbance | Feed | xmeas_1, xmeas_4, xmeas_7 | xmeas_1 rises ~200% above normal, t-test confirmed, stable across runs | Mean-shift | High |
| 2 | B composition change | Feed | **xmeas_30 (primary, v5)**, xmeas_24, xmeas_35, xmeas_4, xmeas_7 | Composition sensors show clearer signal than process variables; xmeas_30 std_ratio 3.67x | Composition-based (variance) | Medium |
| 4 | Reactor CW inlet temp (step) | Cooling | xmv_10 (confirmed primary) | xmv_10 opens ~9% wider, statistically significant; reactor temp NOT significant | Mean-shift (valve only) | Medium |
| 6 | A feed loss | Feed | xmeas_1, xmeas_7 | xmeas_1 drops ~100%, most reliable fault in dataset | Mean-shift | Critical |
| 7 | C feed pressure disturbance | Feed | xmeas_4, xmeas_7 | Transient, NOT significant over full post-fault window | Transient / short-window detection | Medium |
| 8 | A/B/C composition change | Feed | xmeas_1 (unstable), xmeas_4 (stable) | Mixed: xmeas_4 mean-shift reliable, xmeas_1 unreliable across runs | Mixed (prefer variance) | High |
| 11 | Reactor CW inlet temp (random) | Cooling | xmeas_9, xmv_10 | NOT significant by mean; std_ratio 4-6x, stable across runs | Variance/oscillation | Medium |
| 12 | Separator cooling disturbance | Cooling | xmeas_11, xmeas_22, xmeas_13 | Mean barely significant; variance elevated but magnitude varies by run | Variance/oscillation (approximate) | High |
| 13 | Reaction kinetics change | Reaction | xmeas_7 | Mean weakly significant; variance clearly elevated (~10x) | Mixed, variance preferred | Medium |
| 14 | Reactor CW valve stuck | Cooling | xmeas_9, xmeas_21 | NOT significant by mean; variance ~13x and ~11x, very stable | Variance/oscillation (textbook case) | High |

---

## 5. Detailed Fault Descriptions

### Fault 1 — A/C Feed Ratio Disturbance
- **Root cause**: Disturbance in A component feed ratio relative to C
- **First signal**: xmeas_1 rises well above its normal range (t=-147.8, p~0, stable across runs)
- **Secondary signals**: xmeas_4 drops, xmeas_7 fluctuates
- **Severity**: High — disrupts reaction stoichiometry
- **Recommended action**: Check A feed valve (xmv_3), inspect A/C feed ratio controller

### Fault 2 — B Component Composition Change (v5: composition-verified)
- **Root cause**: B (inert) component concentration in feed changes
- **Primary signal (v5)**: xmeas_30 (Purge B Composition) — std_ratio 3.67x, clearest indicator
- **Secondary signals (v5)**: xmeas_24 (Reactor Feed B, std_ratio 2.42x), xmeas_35 (Purge G, largest mean shift 4.14%)
- **Process variables (from v3/v4)**: xmeas_4 slightly elevated, xmeas_7 transiently elevated — statistically significant per v4 t-test but visually subtle
- **Not yet affected**: xmeas_40 (Product G Composition) — final product purity unaffected at observed stage, an early-warning opportunity
- **Temperature response**: Minimal
- **Severity**: Medium — inert buildup could reduce reactor efficiency over time; not yet reaching product quality
- **Recommended action**: Prioritize monitoring xmeas_30 as primary detection signal; check B component supply; consider increasing purge rate (xmv_6)
- **LLM explanation template**: Purge B composition elevated with increased variability, consistent with inert B accumulation. Reactor feed B composition also disturbed. Final product purity not yet affected — early intervention recommended.

### Fault 4 — Reactor Cooling Water Inlet Temperature (Step Change)
- **Root cause**: Cooling water supply temperature increases as a step change
- **Primary signal**: xmv_10 opens wider and stays elevated (t=-147.7, p~0) — clearest and most reliable indicator
- **Important note**: Best detected through xmv_10, not xmeas_9. The controller compensates effectively, so reactor temperature stays close to normal.
- **Severity**: Medium — cooling capacity reduced but currently compensated
- **Recommended action**: Check cooling water supply temperature, inspect heat exchangers

### Fault 6 — A Feed Loss
- **Root cause**: A component feed is lost or blocked
- **First signal**: xmeas_1 drops toward 0 (t=219.8, p~0, most statistically robust fault in the set)
- **Secondary signal**: xmeas_7 rises and does not stabilize
- **Severity**: CRITICAL — most dangerous fault observed
- **Recommended action**: Treat as high priority. Check A feed line and xmv_3. Escalate to safety systems if pressure continues rising.

### Fault 7 — C Feed Pressure Disturbance
- **Root cause**: C component supply pressure fluctuates
- **First signal**: xmeas_4 drops sharply then overshoots; xmeas_7 oscillates sharply
- **Persistence**: Transient — NOT statistically significant over the full post-fault window; signal is concentrated early and fades. Needs short time-window detection.
- **Severity**: Medium
- **Recommended action**: Check C feed pressure regulator, monitor for recurrence

### Fault 8 — A/B/C Composition Simultaneous Change
- **Root cause**: Multiple feed components change composition around the same time
- **First signal**: xmeas_1 and xmeas_4 oscillate in a related pattern
- **Important note**: xmeas_1 mean-shift magnitude is highly inconsistent across runs (std of pct_change = 12.4). Do not rely on xmeas_1 mean-shift; use variance-based features instead. xmeas_4 mean-shift is more stable.
- **Severity**: High — complex multi-variable disturbance
- **Recommended action**: Check feed composition analyzers, inspect feed mixing system

### Fault 11 — Reactor CW Inlet Temperature (Random Variation)
- **Root cause**: Cooling water supply temperature varies irregularly
- **First signal**: xmv_10 oscillates over a wide range; NOT statistically significant by mean
- **Key difference from Fault 4**: Fault 4 is a step (mean shift, stable). Fault 11 is irregular (mean not significant, but variance is elevated and stable across runs).
- **Severity**: Medium
- **Recommended action**: Check cooling water supply for instability, inspect cooling tower controls and pump

### Fault 12 — Separator Cooling System Disturbance
- **Root cause (per TEP documentation)**: Disturbance related to separator cooling water inlet temperature; our EDA observed downstream effects (temperature/pressure oscillation), not the mechanism directly
- **First signal**: xmeas_11 shifts from stable to a wide oscillating range; only sensor with a marginally significant mean shift (p=0.025)
- **Secondary signals**: xmeas_22, xmeas_13 oscillate; magnitude varies moderately across runs
- **Key difference from Fault 14**: Fault 12 affects separator sensors; reactor sensors (xmeas_9, xmeas_21) remain close to normal
- **Severity**: High
- **Recommended action**: Check separator cooling water valve (xmv_11), inspect separator cooling circuit

### Fault 13 — Reaction Kinetics Change
- **Root cause**: Reaction rate constant changes (catalyst degradation or feed impurity effect)
- **First signal**: xmeas_7 oscillates with amplitude that grows over time; only weakly significant by mean (p<0.01), but variance clearly elevated (~10x)
- **Severity**: Medium — gradual degradation rather than acute event
- **Recommended action**: Check catalyst condition and activity, review reactor temperature profile, inspect feed purity

### Fault 14 — Reactor Cooling Water Valve Stuck
- **Root cause**: Reactor cooling water control valve becomes mechanically stuck
- **Key sensors**: xmeas_9 (Reactor Temperature), xmeas_21 (Reactor CW Outlet Temp)
- **Observed pattern**: Both shift from stable narrow ranges to persistent high-frequency oscillation; NOT statistically significant by mean at all, but variance ~13x (xmeas_9) and ~11x (xmeas_21), extremely stable across 10 runs
- **Modeling note**: This is the textbook oscillation-type fault. Mean-based detection will completely miss it — variance/oscillation amplitude is the only reliable signal.
- **Severity**: High
- **Recommended action**: Inspect reactor cooling water valve (xmv_10) for mechanical failure, check valve actuator and positioner

---

## 6. Key Sensor Priority for Model Training

### Tier 1 — Statistically Confirmed, Stable Across Runs

| Sensor | Fault | Evidence |
|--------|-------|----------|
| xmeas_1 | Fault 1, 6 | t-test significant, low run-to-run variance in both faults |
| xmv_10 | Fault 4 | t-test significant (p<0.001), only significant sensor for this fault |
| xmeas_9 (variance, not mean) | Fault 14 | std_ratio ~13x, extremely stable across 10 runs |
| xmeas_21 (variance, not mean) | Fault 14 | std_ratio ~11x, stable across runs |

### Tier 2 — Confirmed, Use Variance Not Mean

| Sensor | Fault | Note |
|--------|-------|------|
| xmeas_9 | Fault 11 | Mean not significant; variance is the only usable signal |
| xmv_10 | Fault 11 | Same as above |
| xmeas_7 | Fault 13 | Mean weakly significant; variance (std_ratio ~10x) more reliable |
| xmeas_11 | Fault 12 | Mean marginally significant; direction confirmed, magnitude varies |

### Tier 3 — Use With Caution

| Sensor | Fault | Issue |
|--------|-------|-------|
| xmeas_1 | Fault 8 | High run-to-run variance in mean-shift magnitude; not reliable as a single feature |
| xmeas_4 | Fault 7 | Signal present only in early post-fault window; full-window statistics miss it |

### Tier 4 — Composition Sensors (UPDATED: Fault 2 now verified)

| Sensor | Fault | Status |
|--------|-------|--------|
| xmeas_30 | Fault 2 | **VERIFIED (v5)** — primary recommended feature, std_ratio 3.67x |
| xmeas_24 | Fault 2 | **VERIFIED (v5)** — secondary feature, std_ratio 2.42x |
| xmeas_35 | Fault 2 | **VERIFIED (v5)** — secondary feature, largest mean shift (4.14%) |
| xmeas_40 | Fault 2 | **VERIFIED (v5)** — confirmed NOT useful (no signal, 0.05% change) |
| xmeas_23 | Fault 1, 8 | Still unverified — lower priority since Fault 1/8 already well-detected via process variables |

---

## 7. Fault Classification Guide

**Mean-based detection works for**: Fault 1, 2 (process variables), 6 reliably; Fault 8 partially (xmeas_4 only)

**Variance-based detection required for**: Fault 4, 7, 11, 14

**Composition-based detection required for**: Fault 2 (xmeas_30 primary — clearer than process variables)

**Mixed / needs both**: Fault 12, 13

### Distinguishing similar faults

**Fault 4 vs Fault 11** — Fault 4: xmv_10 mean shift significant and stable (step). Fault 11: xmv_10 mean not significant (irregular), but variance elevated.

**Fault 12 vs Fault 14** — Fault 12: separator sensors affected, reactor sensors normal. Fault 14: reactor sensors show strong stable variance increase, near-zero mean shift.

**Fault 1 vs Fault 6** — Both strong mean-shift, opposite direction. Fault 1: xmeas_1 rises ~200%. Fault 6: xmeas_1 drops ~100%, most statistically robust fault in the set.

**Fault 7 vs Fault 8** — Fault 7: not significant over full window, signal fades (transient). Fault 8: persistent oscillation, but xmeas_1 mean-shift magnitude inconsistent across runs.

---

## 8. LLM Integration Guide

### Recommended LLM Prompt Structure

```
You are a chemical process assistant for the Tennessee Eastman Process.
An anomaly has been detected. Based on the sensor readings and reference
document below, identify the most likely fault and provide recommendations.
Specify whether the signal is a mean shift, a variance/oscillation increase,
or a composition-domain signal.

CURRENT ANOMALY:
- Triggered sensors: [list sensors and deviation from normal]
- Pattern observed: [describe pattern]

FAULT REFERENCE:
[Insert relevant sections from this document]

Respond with:
1. Most likely fault type and confidence level
2. Root cause explanation in plain language
3. Recommended actions
4. Severity level (Low/Medium/High/Critical)
```

### Example LLM Output (Fault 2, updated with composition data)

```
ANOMALY DETECTED — Pattern consistent with Fault 2 (B Composition Change)

Triggered sensors:
- xmeas_30 (Purge B Composition): variance approximately 3.7x normal
- xmeas_24 (Reactor Feed B Composition): variance approximately 2.4x normal
- xmeas_4, xmeas_7 (process variables): weak but statistically significant shift

Final product purity (xmeas_40) is not yet affected — this is an early-stage
detection opportunity.

Root cause: B (inert) component concentration in feed has increased,
accumulating in the purge stream.

Recommended actions:
1. Check B component supply and feed composition analyzer
2. Consider increasing purge rate (xmv_6)
3. Monitor xmeas_30 trend to catch further buildup early

Severity: MEDIUM
```

---

## 9. Model Training Notes for ML Engineer

### Data Split Recommendation
- Train primarily on normal data (FaultFree_Training) for the anomaly detector.
- Use faulty data for validation, threshold tuning, and fault classification.
- Fault introduced at sample 160 (testing set), sample 20 (training set).

### CRITICAL Preprocessing Note
Do not rely on mean-based features alone. t-test validation shows Faults 4, 7,
11, and 14 are NOT statistically detectable via mean shift; these need
variance-type features (rolling standard deviation or oscillation amplitude).
Recommend computing both rolling mean and rolling std for every sensor used
as a model feature.

### Fault 2 feature recommendation (NEW in v5)
Include xmeas_30 (and optionally xmeas_24, xmeas_35) as model features for
Fault 2 detection. Process variables (xmeas_4, xmeas_7) remain statistically
significant per v4 but should be treated as secondary, not primary, signals.

### Other Preprocessing Notes
- xmeas_9 normal range is extremely narrow (about 0.18 deg C). Normalize carefully.
- xmeas_1 mean-shift is reliable for Fault 1 and 6, but NOT for Fault 8 (high run-to-run variance).
- Remaining composition sensors (xmeas_23, 25-29, 31-34, 36-39, 41) are still unvalidated.
- xmv variables should be included as features; xmv_10 is the primary signal for Fault 4.

### Recommended Model Approach
- Stage 1: Anomaly detection using both mean and variance features per sensor — Isolation Forest or Autoencoder
- Stage 2: Fault classification — Random Forest or LSTM, using Section 7's detection regime split to guide feature selection
- Stage 3: LLM explanation generation, referencing Section 3 for statistical/composition confidence language

### Validation Methodology Note
Process-variable findings are based on simulationRun 1 (t-test) plus 10
sampled runs for consistency checking. Composition sensor findings (Section 3B,
Fault 2) are based on simulationRun 1 only and have not yet been
cross-validated across multiple runs. This is a recommended next step.