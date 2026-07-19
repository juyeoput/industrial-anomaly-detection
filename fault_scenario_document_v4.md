# TEP Fault Scenario Document — Selected Faults v4
## Prepared by: Yoonseo (Chemical Engineering, University at Buffalo)
## For: Juyeop (ML Model Development)

**Scope note**: This document covers 10 of the 20 TEP faults. v3 was based on
single-run EDA (simulationRun 1). v4 adds statistical validation across 10
simulation runs (1, 25, 50, 100, 150, 200, 250, 300, 400, 500) and Welch's
t-test results, replacing single-run observation with cross-validated findings
where possible. Faults not covered: 3, 5, 9, 10, 15, 16, 17, 18, 19, 20.

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
- v3 EDA was performed on simulationRun == 1 only. v4 adds validation across 10 runs.

---

## 2. Complete Variable Definitions

(Unchanged from v3 — see Section 2 content below)

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
| xmeas_4 | A/C Feed Flow | kscmh | 9.347 | 8.936 | 9.749 | Mixed A and C stream total flow. |
| xmeas_5 | Recycle Flow | kscmh | 26.902 | 26.018 | 27.822 | Gas recycle loop flow rate. |
| xmeas_6 | Reactor Feed Rate | kscmh | 42.338 | 41.441 | 43.250 | Total volumetric flow entering reactor. |
| xmeas_7 | Reactor Pressure | kPa | 2705.0 | 2667.8 | 2736.9 | Reactor operating pressure. |
| xmeas_8 | Reactor Level | % | 75.0 | 72.441 | 77.386 | Liquid level inside reactor vessel. |
| xmeas_9 | Reactor Temperature | deg C | 120.40 | 120.31 | 120.49 | Core reaction state indicator. Very narrow normal range (about 0.18 deg C). |
| xmeas_10 | Purge Rate | kscmh | 0.337 | 0.278 | 0.392 | Flow rate of purge stream removing inert B. |
| xmeas_11 | Separator Temperature | deg C | 80.107 | 79.05 | 81.217 | Vapor-liquid separator operating temperature. |
| xmeas_12 | Separator Level | % | 50.0 | 45.411 | 54.258 | Liquid level in separator. |
| xmeas_13 | Separator Pressure | kPa | 2633.7 | 2594.7 | 2666.7 | Separator operating pressure. |
| xmeas_14 | Separator Underflow | m3/hr | 25.161 | 20.707 | 29.961 | Liquid flow from separator to stripper. |
| xmeas_15 | Stripper Level | % | 50.0 | 45.601 | 54.245 | Liquid level in product stripper. |
| xmeas_16 | Stripper Pressure | kPa | 3102.2 | 3071.5 | 3132.5 | Stripper column operating pressure. |
| xmeas_17 | Stripper Underflow | m3/hr | 22.947 | 20.265 | 26.045 | Final product flow rate. |
| xmeas_18 | Stripper Temperature | deg C | 65.803 | 63.845 | 67.652 | Stripper bottom temperature. |
| xmeas_19 | Stripper Steam Flow | kg/hr | 232.215 | 184.61 | 278.28 | Steam flow supplying heat to stripper reboiler. |
| xmeas_20 | Compressor Work | kW | 341.418 | 333.51 | 349.33 | Energy consumption of recycle compressor. |
| xmeas_21 | Reactor CW Outlet Temp | deg C | 94.601 | 93.979 | 95.227 | Reactor cooling water outlet temperature. |
| xmeas_22 | Separator CW Outlet Temp | deg C | 77.294 | 76.005 | 78.554 | Separator cooling water outlet temperature. |

### Measured Variables — Composition Analyzers (xmeas_23 ~ xmeas_41)

Still NOT plotted or statistically validated in our EDA. Reference only.
See Section 5, Tier 3 for candidate sensors relevant to Fault 2.

### Manipulated Variables — Control Valves (xmv_1 ~ xmv_11)

| Variable | Name | Unit | Normal Mean | Normal Min | Normal Max | Control Purpose |
|----------|------|------|-------------|------------|------------|----------------|
| xmv_10 | Reactor CW Valve | %open | 41.103 | 38.557 | 43.601 | Controls reactor cooling water flow — statistically confirmed primary indicator for Fault 4 |
| xmv_11 | Separator CW Valve | %open | 18.122 | 10.856 | 24.524 | Controls separator cooling water flow |
(Full xmv_1-11 table unchanged from v3)

---

## 3. Statistical Validation Summary (NEW in v4)

Two validation steps were added beyond v3's single-run graphical EDA:

