# TEP Fault Scenario Document — Selected Faults v3
## Prepared by: Yoonseo (Chemical Engineering, University at Buffalo)
## For: Junyeop (ML Model Development)

**Scope note**: This document covers 10 of the 20 TEP faults, based on EDA
conducted on simulationRun 1 only. Numerical ranges reflect observations from
this specific run and should be treated as illustrative, not fixed thresholds.
Faults not covered: 3, 5, 9, 10, 15, 16, 17, 18, 19, 20.

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
- EDA in this document was performed on simulationRun == 1 only, unless noted otherwise

---

## 2. Complete Variable Definitions

### Metadata Columns

| Column | Description |
|--------|-------------|
| faultNumber | 0 = normal, 1-20 = fault type |
| simulationRun | Random seed run number (1-500) |
| sample | Time step index (1-500 training, 1-960 testing) |

### Measured Variables — Process (xmeas_1 ~ xmeas_22)

Ranges below are descriptive statistics from FaultFree_Testing (all normal data,
all runs), not from a single run.

| Variable | Name | Unit | Normal Mean | Normal Min | Normal Max | Physical Meaning |
|----------|------|------|-------------|------------|------------|-----------------|
| xmeas_1 | A Feed Flow | kscmh | 0.251 | 0.123 | 0.390 | A component flow rate into reactor. Key feed variable. |
| xmeas_2 | D Feed Flow | kg/hr | 3663.8 | 3503.3 | 3824.7 | Liquid reactant D flow into reactor. |
| xmeas_3 | E Feed Flow | kg/hr | 4508.9 | 4338.2 | 4689.2 | Liquid reactant E flow into reactor. |
| xmeas_4 | A/C Feed Flow | kscmh | 9.347 | 8.936 | 9.749 | Mixed A and C stream total flow. Sensitive to feed ratio changes. |
| xmeas_5 | Recycle Flow | kscmh | 26.902 | 26.018 | 27.822 | Gas recycle loop flow rate from compressor. |
| xmeas_6 | Reactor Feed Rate | kscmh | 42.338 | 41.441 | 43.250 | Total volumetric flow entering reactor. |
| xmeas_7 | Reactor Pressure | kPa | 2705.0 | 2667.8 | 2736.9 | Reactor operating pressure. Broadly responsive across several fault types observed in our EDA (1,2,4,6,7,8,13). |
| xmeas_8 | Reactor Level | % | 75.0 | 72.441 | 77.386 | Liquid level inside reactor vessel. Controlled by product withdrawal. |
| xmeas_9 | Reactor Temperature | deg C | 120.40 | 120.31 | 120.49 | Core reaction state indicator. Very narrow normal range (about 0.18 deg C). |
| xmeas_10 | Purge Rate | kscmh | 0.337 | 0.278 | 0.392 | Flow rate of purge stream removing inert B component. |
| xmeas_11 | Separator Temperature | deg C | 80.107 | 79.05 | 81.217 | Vapor-liquid separator operating temperature. |
| xmeas_12 | Separator Level | % | 50.0 | 45.411 | 54.258 | Liquid level in separator. |
| xmeas_13 | Separator Pressure | kPa | 2633.7 | 2594.7 | 2666.7 | Separator operating pressure. |
| xmeas_14 | Separator Underflow | m3/hr | 25.161 | 20.707 | 29.961 | Liquid flow from separator to stripper. |
| xmeas_15 | Stripper Level | % | 50.0 | 45.601 | 54.245 | Liquid level in product stripper. |
| xmeas_16 | Stripper Pressure | kPa | 3102.2 | 3071.5 | 3132.5 | Stripper column operating pressure. |
| xmeas_17 | Stripper Underflow | m3/hr | 22.947 | 20.265 | 26.045 | Final product flow rate out of stripper. |
| xmeas_18 | Stripper Temperature | deg C | 65.803 | 63.845 | 67.652 | Stripper bottom temperature. Indicates separation efficiency. |
| xmeas_19 | Stripper Steam Flow | kg/hr | 232.215 | 184.61 | 278.28 | Steam flow supplying heat to stripper reboiler. |
| xmeas_20 | Compressor Work | kW | 341.418 | 333.51 | 349.33 | Energy consumption of recycle compressor. |
| xmeas_21 | Reactor CW Outlet Temp | deg C | 94.601 | 93.979 | 95.227 | Reactor cooling water outlet temperature. |
| xmeas_22 | Separator CW Outlet Temp | deg C | 77.294 | 76.005 | 78.554 | Separator cooling water outlet temperature. |

