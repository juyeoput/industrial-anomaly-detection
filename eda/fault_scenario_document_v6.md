# TEP Fault Scenario Document — Selected Faults v6
## Prepared by: Yoonseo (Chemical Engineering, University at Buffalo)
## For: Juyeop (ML Model Development)

**Scope note**: This document covers 10 of the 20 TEP faults. It combines
simulationRun 1 graphs, matched-window process-variable comparisons across 50
sampled runs, and a focused Fault 2 composition analysis across 10 sampled
runs. The run-1 Welch tests retained in the analysis folder are exploratory
only because adjacent time samples are autocorrelated. Run-level results are
the primary quantitative evidence in v6. Faults not covered: 3, 5, 9, 10, 15,
16, 17, 18, 19, and 20.

**Interpretation boundary**: Effect sizes, severity labels, and diagnostic
actions in this document are project-level engineering interpretations. They
are not official TEP safety ratings, operating limits, or validated plant
procedures.

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

| Variable | Name | Unit | Stream | Status as of v6 |
|----------|------|------|--------|------------------|
| xmeas_23 | Reactor Feed A Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_24 | Reactor Feed B Composition | mol% | Reactor inlet | Observed across 10 sampled runs for Fault 2; strongest in the early window |
| xmeas_25 | Reactor Feed C Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_26 | Reactor Feed D Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_27 | Reactor Feed E Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_28 | Reactor Feed F Composition | mol% | Reactor inlet | Not yet plotted or tested |
| xmeas_29 | Purge A Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_30 | Purge B Composition | mol% | Purge stream | Observed across 10 sampled runs for Fault 2; strongest early variability response |
| xmeas_31 | Purge C Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_32 | Purge D Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_33 | Purge E Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_34 | Purge F Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_35 | Purge G Composition | mol% | Purge stream | Observed across 10 sampled runs for Fault 2; persistent late mean increase |
| xmeas_36 | Purge H Composition | mol% | Purge stream | Not yet plotted or tested |
| xmeas_37 | Product D Composition | mol% | Product stream | Not yet plotted or tested |
| xmeas_38 | Product E Composition | mol% | Product stream | Not yet plotted or tested |
| xmeas_39 | Product F Composition | mol% | Product stream | Not yet plotted or tested |
| xmeas_40 | Product G Composition | mol% | Product stream | No material Fault 2 difference observed across the 10 sampled runs |
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

## 3. Validation Method and Evidence

### 3.1 Evidence levels

1. **Graphical EDA**: normal and faulty trajectories from simulationRun 1.
   These plots are examples, not population-level proof.
2. **Exploratory run-1 mean comparison**: the original Welch tests compare
   samples within one run. Their p-values can be too small because time-series
   samples are autocorrelated, so they are not treated as confirmation.
3. **Primary process validation**: for each selected fault and sensor, each of
   50 sampled simulation runs contributes one matched normal-versus-fault
   effect. Run-level differences are assessed with a one-sample t-test and a
   Wilcoxon signed-rank test.
4. **Fault 2 composition validation**: four composition sensors are compared
   across 10 sampled runs using the same matched windows.

The matched windows are:

| Window | Samples | Purpose |
|--------|---------|---------|
| Early | 160-260 | Initial and transient response after fault introduction |
| Late | 300-960 | Persistent response after the initial transient |
| Full | 160-960 | Overall post-fault behavior |

P-values are supporting evidence only. Practical interpretation prioritizes
effect magnitude, direction consistency across runs, variance ratio, and
physical plausibility. No multiple-testing correction was used, so a small
p-value alone must not determine sensor selection.

### 3.2 Fifty-run process-variable findings

