# Research extensions A–D (full project scope)

**Project:** Latency-bounded iterative approximate pipeline  
**Last updated:** 2026-05-21  

This document defines the **four extensions** that turn the base pipeline into an **add-on research project** (not a claim that scheduling iterative hardware is new). Pipeline stages are still **Station A / B / C**; extensions are labeled **Ext-A … Ext-D** below.

---

## Positioning (read once)

| Layer | What it is |
|-------|------------|
| **Prior work** | Scheduling iteration/latency for iterative approximate units under a total latency budget (e.g. Behroozi et al., ISVLSI 2021 — ILP on an application DAG). |
| **Base pipeline** | Fixed-point RTL chain **A → B → C**, per-job deadline **`L`**, discrete **`k`** on Station B, ROM table from offline search. |
| **This repo (full scope)** | Base pipeline **plus Ext-A … Ext-D**: measured RTL validation, early-stop, compressed learned schedule, formal deadline property. |

**Contribution in one line:** A **cycle-accurate hardware instance** of deadline-aware iteration budgeting, with **runtime early termination**, **compressed scheduling**, and **verified deadline compliance**—evaluated against an **ILP/exhaustive oracle** on the same three-node graph.

---

## Extension summary

| ID | Name | What you build | Proves |
|----|------|----------------|--------|
| **Ext-A** | Hardware + oracle validation | RTL with measured **`TA` / `TB_per_iter` / `TC`**; `build_schedule.py` + **`ilp_schedule.py`** on graph A→B→C; ROM **`schedule.hex`** | Scheduled jobs: **0% deadline miss**; ROM **`k`** matches exhaustive/ILP **`k*`** |
| **Ext-B** | Deadline-aware early-stop | Station B: **`k`** = max iterations; exit when **`|residual| < ε`**; optional ROM fields **`ε_bucket`** or fixed ε | At same **`L`**, **≤ cycles** and often **lower error** than fixed-**k** at same cap |
| **Ext-C** | Compressed learned schedule | `train_schedule.py` → **`schedule_learned.hex`** (or shallow tree); ablation vs gold ROM | **Match rate** on **`k*`**, **mean error gap**, **ROM bytes** vs full table |
| **Ext-D** | Formal deadline guarantee | SVA: on **`out_valid`**, **`cycle_count_seen ≤ csr_deadline_L`** for scheduled policies | Property holds in sim; documented counterexample if policy violates (e.g. always-max-**k**) |

**Dependency order:** Core RTL → **Ext-A** → **Ext-B** → **Ext-C** → **Ext-D** (D can start once FSM + counter exist; C needs gold table from A).

---

## Ext-A — Hardware realization + ILP/exhaustive oracle

### Goal

Show the **same scheduling problem** as published DAG/ILP work, but with **measured cycle budgets** in RTL and a **reproducible oracle** in software.

### Software

| Script | Role |
|--------|------|
| `sw/golden_model.py` | High-precision reference for error |
| `sw/build_schedule.py` | Exhaustive **`k*`** per `(L_bucket, class)` s.t. `TA + k·TB + TC ≤ L` |
| `sw/ilp_schedule.py` | Tiny ILP for chain A→B→C (same labels as exhaustive); report **agreement %** |
| `sw/characterize_b.py` | Error vs **`k`** grid for Station B |

### Hardware

- Parameters **`TA`, `TB_per_iter`, `TC`** measured from simulation (document in `docs/RESULTS.md` or `data/timing.json`).
- **`sched_rom`**: `$readmemh("data/schedule.hex")`.
- Testbench asserts **`cycle_count_seen ≤ L`** on every scheduled job.

### Exit criteria

- [ ] `ilp_schedule.py` vs `build_schedule.py`: **100%** agreement on `(L_bucket, class)` rows (or documented exceptions).
- [ ] Verilator regression: **0** deadline misses for ROM-driven runs.
- [ ] `data/timing.json` committed with measured latencies.

---

## Ext-B — Early-stop under iteration cap

### Semantics

- Scheduler outputs **`k_max`** (maximum refinement steps allowed).
- Station B runs iterations **`i = 0 … k_max−1`**, but may assert **`b_done` early** when residual below **`ε`**.
- **Worst-case** cycles still bounded: `TA + k_max × TB_per_iter + TC ≤ L` (offline table only stores feasible **`k_max`**).
- **Actual** cycles: `TA + i_done × TB_per_iter + TC` with **`i_done ≤ k_max`**.

### RTL (`stage_norm_iter`)