### Measured Variables — Composition Analyzers (xmeas_23 ~ xmeas_41)

These were NOT plotted in our EDA. Descriptions below are based on TEP
documentation, not on our own graphs. Treat as reference only until verified.

| Variable | Name | Unit | Stream | Physical Meaning |
|----------|------|------|--------|-----------------|
| xmeas_23 | Reactor Feed A Composition | mol% | Reactor inlet | A component fraction entering reactor |
| xmeas_24 | Reactor Feed B Composition | mol% | Reactor inlet | B (inert) fraction entering reactor |
| xmeas_25 | Reactor Feed C Composition | mol% | Reactor inlet | C component fraction entering reactor |
| xmeas_26 | Reactor Feed D Composition | mol% | Reactor inlet | D component fraction entering reactor |
| xmeas_27 | Reactor Feed E Composition | mol% | Reactor inlet | E component fraction entering reactor |
| xmeas_28 | Reactor Feed F Composition | mol% | Reactor inlet | F component fraction entering reactor |
| xmeas_29 | Purge A Composition | mol% | Purge stream | A fraction in purge |
| xmeas_30 | Purge B Composition | mol% | Purge stream | B (inert) fraction in purge — candidate indicator of B buildup, not yet confirmed in our graphs |
| xmeas_31 | Purge C Composition | mol% | Purge stream | C fraction in purge |
| xmeas_32 | Purge D Composition | mol% | Purge stream | D fraction in purge |
| xmeas_33 | Purge E Composition | mol% | Purge stream | E fraction in purge |
| xmeas_34 | Purge F Composition | mol% | Purge stream | F fraction in purge |
| xmeas_35 | Purge G Composition | mol% | Purge stream | G (product) fraction in purge — potential loss indicator |
| xmeas_36 | Purge H Composition | mol% | Purge stream | H fraction in purge |
| xmeas_37 | Product D Composition | mol% | Product stream | D fraction in final product |
| xmeas_38 | Product E Composition | mol% | Product stream | E fraction in final product |
| xmeas_39 | Product F Composition | mol% | Product stream | F fraction in final product — byproduct indicator |
| xmeas_40 | Product G Composition | mol% | Product stream | G fraction in final product — product purity indicator |
| xmeas_41 | Product H Composition | mol% | Product stream | H fraction in final product — product purity indicator |

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

## 3. Fault Scenario Mapping Table

**Note**: Patterns below are based on simulationRun 1 only. Treat numeric ranges
as illustrative examples of the pattern shape, not fixed detection thresholds.

| Fault | Type (per TEP documentation) | Category | Key Sensors Observed | Pattern Summary | Persistence | Severity |
|-------|-------------------------------|----------|----------------------|-----------------|-------------|----------|
| 1 | A/C feed ratio disturbance | Feed | xmeas_1, xmeas_4, xmeas_7 | xmeas_1 rises well above normal, xmeas_4 drops, xmeas_7 fluctuates | Persistent | High |
| 2 | B composition change | Feed | xmeas_4, xmeas_7 | Subtle in process variables; xmeas_4 slightly elevated, xmeas_7 transiently elevated | Persistent | Medium |
| 4 | Reactor CW inlet temperature (step) | Cooling | xmv_10 (primary), xmeas_7 (secondary) | xmv_10 opens wider and stays elevated; xmeas_9 stays near normal (controller compensates) | Persistent | Medium |
| 6 | A feed loss | Feed | xmeas_1, xmeas_7 | xmeas_1 drops to near 0, xmeas_7 rises without stabilizing | Persistent | Critical |
| 7 | C feed pressure disturbance | Feed | xmeas_4, xmeas_7 | Sharp oscillation then apparent recovery within the observed window | Transient (in this run) | Medium |
| 8 | A/B/C composition change | Feed | xmeas_1, xmeas_4, xmeas_7 | All three oscillate continuously in a related pattern | Persistent | High |
| 11 | Reactor CW inlet temperature (random) | Cooling | xmeas_9, xmv_10 | xmeas_9 irregular oscillation, xmv_10 fluctuates over a wide range | Persistent | Medium |
| 12 | Separator cooling system disturbance | Cooling | xmeas_11, xmeas_22, xmeas_13 | xmeas_11 and xmeas_22 oscillate, xmeas_13 fluctuates; reactor sensors largely unaffected | Persistent | High |
| 13 | Reaction kinetics change | Reaction | xmeas_7 | xmeas_7 oscillates with amplitude that appears to grow over the observed window | Persistent | Medium |
| 14 | Reactor CW valve stuck | Cooling | xmeas_9, xmeas_21 | xmeas_9 and xmeas_21 both shift from stable to persistent oscillation | Persistent | High |

