# Learned Schedule Policy

**Project:** Latency-bounded iterative approximate pipeline  
**Repository:** `Latency-Bounded-Scheduling-For-Iterative-Approximate-Pipeline`  
**Status:** Planning / documentation (RTL implementation in progress)  
**Last updated:** 2026-05-19  

---

## 1. Executive summary

The **hardware thesis** stays fixed in RTL: a three-stage fixed-point pipeline (**multiply → iterative normalize → accumulate**) with a **per-job cycle deadline `L`** and discrete iteration count **`k`** on the approximate stage.

The recommended **AI extension** (best for resume + credibility while keeping RTL central):

> **Learned schedule policy** — train a small offline model to predict optimal **`k`** under deadline constraints, then **validate against an exhaustive/ILP-generated gold schedule** (full ROM table).

AI assists **how the ROM is built and evaluated**; it does **not** replace the iterative datapath or the deadline semantics in hardware.

---

## 2. Architecture (unchanged RTL core)

| Block | Module | Role |
|-------|--------|------|
| Station A | `stage_mul` | Fixed-latency multiply |
| Station B | `stage_norm_iter` | Iterative normalize / divide; quality knob **`k`** |
| Station C | `stage_acc` | Fixed-latency accumulate |
| Manager | `sched_rom` + `pipeline_ctrl` | Pick **`k`**, enforce **`cycles ≤ L`** |

**Cycle budget (parameters):**

```text
cycles_total = TA + k * TB_per_iter + TC
cycles_total ≤ L
```

See `iterative_approximate_dag_storyboard.md` and `iterative_approximate_dag_diagram.md` for cast, FSM, and interfaces.

---

## 3. Why learned scheduling

| Option | Resume / credibility | Keep RTL central? |
|--------|----------------------|-------------------|
| **Learned schedule (recommended)** | Gold baseline = optimal table; clear metrics (miss rate, error gap, storage) | **Yes** |
| Classifier for `segment_class_id` only | Weaker alone; use as **feature** for schedule model | Yes |
| Learned early-stop in Station B | Strong but harder to verify; best as **phase 2** | Alters B behavior |
| End-to-end NN replaces divide | **Avoid** — loses SAADI/iterative story | No |

**Credibility rule:** Show learned policy is **close to provably good** labels from exhaustive search or tiny ILP per `(L_bucket, class, features)`.

---

## 4. Learned schedule policy — design

### 4.1 Offline pipeline (Python)

1. **Characterize Station B:** error vs `k` on a grid of operands (fixed-point golden reference).
2. **Label optimal `k*`** for each sample:
   - Maximize quality (minimize final error) subject to `TA + k·TB + TC ≤ L`.
3. **Features** (examples):
   - `L` or `L_bucket_id`
   - `segment_class_id` (optional)
   - Operand stats: divisor magnitude bucket, ill-conditioned flag, exponent diff
4. **Train small model:**
   - Start with **decision tree** or **logistic regression** (interpretable, easy to export).
   - Optional: tiny MLP if tree is insufficient.
5. **Export:**
   - **V1 (minimum):** predictions written to **`schedule.hex`** (same ROM format as exhaustive table).
   - **V2 (optional):** shallow tree exported as **LUT / comparators** in RTL.

### 4.2 Hardware (unchanged interface)

- ROM still outputs **`k`** to `stage_norm_iter`.
- Controller still asserts **`cycle_count ≤ L`** at job completion.
- ML does **not** change A/B/C algorithms in v1.

### 4.3 Evaluation (required for resume)

| Metric | Baseline A | Baseline B | Proposed |
|--------|------------|------------|----------|
| Deadline miss rate | Always max-`k` | Always min-`k` | Learned schedule |
| Mean / max final error | (same) | (same) | vs **optimal table** |
| Config size | Full table | — | Learned model / compressed ROM |

**Flagship figure:** Final error vs **`L`** — three curves: **scheduled (learned or table)**, **always-min-k**, **always-max-k** (mark violations).