<!-- AUTO:PROCESS_SUMMARY START -->
| Fault | Main observed evidence | v6 interpretation |
|-------|------------------------|-------------------|
| 1 | xmeas_1 persistent mean +203.1%; xmeas_4 -5.9% | Strong persistent mean-shift pattern |
| 2 | xmeas_1 +12.3%; xmeas_4 +2.85%; xmeas_7 response fades | Process variables respond, but composition features improve diagnosis |
| 4 | xmv_10 persistent mean +9.15%, normalized effect 6.9; reactor temperature and pressure remain near normal | Compensating controller action creates a clear valve mean shift |
| 6 | xmeas_1 -99.9%; xmeas_7 +10.0%; several late signals become fixed or zero-variance | Strong feed-loss/saturated-state pattern; fixed values are abnormal, not recovery |
| 7 | xmeas_4 early mean -0.74% with std ratio 7.3; late mean approaches zero but std ratio remains 1.53 | Early transient plus residual variability |
| 8 | Mean direction varies by run; persistent std ratios are 6.0 for xmeas_1, 4.6 for xmeas_4, and 7.5 for xmeas_7 | Variance-dominant multivariable pattern |
| 11 | xmeas_9 std ratio 4.3 and xmv_10 6.5; mean effects are small or inconsistent | Variance/irregular oscillation pattern |
| 12 | xmeas_11, xmeas_13, and xmeas_22 std ratios are 10.0, 11.6, and 6.3 | Separator-side mixed response, dominated by variability |
| 13 | xmeas_7 std ratio 12.3 with normalized late/full mean effect 2.8; xmeas_6 std ratio 1.36 | Mixed pressure response, variance dominant |
| 14 | xmeas_9 std ratio 13.4 and xmeas_21 10.5; mean effects are practically zero | Persistent reactor cooling-side oscillation pattern |
<!-- AUTO:PROCESS_SUMMARY END -->

These values summarize the sampled runs and are descriptive estimates, not
universal detection thresholds.

### 3.3 Fault 2 composition findings across 10 sampled runs

<!-- AUTO:COMPOSITION_SUMMARY START -->
| Sensor | Early window | Late window | Interpretation |
|--------|--------------|-------------|----------------|
| xmeas_24, Reactor Feed B | Mean +7.40%; std ratio 2.64 | Mean +0.44%; std ratio 1.14 | Strong initial composition response that largely fades |
| xmeas_30, Purge B | Mean +6.99%; std ratio 3.59 | Mean -0.11%; std ratio 1.33 | Strongest early variability response among the four tested sensors |
| xmeas_35, Purge G | Mean -1.41%; std ratio 1.26 | Mean +5.22%; std ratio 1.07 | Persistent late mean increase; useful complement to xmeas_30 |
| xmeas_40, Product G | Mean +0.03%; std ratio 1.00 | Mean +0.03%; std ratio 1.00 | No material difference observed in the sampled runs |
<!-- AUTO:COMPOSITION_SUMMARY END -->

Fault 2 is therefore best represented with both an early variability feature
(especially xmeas_30, with xmeas_24 as support) and a late mean feature
(xmeas_35). The xmeas_40 result only means that this sensor showed no material
difference in these sampled runs; it does not prove that product quality can
never be affected.

---

## 4. Fault Scenario Mapping Table

| Fault | Type | Category | Key Sensors | Pattern Summary | Detection Regime | Project Severity |
|-------|------|----------|-------------|-----------------|------------------|------------------|
| 1 | A/C feed ratio disturbance | Feed | xmeas_1, xmeas_4, xmeas_7 | Large, persistent, directionally consistent mean changes | Mean shift | High |
| 2 | B composition change | Feed | xmeas_30, xmeas_24, xmeas_35; xmeas_1, xmeas_4 | Early composition variability followed by a late purge-composition mean response | Time-windowed composition + process mean | Medium |
| 4 | Reactor CW inlet temperature step | Cooling | xmv_10 | Persistent compensating valve opening while reactor state remains controlled | Mean shift in manipulated variable | Medium |
| 6 | A feed loss | Feed | xmeas_1, xmeas_7 | Near-total A-flow loss followed by an abnormal saturated/fixed state | Mean shift + state constraint | Critical |
| 7 | C feed pressure disturbance | Feed | xmeas_4, xmeas_7 | Strong initial transient; mean fades while some excess variability remains | Early-window + variance | Medium |
| 8 | A/B/C composition change | Feed | xmeas_1, xmeas_4, xmeas_7 | Run-dependent means with persistent multivariable variability | Variance dominant | High |
| 11 | Reactor CW inlet temperature random variation | Cooling | xmeas_9, xmv_10 | Small mean effect with persistent irregular variability | Variance/oscillation | Medium |
| 12 | Separator cooling disturbance | Cooling | xmeas_11, xmeas_13, xmeas_22 | Separator-side mean and variance response, dominated by variability | Mixed, variance dominant | High |
| 13 | Reaction kinetics change | Reaction | xmeas_7, xmeas_6 | Strong reactor-pressure variability with a late mean component | Mixed, variance dominant | Medium |
| 14 | Reactor CW valve sticking | Cooling | xmeas_9, xmeas_21 | Near-zero mean effect with persistent high-frequency variability | Variance/oscillation | High |

