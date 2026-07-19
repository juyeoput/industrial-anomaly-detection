# TEP Fault Bottleneck Analysis Document
## Prepared by: Industrial Engineering
## Based on: fault_scenario_document_v4.md (Chemical Engineering)

**Scope note**: This is a document-based logical mapping of which process
unit becomes the bottleneck under each fault, derived from v4's fault
category and sensor-response descriptions. Sensor-level data verification
(via unit level/pressure sensors) is left as a follow-up step, mirroring how
v3 (observation) was later validated by v4 (statistics).

---

## 1. What Is Bottleneck Analysis Here

The TEP process flows through five units in series:

```
Feed -> [Reactor] -> [Condenser] -> [Separator] -> [Compressor] -> [Stripper] -> Product
```

Per the Theory of Constraints (TOC), overall throughput is set by the slowest
stage — the bottleneck. In normal TEP operation the design is balanced, so no
single unit is a standing bottleneck. The relevant question for this project is:
**when a fault occurs, which unit becomes the constraint?**

Identifying this matters because the operational response depends on it:
a reactor bottleneck, a separator bottleneck, and a feed constraint each call
for different load-balancing and maintenance decisions.

---

## 2. How the Bottleneck Is Identified (Sensor Basis)

Each unit has level and pressure sensors. Accumulation (rising level or
pressure that will not clear) is direct evidence that flow cannot pass to the
next stage — i.e., that unit is the constraint.

| Unit | Level Sensor | Pressure Sensor | Temperature Sensor |
|------|--------------|-----------------|--------------------|
| Reactor | xmeas_8 | xmeas_7 | xmeas_9 |
| Separator | xmeas_12 | xmeas_13 | xmeas_11 |
| Stripper | xmeas_15 | xmeas_16 | xmeas_18 |

**Note on verification**: The mapping in Section 3 is currently based on which
unit's sensors v4 reports as disturbed. Direct confirmation via the level
sensors above (xmeas_8/12/15 accumulating) is the recommended follow-up.

---

## 3. Fault -> Bottleneck Unit Mapping (Core)

Bottleneck unit inferred from v4 Section 4 (Category) and the unit whose
sensors are reported as disturbed. 'Constraint type' describes how the unit
becomes limiting.

| Fault | Category | Bottleneck Unit | Evidence (from v4) | Constraint Type |
|-------|----------|-----------------|--------------------|-----------------|
| 1 | Feed | Reactor (input side) | xmeas_1/4/7 disturbed; A/C ratio into reactor broken | Input constraint — wrong feed mix starves correct reaction |
| 2 | Feed | Reactor (input side) | Subtle feed shift; inert B builds up in system | Gradual input constraint — inert accumulation reduces effective capacity |
| 4 | Cooling | Reactor | xmv_10 opens wider to hold reactor temp; cooling capacity constrained | Cooling constraint — heat removal limits stable throughput |
| 6 | Feed | Reactor | xmeas_1 drops to ~0, xmeas_7 pressure runaway | Hard constraint — feed loss + pressure buildup, reactor cannot pass flow |
| 7 | Feed | Reactor (input side) | Transient feed pressure disturbance, self-recovers | Temporary constraint — clears on its own, no lasting bottleneck |
| 8 | Feed | Reactor (input side) | xmeas_1/4/7 oscillate together; multi-component feed unstable | Fluctuating input constraint — unstable feed caps sustainable rate |
| 11 | Cooling | Reactor | xmeas_9/xmv_10 variance elevated; temperature control unstable | Cooling constraint (unstable) — irregular heat removal limits steady operation |
| 12 | Cooling | Separator | separator sensors (xmeas_11/22/13) disturbed; reactor stays normal | Downstream constraint — separation efficiency drops, backs up before stripper |
| 13 | Reaction | Reactor | xmeas_7 variance grows over time; reaction rate degrading | Reaction constraint — declining conversion caps output, worsens over time |
| 14 | Cooling | Reactor | xmeas_9/21 strong variance; cooling valve stuck | Cooling constraint — temperature oscillation forces reduced load |

---

## 4. Bottleneck by Location

**Reactor bottleneck (9 of 10 faults):** Fault 1, 2, 4, 6, 7, 8, 11, 13, 14
- The reactor is the most constraint-prone unit — most faults either feed into
  it (feed faults) or affect its temperature control (cooling/reaction faults).
- Operational implication: reactor is the primary unit to protect and to
  prioritize for maintenance. It is the system's dominant constraint point.

**Separator bottleneck (1 of 10 faults):** Fault 12
- The only fault whose constraint sits downstream of the reactor.
- Operational implication: reduce separator load; expect queue buildup before
  the stripper. Reactor can keep running, so a full stop is unnecessary.

**No lasting bottleneck:** Fault 7
- Transient; the constraint clears on its own. Monitor only.

---

## 5. Link to Operation Strategy

The bottleneck unit directly justifies the operation strategy already defined:

| Fault | Bottleneck | Why the chosen operation response follows |
|-------|-----------|-------------------------------------------|
| 6 | Reactor (hard) | Reactor cannot pass flow + pressure runaway -> immediate line stop (R1) |
| 12 | Separator | Constraint is downstream, reactor fine -> reduce separator load, not full stop (R3) |
| 14 | Reactor (cooling) | Reactor throughput limited by unstable cooling -> slow down + prioritize valve maintenance (R3) |
| 7 | None (transient) | No lasting constraint -> monitor only (R2) |

This closes the loop: bottleneck analysis explains *where* the constraint is,
and the operation strategy says *what to do* about it.

---

## 6. Next Work (TODO)

- [ ] Verify bottleneck mapping with actual level sensors (xmeas_8/12/15) on fault data
- [ ] Quantify queue buildup: how fast does the constrained unit's level/pressure rise after fault onset
- [ ] Estimate throughput loss per fault (ties into OEE Performance term)
- [ ] Cross-check with Throughput KPI once TEP data is available