---

## 4. Detailed Fault Descriptions

### Fault 1 — A/C Feed Ratio Disturbance
- **Root cause**: Disturbance in A component feed ratio relative to C
- **First signal**: xmeas_1 (A Feed Flow) rises well above its normal range
- **Secondary signals**: xmeas_4 (A/C Feed Flow) drops, xmeas_7 (Reactor Pressure) fluctuates
- **Temperature response**: Minimal in xmeas_9
- **Persistence**: Signal remains for the full observed window
- **Severity**: High — disrupts reaction stoichiometry
- **Recommended action**: Check A feed valve (xmv_3), inspect A/C feed ratio controller, verify C feed pressure
- **Chemical engineering interpretation**: The core reaction consumes A and C together. An imbalance shifts selectivity toward byproduct F, which is a stoichiometry problem more than a safety problem in the short term.
- **LLM explanation template**: A component feed flow is elevated well above its normal range. A/C feed ratio appears disrupted. Check A feed valve and ratio controller.

### Fault 2 — B Component Composition Change
- **Root cause**: B (inert) component concentration in feed changes
- **Observed in process variables**: A/C Feed Flow (xmeas_4) shifts slightly upward; reactor pressure (xmeas_7) shows a transient deviation
- **Important caveat**: This fault is subtle in the process variables we plotted. Composition sensors (especially xmeas_30, Purge B Composition) are the theoretically expected primary indicator per TEP documentation, but we have not directly confirmed this in our own EDA. This should be verified separately before relying on it for model design.
- **Temperature response**: Minimal
- **Persistence**: Persistent but subtle — harder to detect than Fault 1
- **Severity**: Medium — inert buildup could reduce reactor efficiency over time
- **Recommended action**: Check feed composition analyzer, inspect B component supply, consider verifying with composition sensors before finalizing detection logic
- **LLM explanation template**: Subtle shift detected in A/C feed flow and reactor pressure, consistent with a possible feed composition change. Recommend checking composition analyzers to confirm.

### Fault 4 — Reactor Cooling Water Inlet Temperature (Step Change)
- **Root cause**: Cooling water supply temperature increases as a step change
- **Primary signal**: xmv_10 (Reactor CW Valve) opens wider and stays at an elevated position — this is the clearest and most reliable indicator
- **Secondary signal**: xmeas_7 (Reactor Pressure) slightly elevated
- **Important note**: Fault 4 is best detected through xmv_10, not xmeas_9. The temperature controller compensates effectively, so xmeas_9 stays close to normal. Relying on reactor temperature alone will likely miss this fault.
- **Persistence**: Persistent — valve stays at elevated opening
- **Severity**: Medium — cooling capacity is reduced but currently compensated
- **Recommended action**: Check cooling water supply temperature at cooling tower, inspect heat exchangers
- **LLM explanation template**: Reactor cooling water valve is holding an elevated opening compared to normal. This suggests the controller is compensating for a cooling water temperature increase. Reactor temperature itself may look normal. Check cooling tower operation.

### Fault 6 — A Feed Loss
- **Root cause**: A component feed is lost or blocked
- **First signal**: xmeas_1 (A Feed Flow) drops toward 0 shortly after fault introduction
- **Secondary signal**: xmeas_7 (Reactor Pressure) rises and does not appear to stabilize within the observed window
- **Temperature response**: xmeas_9 appears to stabilize at a shifted value as reaction slows
- **Persistence**: Persistent — process does not self-recover in the observed window
- **Severity**: CRITICAL — this is the most dangerous fault observed. Pressure trend is concerning and should be treated conservatively.
- **Recommended action**: Treat as high priority. Check A feed line for blockage. Check xmv_3 valve. Escalate to safety systems if reactor pressure continues rising beyond normal operating limits.
- **LLM explanation template**: CRITICAL ALERT. A component feed flow has dropped sharply toward zero. Reactor pressure is rising and not stabilizing. Immediate inspection of A feed line and valve (xmv_3) recommended. Consider safety system escalation.

