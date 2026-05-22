# Learned schedule policy, extensions, and summer roadmap

**Project:** Latency-bounded iterative approximate pipeline  
**Repository:** `Latency-Bounded-Scheduling-For-Iterative-Approximate-Pipeline`  
**Status:** Planning / documentation (RTL not yet in repo)  
**Last updated:** 2026-05-21  

---

## 1. Executive summary

**Hardware core:** Fixed-point pipeline **multiply → iterative normalize → accumulate**, per-job deadline **`L`**, refinement cap **`k_max`** on Station B.

**Full research scope** = core + four extensions (**Ext-A … Ext-D**). Canonical spec: [`02_RESEARCH_EXTENSIONS_ABCD.md`](02_RESEARCH_EXTENSIONS_ABCD.md).

| Extension | Role |
|-----------|------|
| **Ext-A** | RTL + measured latencies; ROM from exhaustive/**ILP** oracle |
| **Ext-B** | **Early-stop** in B under **`k_max`** (main algorithmic add-on) |
| **Ext-C** | **This file’s focus:** learned/compressed ROM vs gold |
| **Ext-D** | SVA **`cycles ≤ L`** on scheduled completion |

Ext-C does **not** replace Station B; it only changes how **`schedule*.hex`** is produced.

---

## 2. Architecture

| Block | Module | Role |
|-------|--------|------|
| Station A | `stage_mul` | Fixed-latency multiply |
| Station B | `stage_norm_iter` | Iterative normalize; **`k_max`** cap; **Ext-B** early-stop |
| Station C | `stage_acc` | Fixed-latency accumulate |
| Manager | `sched_rom` + `pipeline_ctrl` | ROM → **`k_max`** (and optional **ε**); cycle counter |

**Worst-case cycle budget:**

```text
cycles_worst = TA + k_max * TB_per_iter + TC
cycles_worst ≤ L
```

**Actual cycles (Ext-B):**

```text
cycles_actual = TA + i_done * TB_per_iter + TC
i_done ≤ k_max
```

---

## 3. Ext-C — Learned schedule policy

### 3.1 Why learned scheduling (within full project)

| Approach | Role in full project |
|--------|----------------------|
| **Gold ROM (Ext-A)** | Oracle labels; required baseline |
| **Early-stop (Ext-B)** | Primary hardware novelty |
| **Learned ROM (Ext-C)** | Storage/compression study vs gold |
| **NN replaces divide** | **Out of scope** |

**Credibility rule:** Learned policy must be compared to **ILP/exhaustive gold** from Ext-A, not standalone.

### 3.2 Offline pipeline (Python)

1. Characterize Station B: error vs **`k`** (`characterize_b.py`).
2. Gold labels **`k*`** per `(L_bucket, class)` — `build_schedule.py` + cross-check `ilp_schedule.py`.
3. Features: `L_bucket`, `class_id`, optional divisor magnitude / ill-conditioned flag.
4. Train **decision tree** or **logistic** (`train_schedule.py`).
5. Export **`data/schedule_learned.hex`** (same layout as gold).
6. Optional: shallow tree in `rtl/sched_tree.sv` if time.

### 3.3 Evaluation (Ext-C)

| Metric | vs |
|--------|-----|
| Deadline miss rate | Must be **0%** on feasible rows |
| **`k` match rate** | Gold **`k*** |
| Mean / max error gap | Gold-scheduled runs |
| ROM / model size | Full `schedule.hex` |

**Ablations:** remove Ext-B from sweep (fixed-**k** only) when isolating learned **`k`** choice.

---

## 4. Summer roadmap (build phases 1–9)

Assumes full-time summer; adjust if part-time.

| Phase | Duration | Extension | Deliverable |
|-------|----------|-----------|-------------|
| **1** | ~1–2 wk | — | `stage_norm_iter` (fixed **k**), unit TB, golden |
| **2** | ~0.5–1 wk | — | `stage_mul`, `stage_acc` |
| **3** | ~1 wk | Ext-A start | `pipeline_ctrl`, `top_iter_pipeline`, cycle counter |
| **4** | ~1 wk | **Ext-A** | `build_schedule.py`, `ilp_schedule.py`, `schedule.hex`, 0% misses |
| **5** | ~3–5 d | **Ext-A** | Sweeps, error vs **L**, `RESULTS.md` draft |
| **6** | ~1–1.5 wk | **Ext-B** | Early-stop in B, cycles vs error plot |
| **7** | ~1–2 wk | **Ext-C** | `train_schedule.py`, ablation table |
| **8** | ~0.5–1 wk | **Ext-D** | `deadline_props.sv`, `make test`, CI |
| **9** | optional | — | FPGA UART demo |

**Minimum before Ext-C:** Phases 1–5 (gold ROM + measurements).  
**Do not skip Ext-A** to train learned schedule — no oracle without gold table.

---

## 5. Repository layout (target)

```text
rtl/
  stage_mul.sv, stage_norm_iter.sv, stage_acc.sv
  sched_rom.sv, sched_addr_gen.sv, pipeline_ctrl.sv
  top_iter_pipeline.sv, csr_regs.sv
  assertions/deadline_props.sv
tb/
  tb_top.sv, scoreboard.sv
sw/
  golden_model.py, characterize_b.py
  build_schedule.py, ilp_schedule.py
  train_schedule.py, plot_results.py
data/
  schedule.hex, schedule_learned.hex, timing.json
results/
docs/
  02_RESEARCH_EXTENSIONS_ABCD.md, RESULTS.md
Makefile
.github/workflows/ci.yml
```

---

## 6. Resume / report bullets (after measurement)

**Core + Ext-A:**

> Cycle-accurate SystemVerilog pipeline with table-driven iteration budgeting under per-job cap **L**; ROM matches ILP/exhaustive oracle on A→B→C graph; **100%** deadline compliance on scheduled runs.

**Ext-B (add if implemented):**

> Deadline-aware early-stop in iterative normalize stage: **i_done ≤ k_max**, reduced mean cycles vs fixed-**k** at same **L**.

**Ext-C (add if implemented):**

> Learned schedule compressed ROM vs gold: **N%** **k** match, **E%** mean error gap, **B** bytes saved.

**Ext-D (add if implemented):**

> SVA proof obligation **`cycle_count ≤ L`** at job completion for scheduled policies.

---

## 7. Using AI coding assistants

| Appropriate | You must own |
|-------------|----------------|
| Makefile / Verilator scaffolding | **TA/TB/TC**, fixed-point format |
| `ilp_schedule.py`, `train_schedule.py` skeletons | Label definition, oracle agreement |
| Plot scripts | Figure interpretation, all reported numbers |

---

## 8. Related docs

| File | Contents |
|------|----------|
| `02_RESEARCH_EXTENSIONS_ABCD.md` | Full Ext-A…D spec + holistic evaluation matrix |
| `01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md` | Step-by-step implementation |
| `iterative_approximate_dag_diagram.md` | Signals, FSM, SVA notes |
| `00_START_HERE_READ_THESE_FOUR_DOCS.md` | Doc index |

---

*RTL pipeline + Ext-A oracle + Ext-B early-stop + Ext-C learned ROM + Ext-D formal check = agreed full project scope.*
