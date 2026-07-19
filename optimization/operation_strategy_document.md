# TEP Fault Operation Strategy Document
## Prepared by: Industrial Engineering
## Based on: fault_scenario_document_v4.md (Chemical Engineering)

**Scope note**: This document extends Section 4 (Recommended actions) of the
fault scenario document from an equipment-inspection view into an operational
decision view. Severity and persistence values are taken directly from the
fault scenario document (Sections 3 and 4) and are not re-derived here.
Cross-checked against v4: all 10 severity levels are unchanged from v3, so the
operational responses below remain valid. v4's statistical validation further
supports the classification of Fault 7 as transient (monitor-only).

---

## 1. Purpose — Why This Document Exists

The fault scenario document answers: *what broke, which sensors react,
and how to inspect the equipment.* That is a **process/equipment view**.

This document adds the next step: *given the fault, how should we operate the
plant?* That is the **industrial engineering (operations) view**.

```
Chemical Engineering            Industrial Engineering   <- this document
"Cooling valve is stuck,        "So what about production?
 inspect the valve"        ->     Stop the line? Slow down?
                                 Maintenance priority?"
```

Two downstream uses:
1. Feeds the LLM prompt so the AI outputs *cause + operational action*.
2. Provides the basis for the dashboard KPI panel (each fault's OEE impact).

---

## 2. Three Basic Operating Rules

All fault responses are classified by three rules, decided by the combination
of Severity and Persistence.

| Rule | Condition | Default operating policy | Reason |
|------|-----------|--------------------------|--------|
| **R1. Immediate stop** | Critical + runaway/safety threat | Stop line, engage safety systems | Safety over production. Stop even at high loss |
| **R2. Monitor only** | Transient (recovers on its own) | No action, monitor + log | Overreaction (needless stop) costs more |
| **R3. Slow / adjust** | Persistent but not dangerous | Slow down / rebalance load + raise maintenance priority | Full stop is excessive. Keep producing while responding |

---

## 3. OEE Linkage

OEE = Availability x Performance x Quality

Each fault degrades a different one of these three. This is the core of the
dashboard KPI panel.

| Fault character | OEE component degraded | Explanation |
|-----------------|------------------------|-------------|
| Line-stop type (e.g. Fault 6) | **Availability** | Equipment stops, uptime drops |
| Slow-down type (e.g. Fault 14) | **Performance** | Runs slower than rated speed |
| Quality-loss type (e.g. Fault 1) | **Quality** | Reaction imbalance raises defects/byproduct |
| Minor/transient (e.g. Fault 7) | Almost none | Self-recovers, negligible KPI impact |

---

## 4. Fault Operation Strategy Table (Core)

| Fault | Fault description | Affected unit | Severity | Persistence | Rule | OEE impact | Operation strategy (IE) |
|-------|-------------------|---------------|----------|-------------|------|------------|-------------------------|
| **6** | A feed loss, reactor pressure runaway | Reactor (Feed) | Critical | Persistent | **R1** | Availability crash | **Consider immediate line stop.** Engage pressure safety systems. A feed line and xmv_3 must be cleared before restart. Rebuild production schedule |
| **1** | A/C feed ratio breakdown, byproduct rises | Reactor (Feed) | High | Persistent | R3 | Quality drop | **Keep producing but downgrade quality management.** Isolate off-spec output, raise priority on A/C ratio controller maintenance |
| **8** | A/B/C simultaneous variation, sustained oscillation | Reactor (Feed) | High | Persistent | R3 | Quality + Performance drop | **Slow-rate operation.** Compound feed problem, lower throughput until stable. Check feed supply quality, inspect mixing system |
| **12** | Separator cooling disturbance, separation efficiency down | Separator (Cooling) | High | Persistent | R3 | Performance drop | **Reduce separator load.** Prepare for downstream stripper queue buildup. Raise priority on separator cooling (xmv_11) maintenance |
| **14** | Reactor cooling valve stuck, temperature oscillation | Reactor (Cooling) | High | Persistent | R3 | Performance drop | **Slow-rate operation + top maintenance priority.** Temperature control unstable, lower load to suppress oscillation. Dispatch maintenance to cooling valve (xmv_10) immediately |
| **2** | Inert B buildup, gradual efficiency loss | Reactor (Feed) | Medium | Persistent (slow) | R3 | Performance slow drop | **Continue normal operation, planned maintenance.** Not urgent. Fold feed composition analysis and purge-rate adjustment into next maintenance cycle |
| **4** | Cooling water temp rise (step), controller compensating | Reactor (Cooling) | Medium | Persistent | R3 | Minor (compensated) | **Increased monitoring + planned maintenance.** Controller is holding for now. Add cooling tower check to planned maintenance, watch for compensation margin exhaustion |
| **11** | Cooling water temp irregular, temperature wandering | Reactor (Cooling) | Medium | Persistent | R3 | Performance small drop | **Increased monitoring.** Control still tracking but unstable. Add cooling water supply/pump check to planned maintenance |
| **13** | Reaction itself slowly degrading (catalyst) | Reactor (Reaction) | Medium | Persistent (worsening) | R3 | Performance progressive drop | **Plan maintenance.** Worsens over time, so schedule catalyst replacement. Monitor growing oscillation amplitude trend |
| **7** | C feed pressure brief spike, self-recovers | Reactor (Feed) | Medium | **Transient** | **R2** | Almost none | **No action, monitor + log.** Self-recovers. Track recurrence frequency only; if repeated, inspect C feed regulator |

---

## 5. Strategy Summary (Grouped by Rule)

**R1 — Immediate stop (1 fault)**
- Fault 6: the only Critical. Pressure runaway threatens safety -> stop line + safety systems

**R2 — Monitor only (1 fault)**
- Fault 7: the only transient fault. Self-recovers, so no overreaction, log only

**R3 — Slow / adjust (8 faults)**
- Quality management: Fault 1 (downgrade quality tier)
- Slow-rate operation: Fault 8, 14 (lower throughput to stabilize)
- Load rebalancing: Fault 12 (reduce separator load)
- Planned maintenance: Fault 2, 4, 11, 13 (not urgent, fold into maintenance cycle)

