# Project documentation — read in this order

This folder contains **four documents** for the **latency-bounded iterative approximate pipeline** project. Start here, then follow the list below.

**Repository:** [Latency-Bounded-Scheduling-For-Iterative-Approximate-Pipeline](https://github.com/EeshanaHari9/Latency-Bounded-Scheduling-For-Iterative-Approximate-Pipeline)

---

## The four documents

| # | File | What it is | Who should read it |
|---|------|------------|-------------------|
| **1** | [`01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md`](01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md) | **Main presentation.** Problem, vocabulary, end-to-end flow, every block broken into sub-blocks, implementation order, software path, learned-schedule extension, key diagrams inline. | **Read this first** for a full walkthrough. |
| **2** | [`iterative_approximate_dag_storyboard.md`](iterative_approximate_dag_storyboard.md) | **One-page storyboard.** Plain-language cast (Station A/B/C + scheduler), dials, one-job flow, target plot, mini glossary. | Quick mental model; good for a 5-minute overview. |
| **3** | [`iterative_approximate_dag_diagram.md`](iterative_approximate_dag_diagram.md) | **Detailed diagrams.** Full Mermaid set (system, signals, scheduler, Station B internals, FSM, sequence, offline flow, timing budget, testbench, ASCII bus picture, RTL file checklist). | Reference while implementing or reviewing architecture. |
| **4** | [`learned_schedule_policy_and_roadmap.md`](learned_schedule_policy_and_roadmap.md) | **Learned schedule + roadmap.** Why ML sits on the scheduler only, offline train/export flow, evaluation tables, phased build plan, repo layout. | After you understand the RTL core; before building phase F (ML). |

---

## Suggested reading path

```text
00_START_HERE (this file)
        │
        ▼
01_PROJECT_WALKTHROUGH  ─── full step-by-step (presentation)
        │
        ├──► 02 storyboard     (short recap)
        ├──► 03 diagrams      (deep reference + all figures)
        └──► 04 learned policy (ML extension + schedule)
```

**For a live presentation:** Use **document 1** as the script; open **document 3** for backup slides (diagrams). Keep **document 2** as the closing “one slide” summary.

---

## What the project is (one paragraph)

A **simulated hardware pipeline** processes each **job** in three stages: **multiply** (fixed time) → **iterative normalize/divide** (variable quality, knob **`k`**) → **accumulate** (fixed time). A **scheduler** picks **`k`** so total clock cycles **`≤ L`** (deadline). Software **precomputes** good **`k`** values (exhaustive search, then optionally a **learned model** validated against that table). Results are **measured** in simulation: error vs deadline, compared to naive policies.

---

## Status

| Component | Status |
|-----------|--------|
| Architecture docs | Complete (this folder) |
| RTL (`rtl/`) | Planned / in progress |
| Software (`sw/`) | Planned |
| Measured results (`RESULTS.md`) | After simulation runs |

---

*Index last updated: 2026-05-19*