### Fault 7 — C Feed Pressure Disturbance
- **Root cause**: C component supply pressure fluctuates
- **First signal**: xmeas_4 (A/C Feed Flow) drops sharply then overshoots
- **Secondary signal**: xmeas_7 (Reactor Pressure) oscillates sharply
- **Persistence**: Appeared transient in this run — signal diminished after roughly 400 samples, but this should not be assumed to hold across all simulation runs
- **Severity**: Medium — appeared to be a temporary disruption in this run
- **Recommended action**: Check C feed pressure regulator, monitor for recurrence, log event for maintenance review
- **LLM explanation template**: C feed pressure disturbance suspected. A/C feed flow and reactor pressure showed sharp oscillation. Check C feed pressure regulator and monitor for recurrence.

### Fault 8 — A/B/C Composition Simultaneous Change
- **Root cause**: Multiple feed components change composition around the same time
- **First signal**: xmeas_1 and xmeas_4 begin oscillating in a related pattern
- **Secondary signal**: xmeas_7 oscillates continuously
- **Temperature response**: Minimal
- **Persistence**: Persistent oscillation — system does not appear to stabilize in the observed window
- **Severity**: High — multi-variable disturbance, more complex than single-feed faults
- **Recommended action**: Check feed composition analyzers, inspect feed mixing system, verify supply quality
- **LLM explanation template**: Multiple feed-related signals showing simultaneous abnormal oscillation. Suggests a compound feed composition issue. Check composition analyzers and supply quality.

### Fault 11 — Reactor CW Inlet Temperature (Random Variation)
- **Root cause**: Cooling water supply temperature varies irregularly, as opposed to a single step change
- **First signal**: xmv_10 (Reactor CW Valve) oscillates over a wide range
- **Secondary signal**: xmeas_9 (Reactor Temperature) oscillates irregularly
- **Key difference from Fault 4**: Fault 4 looks like a step (valve settles at a new level). Fault 11 looks irregular (valve keeps fluctuating).
- **Persistence**: Persistent irregular oscillation
- **Severity**: Medium — reactor temperature control appears less stable than normal
- **Recommended action**: Check cooling water supply for instability, inspect cooling tower controls and pump
- **LLM explanation template**: Reactor cooling water valve is fluctuating irregularly. Reactor temperature is also oscillating. Cooling water supply temperature may be unstable. Check cooling tower and pump.

### Fault 12 — Separator Cooling System Disturbance
- **Root cause (per TEP documentation)**: Disturbance related to separator cooling water inlet temperature. Note: our EDA observed the downstream effects (temperature and pressure oscillation), not the cooling water flow or inlet temperature directly, so we describe this as a general cooling system disturbance rather than assuming the specific mechanism.
- **First signal**: xmeas_11 (Separator Temperature) shifts from stable to a wide oscillating range
- **Secondary signals**: xmeas_22 (Separator CW Outlet Temp) oscillates, xmeas_13 (Separator Pressure) fluctuates
- **Key difference from Fault 14**: Fault 14 affects reactor sensors. Fault 12 affects separator sensors. In our EDA, xmeas_9 and xmeas_21 (reactor sensors) remained close to normal during Fault 12.
- **Persistence**: Persistent
- **Severity**: High — separator performance appears degraded
- **Recommended action**: Check separator cooling water valve (xmv_11), inspect separator cooling circuit
- **LLM explanation template**: Separator temperature and cooling water outlet temperature are both oscillating outside normal range. Reactor sensors appear unaffected, suggesting the issue is localized to the separator cooling system. Check xmv_11 and separator cooling circuit.

### Fault 13 — Reaction Kinetics Change
- **Root cause**: Reaction rate constant changes (e.g., catalyst degradation or feed impurity effect)
- **First signal**: xmeas_7 (Reactor Pressure) begins oscillating with amplitude that appears to increase over the observed window
- **Secondary signals**: Minimal in other sensors we plotted
- **Temperature response**: xmeas_9 shows little change
- **Persistence**: Persistent — appears to worsen over time in this run
- **Severity**: Medium — appears to be a gradual degradation rather than an acute event
- **Recommended action**: Check catalyst condition and activity, review reactor temperature profile, inspect feed purity
- **LLM explanation template**: Reactor pressure oscillation with growing amplitude detected. Possible reaction kinetics change — check catalyst condition and feed purity.