**A. Multi-run consistency check** — the same mean/variance comparison was
repeated across 10 simulation runs (1, 25, 50, 100, 150, 200, 250, 300, 400, 500)
to see whether v3's single-run observations hold up. Result: most patterns were
confirmed as stable, with one notable exception (Fault 8, see below).

**B. Welch's t-test** — tests whether the fault-period mean is statistically
different from the normal-period mean (run 1, alpha = 0.05). This is a MEAN-based
test only. Key finding: it correctly detects value-shift faults but fails to flag
oscillation-type faults where the mean barely moves but variance increases sharply.
This is an expected and informative result, not a modeling failure — it is direct
evidence that mean-based thresholds alone are insufficient for this system.

| Fault | Type | t-test result (mean-based) | Multi-run consistency | Conclusion |
|-------|------|------------------------------|------------------------|------------|
| 1 | A/C feed ratio | Significant (p<0.001) on xmeas_1, xmeas_4, xmeas_7 | Stable (low run-to-run variance) | Mean-shift fault — safely detectable via mean threshold |
| 2 | B composition | Significant (p<0.001) on xmeas_1, xmeas_4, xmeas_7 in process variables | Stable | Detectable via process variables alone; composition sensors still unverified |
| 4 | Reactor CW inlet temp (step) | Significant (p<0.001) on xmv_10 only; xmeas_9/21/7 NOT significant | Stable | Confirms v3 finding: must use xmv_10, not reactor temperature |
| 6 | A feed loss | Significant (p<0.001) on all four key sensors | Very stable | Clearest, most reliably detectable fault in the set |
| 7 | C feed pressure disturbance | NOT significant on any sensor (mean returns to normal by end of window) | Stable | Confirms v3: transient fault, needs short time-window / early-detection approach, not full-window mean |
| 8 | A/B/C composition change | Significant on xmeas_1 (p<0.01), xmeas_4 (p<0.001); NOT significant on xmeas_7, xmeas_9 | UNSTABLE — xmeas_1 pct-change had very high run-to-run variance (std of 12.4 vs mean of -6.2) | Do not rely on xmeas_1 mean-shift for Fault 8. Use std_ratio / variance-based features instead (more stable across runs) |
| 11 | Reactor CW inlet temp (random) | NOT significant on any sensor | Stable | Confirms v3: pure oscillation fault, undetectable by mean-based methods, requires variance-based detection |
| 12 | Separator cooling disturbance | Significant only on xmeas_11 (p<0.05); others not significant | Moderate variability in std_ratio across runs (esp. xmeas_11, xmeas_13) | Direction of effect confirmed, but exact magnitude varies by run — treat numeric ranges as approximate |
| 13 | Reaction kinetics change | Significant only on xmeas_7 (p<0.01) | Moderate variability in std_ratio | Detectable via reactor pressure, but variance-based feature preferred over mean alone |
| 14 | Reactor CW valve stuck | NOT significant on any sensor | Very stable, very high std_ratio (about 13x on xmeas_9, about 11x on xmeas_21, consistent across runs) | Textbook oscillation-type fault. Mean-based detection will completely miss this. Variance/oscillation amplitude is the only reliable signal. |

### Key modeling implication

Faults split cleanly into two detection regimes:

**Mean-shift faults (detectable by simple threshold on mean value):**
Fault 1, 2, 6, and partially 8 and 13.

**Variance/oscillation faults (mean-based methods will miss these; need rolling
std, rolling variance, or frequency-domain features):**
Fault 4, 7, 11, 14, and partially 12.

Recommendation: the anomaly detection model should include both mean-based and
variance-based features per sensor (e.g., rolling mean AND rolling standard
deviation over a moving window), not mean alone. This single design choice affects
roughly half of the fault types in this document.

---

## 4. Fault Scenario Mapping Table (Updated with statistical backing)