Project severity is a prioritization aid for this portfolio, not an official
plant hazard classification.

---

## 5. Detailed Fault Descriptions

### Fault 1 — A/C Feed Ratio Disturbance
- **Root cause**: Disturbance in A component feed ratio relative to C
- **Observed evidence**: xmeas_1 shows a persistent increase of about 203% across the 50 sampled runs; xmeas_4 decreases about 5.9%
- **Secondary response**: xmeas_7 shows transient pressure dynamics
- **Severity**: High — disrupts reaction stoichiometry
- **Diagnostic checks**: Inspect A-feed measurement, xmv_3 behavior, and the A/C ratio-control loop

### Fault 2 — B Component Composition Change
- **Root cause**: B (inert) component concentration in feed changes
- **Early composition response**: xmeas_30 mean +6.99% and std ratio 3.59; xmeas_24 mean +7.40% and std ratio 2.64
- **Late composition response**: xmeas_35 mean +5.22%; the early xmeas_30 and xmeas_24 responses largely fade
- **Process response**: xmeas_1 and xmeas_4 show persistent but less fault-specific mean changes; xmeas_7 is mainly transient
- **No material sampled-run response**: xmeas_40 remains near its matched normal values
- **Temperature response**: Minimal
- **Severity**: Medium — project-level ranking based on upstream composition disturbance
- **Diagnostic checks**: Review feed-composition analyzers, B-source conditions, purge composition, and xmv_6 behavior; do not prescribe a new purge setting from this analysis alone

### Fault 4 — Reactor Cooling Water Inlet Temperature (Step Change)
- **Root cause**: Cooling water supply temperature increases as a step change
- **Primary signal**: xmv_10 opens about 9.15% farther and remains elevated across the sampled runs
- **Important note**: This fault has a mean-shift signature in xmv_10. Reactor temperature and pressure stay close to normal because the control loop compensates.
- **Severity**: Medium — cooling capacity reduced but currently compensated
- **Diagnostic checks**: Review cooling-water supply temperature, exchanger performance, and the xmv_10 control response

### Fault 6 — A Feed Loss
- **Root cause**: A component feed is lost or blocked
- **First signal**: xmeas_1 falls by about 99.9%; xmeas_7 rises by about 10%
- **Later behavior**: Some signals become fixed or zero-variance. This is an abnormal saturated state, not evidence of process recovery.
- **Severity**: Critical within this project's ranking; this is not an official hazard assessment
- **Diagnostic checks**: Treat the pattern as high priority and inspect the A-feed path, measurement, and xmv_3 response under the site's approved procedures

### Fault 7 — C Feed Pressure Disturbance
- **Root cause**: C component supply pressure fluctuates
- **First signal**: xmeas_4 drops sharply then overshoots; xmeas_7 oscillates sharply
- **Persistence**: The mean response is concentrated in the early window and fades, but late variability remains above normal on some sensors. Treat it as an early transient with a residual variance signature, not complete recovery.
- **Severity**: Medium
- **Diagnostic checks**: Review the C-feed pressure regulator and check whether the transient recurs

### Fault 8 — A/B/C Composition Simultaneous Change
- **Root cause**: Multiple feed components change composition around the same time
- **Observed evidence**: xmeas_1, xmeas_4, and xmeas_7 have persistent variance ratios of roughly 6.0, 4.6, and 7.5
- **Important note**: Mean direction and magnitude vary by run. Use multivariable rolling variance and temporal features rather than a fixed xmeas_1 mean threshold.
- **Severity**: High — complex multi-variable disturbance
- **Diagnostic checks**: Review feed composition analyzers and the feed-mixing system

### Fault 11 — Reactor CW Inlet Temperature (Random Variation)
- **Root cause**: Cooling water supply temperature varies irregularly
- **Observed evidence**: xmeas_9 std ratio is about 4.3 and xmv_10 about 6.5, while mean effects remain small or inconsistent
- **Key difference from Fault 4**: Fault 4 produces a persistent xmv_10 mean shift; Fault 11 primarily increases irregular variability.
- **Severity**: Medium
- **Diagnostic checks**: Review cooling-water supply stability, pump behavior, and cooling controls