### Fault 14 — Reactor Cooling Water Valve Stuck

**Key sensors**:
- xmeas_9: Reactor Temperature
- xmeas_21: Reactor Cooling Water Outlet Temperature

**Observed pattern**:
After fault introduction, reactor temperature changes from a stable narrow range
around 120.4 deg C to persistent high-frequency oscillation roughly between 120.0
and 120.8 deg C. Reactor cooling water outlet temperature also changes from stable
behavior around 94.5 deg C to persistent oscillation roughly between 92 and 97 deg C.

**Secondary signal**:
Reactor pressure shows some fluctuation, but it is not the primary indicator for this fault.

**Modeling note**:
Fault 14 should be detected mainly through oscillation amplitude and variability in
xmeas_9 and xmeas_21, rather than a shift in the mean value alone.

**Chemical engineering interpretation**:
Because the reactor is exothermic, cooling water control is critical for stable operation.
If the cooling water control valve is stuck, the temperature control loop cannot regulate
heat removal smoothly, causing both reactor temperature and cooling water outlet
temperature to oscillate persistently.

**Recommended action**: Inspect reactor cooling water valve (xmv_10) for mechanical failure, check valve actuator and positioner

**LLM explanation template**: Reactor temperature and reactor cooling water outlet temperature are both oscillating outside their normal ranges, with pressure relatively unaffected. This pattern is consistent with a stuck reactor cooling water valve. Inspect valve xmv_10 and its actuator.

---

## 5. Key Sensor Priority for Model Training

Based on patterns observed in our EDA (simulationRun 1). Should be validated
against additional runs before being treated as final.

### Tier 1 — Broadly Responsive Sensors

| Sensor | Name | Responds to (observed) | Why Important |
|--------|------|------------------------|---------------|
| xmeas_7 | Reactor Pressure | 1, 2, 4, 6, 7, 8, 13 | Responded in most faults we observed. Candidate for a general-purpose anomaly signal. |
| xmeas_1 | A Feed Flow | 1, 6, 8 | Drops toward 0 in Fault 6 (critical). Rises in Fault 1. |
| xmeas_4 | A/C Feed Flow | 1, 2, 7, 8 | Sensitive to feed-related faults. |
| xmeas_9 | Reactor Temperature | 11, 14 | Very narrow normal range (about 0.18 deg C). Any oscillation stands out. |

### Tier 2 — Fault-Specific Sensors

| Sensor | Name | Specific Fault | Why Important |
|--------|------|----------------|---------------|
| xmeas_21 | Reactor CW Outlet Temp | Fault 14 | Co-oscillates with xmeas_9 when cooling valve is stuck |
| xmeas_11 | Separator Temperature | Fault 12 | Primary observed signal for separator cooling disturbance |
| xmeas_22 | Separator CW Outlet Temp | Fault 12 | Co-oscillates with xmeas_11 |
| xmeas_13 | Separator Pressure | Fault 12 | Secondary signal |
| xmv_10 | Reactor CW Valve | Fault 4, 11 | Valve behavior is more diagnostic than reactor temperature for these two faults |

### Tier 3 — Composition Sensors (unverified in our own EDA)

| Sensor | Name | Candidate Fault | Status |
|--------|------|------------------|--------|
| xmeas_30 | Purge B Composition | Fault 2 | Not plotted by us — recommended for follow-up EDA |
| xmeas_23 | Reactor Feed A Composition | Fault 1, 8 | Not plotted by us — recommended for follow-up EDA |
| xmeas_40 | Product G Composition | Feed faults generally | Not plotted by us — recommended for follow-up EDA |

---

## 6. Fault Classification Guide for Model

### By Category

**Feed Faults** (Fault 1, 2, 6, 7, 8)
- Commonly involved sensors: xmeas_1, xmeas_4, xmeas_7
- These faults affect what goes INTO the reactor
- Pressure (xmeas_7) is often the first to respond, based on our EDA