| Fault | Type | Category | Key Sensors | Pattern Summary | Detection Regime | Severity |
|-------|------|----------|-------------|-----------------|-------------------|----------|
| 1 | A/C feed ratio disturbance | Feed | xmeas_1, xmeas_4, xmeas_7 | xmeas_1 rises ~200% above normal (t-test confirmed, stable across runs) | Mean-shift | High |
| 2 | B composition change | Feed | xmeas_4, xmeas_7 | Subtle but statistically confirmed shift in process variables | Mean-shift | Medium |
| 4 | Reactor CW inlet temp (step) | Cooling | xmv_10 (confirmed primary) | xmv_10 opens ~9% wider, statistically significant; reactor temp NOT significant | Mean-shift (valve only) | Medium |
| 6 | A feed loss | Feed | xmeas_1, xmeas_7 | xmeas_1 drops ~100% (t=219.8, p~0), most reliable fault in dataset | Mean-shift | Critical |
| 7 | C feed pressure disturbance | Feed | xmeas_4, xmeas_7 | Transient; NOT significant over full post-fault window; early samples needed | Transient / requires short-window detection | Medium |
| 8 | A/B/C composition change | Feed | xmeas_1 (unstable), xmeas_4 (stable) | Mixed: xmeas_4 mean-shift reliable, xmeas_1 mean-shift unreliable across runs — use variance instead | Mixed (prefer variance) | High |
| 11 | Reactor CW inlet temp (random) | Cooling | xmeas_9, xmv_10 | NOT significant by mean; std_ratio 4-6x, stable across runs | Variance/oscillation | Medium |
| 12 | Separator cooling disturbance | Cooling | xmeas_11, xmeas_22, xmeas_13 | Mean barely significant; variance elevated but magnitude varies by run | Variance/oscillation (approximate magnitude) | High |
| 13 | Reaction kinetics change | Reaction | xmeas_7 | Mean weakly significant; variance clearly elevated (~10x), amplitude grows over time | Mixed, variance preferred | Medium |
| 14 | Reactor CW valve stuck | Cooling | xmeas_9, xmeas_21 | NOT significant by mean at all; variance ~13x and ~11x, very stable across runs | Variance/oscillation (textbook case) | High |

---

## 5. Key Sensor Priority for Model Training (Updated)

### Tier 1 — Statistically Confirmed, Stable Across Runs

| Sensor | Fault | Evidence |
|--------|-------|----------|
| xmeas_1 | Fault 1, 6 | t-test significant, low run-to-run variance in both faults |
| xmv_10 | Fault 4 | t-test significant (p<0.001), only significant sensor for this fault |
| xmeas_9 (variance, not mean) | Fault 14 | std_ratio ~13x, extremely stable across 10 runs (std of ratio = 0.30) |
| xmeas_21 (variance, not mean) | Fault 14 | std_ratio ~11x, stable across runs |

### Tier 2 — Confirmed but Use Variance, Not Mean

| Sensor | Fault | Note |
|--------|-------|------|
| xmeas_9 | Fault 11 | Mean not significant; variance is the only usable signal |
| xmv_10 | Fault 11 | Same as above |
| xmeas_7 | Fault 13 | Mean weakly significant; variance (std_ratio ~10x) more reliable |
| xmeas_11 | Fault 12 | Mean marginally significant (p=0.025); direction confirmed, magnitude varies |

### Tier 3 — Use With Caution

| Sensor | Fault | Issue |
|--------|-------|-------|
| xmeas_1 | Fault 8 | High run-to-run variance in mean-shift magnitude; not reliable as single feature |
| xmeas_4 | Fault 7 | Signal present only in early post-fault window; full-window statistics miss it |

### Tier 4 — Composition Sensors (still unverified in our EDA)

| Sensor | Candidate Fault | Status |
|--------|------------------|--------|
| xmeas_30 | Fault 2 | Not yet plotted or tested — recommended follow-up |
| xmeas_23 | Fault 1, 8 | Not yet plotted or tested — recommended follow-up |

---

## 6. Fault Classification Guide (Updated)

### Detection regime is now the primary split, not just fault category

**Mean-based detection works for:** Fault 1, 2, 6 (reliable); Fault 8 partially (xmeas_4 only)

**Variance-based detection required for:** Fault 4, 7, 11, 14 (mean-based methods will miss these entirely or mostly)

**Mixed / needs both:** Fault 12, 13

### Distinguishing similar faults (updated with statistical notes)

**Fault 4 vs Fault 11** — both reactor cooling water faults.
- Fault 4: xmv_10 MEAN shift is significant and stable (step change). Reactor temp unaffected.
- Fault 11: xmv_10 MEAN shift is NOT significant (irregular, cancels out over time), but VARIANCE is elevated. Reactor temp also shows elevated variance, not mean shift.

**Fault 12 vs Fault 14** — both cooling-related, different locations.
- Fault 12: separator sensors show mean and variance changes, but with more run-to-run variability in magnitude.
- Fault 14: reactor sensors show almost NO mean shift but very strong and very stable variance increase — the cleanest oscillation signature in the dataset.

**Fault 1 vs Fault 6** — both A feed faults, both are strong mean-shift faults, opposite direction.
- Fault 1: xmeas_1 rises ~200%, t=-147.8, extremely stable.
- Fault 6: xmeas_1 drops ~100%, t=219.8, the single most statistically robust fault in this set.