| Signal / param | Role |
|----------------|------|
| `k_max` | From ROM (same field as **`k`** in fixed-**k** mode, reinterpreted as cap) |
| `epsilon` | CSR or ROM bucket (fixed-point threshold on residual) |
| `iter_count_out` | Expose iterations used (for plots) |
| `early_stop` | Status bit: finished before **`k_max`** |

### Offline

- Extend `build_schedule.py` (or `build_schedule_earlystop.py`) to label **`(k_max, ε)`** or fix ε globally first (v1: **fixed ε**, schedule only **`k_max`**).
- Golden model must model early-stop identically.

### Evaluation (required)

- Plot: **mean final error** and **mean cycles** vs **`L`**.
- Curves: fixed-**k** scheduled, **early-stop** scheduled, always-min-**k**, always-max-**k**.
- Table: **cycles saved (%)** at same **`L`** without increasing misses.

### Exit criteria

- [ ] Early-stop never uses more iterations than **`k_max`**.
- [ ] Scheduled early-stop: **0%** deadline misses.
- [ ] At least one **`L`** bucket where early-stop **beats** fixed-**k** on error or cycles.

---

## Ext-C — Compressed learned schedule

### Goal

**Compress** the gold ROM while staying near optimal; **not** the primary novelty (Ext-B leads).

### Flow

1. Gold labels from Ext-A (`build_schedule.py`).
2. Features: `L_bucket`, `class_id`, optional divisor magnitude / ill-conditioned flag.
3. Train **decision tree** or **logistic** (`train_schedule.py`).
4. Export **`data/schedule_learned.hex`** (same ROM layout as gold).
5. Optional v2: export comparators to `rtl/sched_tree.sv` (only if time).

### Metrics (fill in `RESULTS.md`)

| Metric | Definition |
|--------|------------|
| **`k` match rate** | % jobs where learned **`k` == k*** |
| **Mean error gap** | vs gold-scheduled runs |
| **ROM size** | bytes: full table vs learned table (or tree depth) |
| **Miss rate** | Must stay **0%** for learned schedule on feasible rows |

### Exit criteria

- [ ] Learned schedule: **0%** deadline misses on test sweep.
- [ ] Documented tradeoff: e.g. **≥90%** `k` match and **&lt;X%** mean error increase vs gold (targets TBD after sim).

---

## Ext-D — Formal deadline property

### Property (SVA sketch)

```systemverilog
// Scheduled policies: when job completes, cycles must not exceed L.
property p_deadline_met;
  @(posedge clk) disable iff (!rst_n)
    out_valid |-> (cycle_count_seen <= csr_deadline_L);
endproperty
assert property (p_deadline_met);
```

### Scope

- **Bind** to `top_iter_pipeline` or include in `tb/tb_top.sv`.
- Run with Verilator (SVA subset) or commercial sim if available.
- **Expect failure** when TB forces always-max-**k** beyond **`L`** (sanity check).

### Optional extensions

- `busy |-> cycle_count_seen <= L` (monotonic in-job guard).
- FSM cover: FETCH_K → RUN_A → RUN_B → RUN_C → DONE.

### Exit criteria

- [ ] Assert passes for **ROM-scheduled** and **learned-scheduled** regressions.
- [ ] One **negative test** documented (max-**k** violates **`L`**).

---

## Holistic evaluation matrix

All policies should appear in sweeps where applicable:

| Policy | Ext-A | Ext-B | Ext-C | Ext-D |
|--------|-------|-------|-------|-------|
| Always min-**k** | baseline | baseline | — | expect pass |
| Always max-**k** | baseline | baseline | — | expect **fail** |
| Gold ROM (fixed **k**) | primary | compare | oracle | pass |
| Gold ROM + early-stop | — | primary | — | pass |
| Learned ROM | — | optional | primary | pass |

### Figures to produce (`results/plots/`)

1. **Error vs `L`** — all policies (flagship).
2. **Cycles vs `L`** — early-stop vs fixed-**k** (Ext-B).
3. **ROM size / match rate** — learned vs gold (Ext-C).
4. **ILP vs exhaustive agreement** — bar or table (Ext-A).

---

## Repository layout (full scope)