**Cooling Faults** (Fault 4, 11, 12, 14)
- Commonly involved sensors: xmeas_9, xmeas_21, xmeas_11, xmeas_22, xmv_10
- These faults affect temperature control systems
- Location matters: reactor (Fault 4, 11, 14) vs separator (Fault 12)

**Reaction Fault** (Fault 13)
- Primary sensor: xmeas_7
- Distinguishing pattern: amplitude appears to increase over time
- Other sensors relatively unaffected in our EDA

### How to Distinguish Similar Faults

**Fault 4 vs Fault 11** (both reactor cooling water temperature faults)
- Fault 4: xmv_10 steps up and stays at a new level. xmeas_9 stays close to normal.
- Fault 11: xmv_10 fluctuates irregularly. xmeas_9 also oscillates irregularly.

**Fault 12 vs Fault 14** (both cooling-related)
- Fault 12: Separator sensors affected (xmeas_11, xmeas_22, xmeas_13). Reactor sensors stayed near normal in our EDA.
- Fault 14: Reactor sensors affected (xmeas_9, xmeas_21). Separator sensors not examined for this fault in our EDA.

**Fault 1 vs Fault 6** (both A feed faults)
- Fault 1: xmeas_1 rises well above normal. Ratio disturbed but A still flowing.
- Fault 6: xmeas_1 drops toward zero. Feed loss.

**Fault 7 vs Fault 8** (both cause oscillation in feed-related sensors)
- Fault 7: Appeared transient in our observed window.
- Fault 8: Appeared persistent, not stabilizing in our observed window.

---

## 7. LLM Integration Guide

### Recommended LLM Prompt Structure

```
You are a chemical process assistant for the Tennessee Eastman Process.
An anomaly has been detected. Based on the sensor readings and reference
document below, identify the most likely fault and provide recommendations.
Note that reference ranges are based on limited EDA and should be treated
as approximate patterns, not exact thresholds.

CURRENT ANOMALY:
- Triggered sensors: [list sensors and deviation from normal]
- Pattern observed: [describe pattern: spike/oscillation/drop/step]

FAULT REFERENCE:
[Insert relevant sections from this document]

Respond with:
1. Most likely fault type and confidence level
2. Root cause explanation in plain language
3. Recommended actions
4. Severity level (Low/Medium/High/Critical)
```

### Example LLM Output (Fault 14)

```
ANOMALY DETECTED — Pattern consistent with Fault 14 (Reactor CW Valve Stuck)

Triggered sensors:
- xmeas_9 (Reactor Temperature): oscillating roughly 120.0-120.8 deg C (normal: 120.31-120.49)
- xmeas_21 (Reactor CW Outlet Temp): oscillating roughly 92-97 deg C (normal: 93.979-95.227)

Root cause: Reactor cooling water control valve may be mechanically stuck,
preventing the control loop from regulating reactor temperature.

Recommended actions:
1. Inspect reactor cooling water valve (xmv_10) for mechanical failure
2. Check valve actuator and positioner
3. Monitor reactor temperature closely

Severity: HIGH
```

---

## 8. Model Training Notes for ML Engineer

### Data Split Recommendation
- For anomaly detection, train primarily on normal data (FaultFree_Training).
- Faulty data should be used for validation, threshold tuning, and fault classification — not as the primary training signal for the anomaly detector itself.
- Note: fault introduced at sample 160 in the testing set, sample 20 in the training set.

### Preprocessing Notes
- xmeas_9 normal range is extremely narrow (about 0.18 deg C). Normalize carefully so this signal is not lost.
- xmeas_1 has a relatively wide normal range (0.123-0.390). Fault 1 pushes it well above this range.
- Composition sensors (xmeas_23~41) have not been validated in our own EDA yet — verify before relying on them.
- xmv variables are control outputs. Recommend including them as features since they reveal compensatory behavior (see Fault 4, 11).

### Recommended Model Approach
- Stage 1: Anomaly detection (normal vs abnormal) — Isolation Forest or Autoencoder
- Stage 2: Fault classification (which fault) — Random Forest or LSTM
- Stage 3: LLM explanation generation, using this document as reference context

### General Guidance
- Favor pattern-based detection (oscillation, trend direction, amplitude change) over fixed numeric thresholds, since our reference ranges come from a single simulation run.
- Faults 2, 7, and 13 appeared harder to detect confidently in our EDA and may need additional validation across multiple simulation runs.