### Fault 12 — Separator Cooling System Disturbance
- **Root cause (per TEP documentation)**: Disturbance related to separator cooling water inlet temperature; our EDA observed downstream effects (temperature/pressure oscillation), not the mechanism directly
- **Observed evidence**: xmeas_11, xmeas_13, and xmeas_22 show large variability increases; xmeas_11 tends to decrease late while xmeas_13 tends to increase
- **Key difference from Fault 14**: Fault 12 affects separator sensors; reactor sensors (xmeas_9, xmeas_21) remain close to normal
- **Severity**: High
- **Diagnostic checks**: Review xmv_11 and the separator cooling circuit

### Fault 13 — Reaction Kinetics Change
- **Root cause**: Reaction rate constant changes (catalyst degradation or feed impurity effect)
- **Observed evidence**: xmeas_7 std ratio is about 12.3 with a meaningful late mean component; xmeas_6 has a smaller variability increase
- **Severity**: Medium — gradual degradation rather than acute event
- **Diagnostic checks**: Review catalyst condition, feed purity, and reactor pressure behavior

### Fault 14 — Reactor Cooling Water Valve Sticking
- **Root cause**: Reactor cooling-water valve sticking according to the TEP fault definition; this EDA verifies the response pattern, not the mechanical mechanism itself
- **Key sensors**: xmeas_9 (Reactor Temperature), xmeas_21 (Reactor CW Outlet Temp)
- **Observed pattern**: Persistent high-frequency variability with std ratios about 13.4 and 10.5, while practical mean effects remain near zero
- **Modeling note**: Rolling variance, spectral, or sequence features are substantially more informative than a mean-only feature for this response.
- **Severity**: High
- **Diagnostic checks**: Inspect the reactor cooling loop, including valve, actuator, positioner, and temperature measurements

All diagnostic checks above are investigation prompts. They must not be used as
automatic control commands or substitutes for approved operating procedures.

---

## 6. Feature Priority for Model Development

This is a feature-engineering guide, not a recommendation to discard the other
variables before an ablation study.

| Feature group | Faults | Recommended representation |
|---------------|--------|----------------------------|
| xmeas_1, xmeas_4 | 1, 2, 6 | Raw scaled value, rolling mean, change from baseline |
| xmv_10 | 4, 11 | Rolling mean for Fault 4; rolling std and temporal features for Fault 11 |
| xmeas_4, xmeas_7 | 7 | Short early windows plus rolling std; avoid full-window mean alone |
| xmeas_1, xmeas_4, xmeas_7 | 8 | Multivariable rolling std/covariance or sequence representation |
| xmeas_9, xmv_10 | 11 | Rolling std, range, frequency or sequence features |
| xmeas_11, xmeas_13, xmeas_22 | 12 | Rolling mean and std, with separator-side grouping |
| xmeas_7, xmeas_6 | 13 | Rolling std plus late-window mean or trend |
| xmeas_9, xmeas_21 | 14 | Rolling std, range, spectral energy, or sequence features |
| xmeas_30, xmeas_24 | 2 | Early-window mean and std |
| xmeas_35 | 2 | Late-window rolling mean |

For the four tested Fault 2 composition variables, xmeas_40 is a useful
negative-control candidate but should not be called universally irrelevant.
The remaining composition variables have not yet received the same focused
multi-run validation.

---

## 7. Fault Classification Guide

- **Persistent mean dominant**: Faults 1, 4, and 6.
- **Composition and time-window dependent**: Fault 2.
- **Early transient with residual variance**: Fault 7.
- **Variance dominant**: Faults 8, 11, and 14.
- **Mixed mean and variance**: Faults 12 and 13.

### Distinguishing similar faults

**Fault 4 vs Fault 11**: Fault 4 has a persistent xmv_10 mean increase. Fault
11 has a much stronger variability response in xmv_10 and xmeas_9.

**Fault 12 vs Fault 14**: Fault 12 is centered on separator variables
(xmeas_11, xmeas_13, xmeas_22). Fault 14 is centered on reactor cooling-side
variables (xmeas_9, xmeas_21).

**Fault 1 vs Fault 6**: Both produce large xmeas_1 changes, but in opposite
directions. Fault 1 raises xmeas_1 by roughly 203%; Fault 6 reduces it by
roughly 99.9%.

**Fault 7 vs Fault 8**: Fault 7 has a concentrated early transient and a
smaller residual variability response. Fault 8 maintains strong
multivariable variability over the late window.

---

## 8. LLM Explanation Guide

The LLM receives model evidence; it does not independently diagnose the raw
process. It should use cautious language such as **"pattern consistent with"**
and must separate observed evidence from inferred mechanism.