```text
rtl/
  stage_mul.sv, stage_norm_iter.sv   # B: early-stop + k_max
  stage_acc.sv, sched_rom.sv, sched_addr_gen.sv
  pipeline_ctrl.sv, csr_regs.sv, top_iter_pipeline.sv
  assertions/deadline_props.sv       # Ext-D (or in tb)
tb/
  tb_top.sv, scoreboard.sv
sw/
  golden_model.py, characterize_b.py
  build_schedule.py, ilp_schedule.py    # Ext-A
  build_schedule_earlystop.py           # Ext-B (optional separate)
  train_schedule.py, plot_results.py
data/
  schedule.hex, schedule_learned.hex, timing.json
results/
  sweeps/*.csv, plots/*.png
docs/
  RESULTS.md
Makefile                             # targets: sim, test, schedule, ilp, train, plot
```

---

## Summer build order (implementation)

| Week block | Work |
|------------|------|
| 1–2 | Station B (fixed **k**), then A, C; golden + unit TBs |
| 2–3 | Top FSM, cycle counter, sched ROM — **Ext-A** complete |
| 3 | Sweeps, `ilp_schedule.py`, flagship error plot, `RESULTS.md` draft |
| 4 | **Ext-B** early-stop in B + cycles plot |
| 5 | **Ext-C** train + learned hex + ablation table |
| 5–6 | **Ext-D** SVA + CI `make test` |

FPGA demo remains **optional**; not required for A–D.

---

## Publication target: DAC (64th, 2027)

**Conference:** [DAC](https://dac.com) — Design Automation Conference · **DAC 2027** in San Jose (~July 2027).  
**Research track:** Up to **6 pages + 1 page references only**; double-blind; original unpublished work.  
**Expected submission window (follow [dac.com](https://dac.com) when posted):** ~**November 2026** (abstract ~1 week before full PDF), based on the DAC 2026 cycle (Nov 2025 submit → DAC 2026).

### Timeline aligned with your plan

| When | Work |
|------|------|
| **Summer 2026** | Implement Ext-A…D; fill `RESULTS.md` with numbers and plots |
| **Sep–Oct 2026** | Paper outline, figures, related work (Behroozi ISVLSI 2021 + AHLS/DAC approximate scheduling line) |
| **~Nov 2026** | DAC 2027 research manuscript + abstract submit |
| **Jul 2027** | Presentation if accepted |

### How to frame for DAC reviewers

DAC cares about **design automation**, not only RTL. Lead with:

1. **Problem:** Co-optimizing **iteration latency** and **output quality** under a **hard cycle budget** in approximate datapaths (common in HLS and custom accelerators).
2. **Method:** Oracle scheduling (ILP/exhaustive on A→B→C) + **cycle-accurate RTL** + **early-stop under cap** + optional **compressed schedule** + **checked deadline property**.
3. **Results:** Pareto-style **error vs `L`**, **cycles saved** (Ext-B), **storage vs accuracy** (Ext-C), comparison to **fixed-k** and **always-max-k** baselines.

**Position vs prior work:** Extend iterative-hardware scheduling (Behroozi et al.) with a **verified hardware instance**, **runtime early termination**, and **formal deadline compliance**—not a new abstract scheduler alone.

### What to strengthen for a competitive DAC submission

| Gap for DAC | Mitigation |
|-------------|------------|
| Single 3-node chain feels small | Add **second case study** (e.g. small FIR tap or PoE-style chain from Behroozi paper) using same flow |
| No HLS comparison | Cite AHLS / variable-cycle HLS papers; optional: generate one schedule from open-source HLS or hand-map to your ILP |
| Energy not measured | Add **cycle-count × activity** proxy or FPGA power sample on scheduled vs max-k |
| Learned schedule weak alone | Keep Ext-C as **compression** subsection; headline **Ext-B + Ext-A** |
| Reproducibility | Public repo + `make reproduce` before submit |

### If DAC desk-rejects or TPC pass is tight

Backup same story: **DATE**, **ASP-DAC**, **ISVLSI** (Behroozi venue), **CASES**—shorter revision cycle, similar audience.

---

## Related docs

| File | Role |
|------|------|
| [`00_START_HERE_READ_THESE_FOUR_DOCS.md`](00_START_HERE_READ_THESE_FOUR_DOCS.md) | Doc index |
| [`01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md`](01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md) | Implementation walkthrough aligned with A–D |
| [`learned_schedule_policy_and_roadmap.md`](learned_schedule_policy_and_roadmap.md) | Ext-C detail + phased roadmap |
| [`iterative_approximate_dag_diagram.md`](iterative_approximate_dag_diagram.md) | Signals for early-stop, ILP, SVA |

---

*Extensions A–D are the agreed full project scope for summer implementation.*