**Ablations table:**

- Learned vs **exhaustive optimal** table: % jobs matching `k*`, mean error degradation.
- Optional: ROM entries vs tree depth (storage).

---

## 5. Compressed summer roadmap

Assumes **full-time** work; adjust if part-time.

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **A — Core RTL** | ~1–2 weeks | `stage_mul`, `stage_norm_iter`, `stage_acc`, unit TBs, golden model |
| **B — Integration** | ~1 week | `pipeline_ctrl`, `top_iter_pipeline`, cycle counter |
| **C — Optimal schedule** | ~1 week | `build_schedule.py`, exhaustive labels, ROM, deadline asserts |
| **D — Results** | ~3–5 days | Flagship plot + `RESULTS.md` with numbers |
| **E — CI / hygiene** | ~2–3 days | Verilator `make test`, GitHub Actions |
| **F — Learned policy** | ~1–2 weeks | Train model, ablations vs optimal table |
| **G — Optional wow** | ~2–3 weeks | Pick **one:** FPGA UART demo, early-stop in B, or tree-in-RTL |

**Resume-worthy MVP (no ML):** ~3–4 weeks.  
**Impressive summer version:** MVP + **phase F** (+ optional G).

---

## 6. Repository layout (target)

```text
rtl/                 stage_mul, stage_norm_iter, stage_acc, sched_rom, pipeline_ctrl, top
tb/                  Verilator testbench, scoreboard
sw/                  golden_model.py, build_schedule.py, train_schedule.py, plot_results.py
data/                schedule.hex, schedule_learned.hex, test_vectors/
results/             sweeps/*.csv, plots/*.png
docs/                storyboard, diagram, this file, RESULTS.md
Makefile             sim, test, schedule, train, plot
.github/workflows/   ci.yml
```

---

## 7. Fill after Measurement

**RTL (lead):**

> Implemented deadline-aware fixed-point pipeline in SystemVerilog (multiply → iterative normalize → accumulate) with table-driven iteration budgeting under per-job cycle cap **L**; Verilator regression with **100%** deadline compliance on scheduled runs.

**ML extension (second clause, after phase F):**

> Trained lightweight schedule model to select refinement depth **k**; matched offline-optimal iteration budgets on **N%** of jobs within **E%** mean error vs full lookup table.

**Do not claim** ML on resume until phase F metrics exist.

---

## 8. Using AI coding assistants (ChatGPT, Claude, Cursor)

| Appropriate | You must own |
|-------------|----------------|
| Makefile / Verilator scaffolding | Fixed-point format, **TA/TB/TC** budget |
| Test vector generation, plot scripts | Flagship figure interpretation |
| Debug hints, doc drafts | Architecture and all resume numbers |
| `train_schedule.py` structure | Label definition, comparison to optimal |

---

## 9. Extensions (priority after learned schedule)

1. **Early-stop** in Station B — same `k` cap, exit when residual &lt; ε; compare cycles vs error.
2. **Input class features** — feed classifier output into schedule model.
3. **FPGA demo** — UART print `L, k, cycles, error` (reuse prior UART experience).
4. **SVA** — `cycles ≤ L` at DONE; optional formal on FSM.

**Avoid as primary goal:** full SoC-scale integration, unrelated repos, end-to-end neural divide replacing Station B.

---

## 10. Related docs

| File | Contents |
|------|----------|
| `00_START_HERE_READ_THESE_FOUR_DOCS.md` | Index of all four documents |
| `01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md` | Full step-by-step presentation |
| `iterative_approximate_dag_storyboard.md` | Plain-language cast, dials, deliverables |
| `iterative_approximate_dag_diagram.md` | Mermaid + ASCII architecture |
| `RESULTS.md` | *(create after sim)* measured numbers |

---

*This document captures the agreed direction: RTL pipeline + optimal schedule baseline + learned policy validation