### Recommended prompt structure

```text
You are explaining an anomaly detected in the Tennessee Eastman Process.
Use only the supplied model result, sensor evidence, and fault reference.
Do not invent measurements, setpoints, valve commands, or safety procedures.

MODEL RESULT:
- Candidate fault(s): [ranked classes and probabilities]
- Detection threshold and score: [values]

SENSOR EVIDENCE:
- Triggered features: [sensor, feature type, value, normal reference]
- Time pattern: [early, late, persistent, oscillatory]

FAULT REFERENCE:
[relevant v6 entries]

Respond with:
1. Most likely pattern and calibrated confidence
2. Observed supporting evidence
3. Plausible process interpretation, clearly labeled as an inference
4. Diagnostic checks only, not operating commands
5. Important uncertainty or competing fault
```

### Example Fault 2 explanation

```text
The observed pattern is consistent with Fault 2, a B-composition disturbance.
Confidence should follow the classifier's calibrated probability rather than
being invented by the LLM.

Evidence: xmeas_30 and xmeas_24 show elevated early-window mean and variability,
while xmeas_35 shows a persistent late mean increase. xmeas_40 shows no material
difference in the sampled-run analysis.

Process interpretation: this combination is consistent with an upstream
composition change propagating into the purge stream. This is an inference,
not direct proof of inert accumulation.

Diagnostic checks: review feed and purge composition measurements and inspect
the associated control-loop trends under approved operating procedures.
```

---

## 9. Model Handoff Notes

### 9.1 Leakage-safe split

- Split data by `simulationRun`, never by individual rows or overlapping
  windows. No run may appear in more than one of train, validation, and test.
- Treat the pre-injection segment of a faulty run as normal for labeling, but
  keep the entire run in one split.
- Fit scalers and other learned preprocessing only on normal training runs.
- Keep the final test runs untouched until the model and thresholds are fixed.

### 9.2 Training roles

- An unsupervised anomaly detector may train on normal training runs only.
- A supervised fault classifier may use labeled faulty training runs.
- Use faulty validation runs for model selection and classifier calibration.
- Calibrate the anomaly threshold on normal validation runs to a declared
  target false-positive rate; do not tune it on the final faulty test set.

### 9.3 Features and experiments

- Start with raw scaled values plus rolling mean, rolling std, range, and rate
  of change. Window lengths must be chosen on validation runs.
- Add spectral or sequence features for the oscillatory faults if rolling
  statistics are insufficient.
- Include manipulated variables; xmv_10 is central to separating Fault 4 and
  Fault 11.
- Include xmeas_24, xmeas_30, and xmeas_35 for Fault 2.
- Compare all 52 process variables (41 XMEAS + 11 XMV) against the selected
  feature set through an ablation study. Do not assume EDA priority alone is
  the optimal model input.

### 9.4 Required evaluation

- Report anomaly false-alarm rate on normal test runs.
- Report per-fault recall, precision, F1, and a confusion matrix.
- Report detection delay from sample 160 for testing data.
- Show run-level distributions or confidence intervals, not only pooled-row
  scores.
- Evaluate early and late windows separately for Faults 2 and 7.

### 9.5 Evidence files

- `fault_run_level_validation.csv`: matched-window process results across 50
  sampled runs.
- `fault2_composition_multi_run_summary.csv`: Fault 2 composition results
  across 10 sampled runs.
- The run-1 graph files: visual examples for explanation and QA.
- The exploratory run-1 t-test output: retained for traceability, not used as
  independent statistical confirmation.

---

## 10. Remaining Limitations

- Only 10 of the 20 faults are documented here.
- Graphs show one representative run and should not be read as universal
  trajectories.
- Process validation uses 50 sampled runs rather than every available run.
- Focused multi-run composition validation currently covers only four Fault 2
  sensors and 10 sampled runs.
- Statistical tests are numerous and unadjusted for multiplicity; effect size,
  consistency, and held-out model performance remain essential.
- Fault labels describe the simulator scenarios. Real-plant diagnosis would
  require instrumentation checks, process context, and site procedures.

### Version change from v5 to v6

v6 replaces single-run statistical claims with run-level evidence, adds the
10-run Fault 2 composition results, corrects the Fault 4/6/7 detection
descriptions, separates diagnostic suggestions from operating instructions,
and adds leakage-safe model handoff and evaluation requirements.
