# Project documentation — read in this order

This folder documents the **latency-bounded iterative approximate pipeline** and its **four research extensions (Ext-A … Ext-D)**. Start here, then follow the list below.

**Repository:** [Latency-Bounded-Scheduling-For-Iterative-Approximate-Pipeline](https://github.com/EeshanaHari9/Latency-Bounded-Scheduling-For-Iterative-Approximate-Pipeline)

---

## Documents

| # | File | What it is | Who should read it |
|---|------|------------|-------------------|
| **1** | [`01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md`](01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md) | **Main walkthrough.** Problem, vocabulary, blocks, implementation order, metrics—aligned with Ext-A…D. | **Read first** for full detail. |
| **2** | [`02_RESEARCH_EXTENSIONS_ABCD.md`](02_RESEARCH_EXTENSIONS_ABCD.md) | **Extension spec.** Ext-A (RTL + ILP oracle), Ext-B (early-stop), Ext-C (learned ROM), Ext-D (SVA); build order, exit criteria, evaluation matrix. | **Scope and checklist** before coding. |
| **3** | [`iterative_approximate_dag_storyboard.md`](iterative_approximate_dag_storyboard.md) | **One-page storyboard.** Cast, dials, one-job flow, deliverables. | 5-minute overview. |
| **4** | [`iterative_approximate_dag_diagram.md`](iterative_approximate_dag_diagram.md) | **Diagrams.** Mermaid + ASCII; signals for early-stop and formal checks. | While implementing RTL/TB. |
| **5** | [`learned_schedule_policy_and_roadmap.md`](learned_schedule_policy_and_roadmap.md) | **Ext-C detail** + build phases 1–9. | Before `train_schedule.py`. |

---

## Suggested reading path

```text
00_START_HERE (this file)
        │
        ▼
02_RESEARCH_EXTENSIONS_ABCD  ─── scope: what Ext-A…D mean
        │
        ▼
01_PROJECT_WALKTHROUGH  ─── how to build it step by step
        │
        ├──► storyboard (short recap)
        ├──► diagrams (signals + FSM)
        └──► learned policy (Ext-C)
```

---

## What the project is (one paragraph)

A **simulated fixed-point pipeline** (multiply → **iterative** normalize/divide → accumulate) runs each **job** under a cycle deadline **`L`**. A **scheduler** picks refinement depth **`k`** (and, with **Ext-B**, may stop early before the cap). **Ext-A** implements the pipeline in RTL with **measured** stage latencies and proves ROM choices match an **exhaustive/ILP oracle**. **Ext-B** adds **deadline-aware early-stop** in Station B. **Ext-C** adds a **compressed learned schedule** validated against the gold table. **Ext-D** adds a **formal SVA guarantee** that scheduled jobs finish with **`cycles ≤ L`**. Evaluation is simulation-first (FPGA optional).

---

## Status

| Component | Status |
|-----------|--------|
| Architecture + Ext-A…D docs | Complete (this folder) |
| RTL (`rtl/`) | Planned |
| Software (`sw/`) | Planned |
| `docs/RESULTS.md` | After simulation runs |

---

*Index last updated: 2026-05-21*