**Fault 7 vs Fault 8** — both involve oscillation in feed-related sensors.
- Fault 7: not significant over the full post-fault window — signal is concentrated early and fades. Needs short time-window detection.
- Fault 8: persistent oscillation, but the mean-shift magnitude itself is inconsistent across runs (high std of pct_change). Variance-based features are more dependable here.

---

## 7. LLM Integration Guide

(Prompt structure unchanged from v3 — see below. Content updated to reference
statistical confidence where available.)

### Recommended LLM Prompt Structure

```
You are a chemical process assistant for the Tennessee Eastman Process.
An anomaly has been detected. Based on the sensor readings and reference
document below, identify the most likely fault and provide recommendations.
Reference ranges come from EDA validated across 10 simulation runs where noted;
treat unvalidated ranges as approximate.

CURRENT ANOMALY:
- Triggered sensors: [list sensors and deviation from normal, specify mean shift vs variance increase]
- Pattern observed: [describe pattern: spike/oscillation/drop/step]

FAULT REFERENCE:
[Insert relevant sections from this document, including Section 3 statistical backing]

Respond with:
1. Most likely fault type and confidence level
2. Root cause explanation in plain language
3. Recommended actions
4. Severity level (Low/Medium/High/Critical)
```

### Example LLM Output (Fault 14, now with statistical grounding)

```
ANOMALY DETECTED — Pattern consistent with Fault 14 (Reactor CW Valve Stuck)

Triggered sensors:
- xmeas_9 (Reactor Temperature): variance approximately 13x normal, mean unchanged
- xmeas_21 (Reactor CW Outlet Temp): variance approximately 11x normal, mean unchanged

This is a variance-based signature, validated as stable across 10 independent
simulation runs. Mean-based checks alone would NOT catch this fault.

Root cause: Reactor cooling water control valve may be mechanically stuck,
preventing the control loop from regulating reactor temperature.

Recommended actions:
1. Inspect reactor cooling water valve (xmv_10) for mechanical failure
2. Check valve actuator and positioner
3. Monitor reactor temperature variance closely

Severity: HIGH
```

---

## 8. Model Training Notes for ML Engineer (Updated)

### Data Split Recommendation
- Train primarily on normal data (FaultFree_Training) for the anomaly detector.
- Use faulty data for validation, threshold tuning, and fault classification.
- Fault introduced at sample 160 (testing set), sample 20 (training set).

### CRITICAL Preprocessing Note (new in v4)
Do not rely on mean-based features alone. t-test validation shows that Faults
4, 7, 11, and 14 — four of the ten faults analyzed — are NOT statistically
detectable via mean shift. These faults are only visible through variance-type
features (rolling standard deviation, rolling variance, or oscillation amplitude
over a moving window). Recommend computing BOTH rolling mean and rolling std for
every sensor used as a model feature.

### Other Preprocessing Notes
- xmeas_9 normal range is extremely narrow (about 0.18 deg C). Normalize carefully.
- xmeas_1 mean-shift is reliable for Fault 1 and 6, but NOT reliable for Fault 8 (high run-to-run variance) — do not use the same feature/threshold logic for all three.
- Composition sensors (xmeas_23~41) remain unvalidated in our own EDA.
- xmv variables should be included as features; xmv_10 in particular is the primary signal for Fault 4.

### Recommended Model Approach
- Stage 1: Anomaly detection using BOTH mean and variance features per sensor — Isolation Forest or Autoencoder
- Stage 2: Fault classification — Random Forest or LSTM, using Section 6's detection regime split (mean-shift vs variance-based) to guide feature selection per fault
- Stage 3: LLM explanation generation, referencing Section 3 for statistical confidence language

### Faults Requiring Special Handling
- **Fault 7**: transient — needs short time-window detection, not full-window statistics
- **Fault 8**: use xmeas_4 mean-shift or variance features; avoid relying on xmeas_1 mean-shift (unstable across runs)
- **Fault 14, 11, 4**: variance/oscillation-based detection only
- **Fault 2, 13**: consider validating composition sensors (xmeas_30) and reaction-related sensors further; current signal is present but not the strongest in the set

### Validation Methodology Note
All findings above are based on simulationRun 1 (t-test) and 10 sampled runs
(1, 25, 50, 100, 150, 200, 250, 300, 400, 500) for consistency checking. This is
still a subset of the full 500 runs. Findings marked 'stable across runs' have
low variance in the 10-run sample and are reasonably trustworthy; findings not
marked this way should be treated as provisional.