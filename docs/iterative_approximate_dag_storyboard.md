# One-page storyboard: deadline-aware scheduling for a 3-stage iterative pipeline

**Theme:** A small hardware “factory line” (stations A → B → C) under a **hard cycle budget** **`L`**, with an **iterative approximate** middle stage whose quality is controlled by **`k`** and optional **early-stop**. Scheduling theory exists in prior work; this project **implements and extends** it in RTL with extensions **Ext-A … Ext-D** (see [`02_RESEARCH_EXTENSIONS_ABCD.md`](02_RESEARCH_EXTENSIONS_ABCD.md)).

---

## 1. Cast (what each block is)

| Role | Working name | What it does (plain English) |
|------|----------------|------------------------------|
| **Station A** | `STAGE_MUL` | Multiplies two fixed-point numbers. **Exact**, fixed latency. |
| **Station B** | `STAGE_NORM` | **Iterative** divide/normalize: up to **`k_max`** refinement steps; **Ext-B** can stop early when residual &lt; **ε**. |
| **Station C** | `STAGE_ACC` | Accumulates (e.g. `z0 + q`). **Exact**, fixed latency. |
| **Manager** | `SCHEDULER` | ROM (or learned ROM) picks **`k_max`** (and optionally **ε**) so **worst-case** cycles **≤ `L`** and error is minimized offline. |

**Data path:** `A → B → C` (chain only in v1).

---

## 2. The “dials”

| Dial | Meaning |
|------|---------|
| **`L`** | Max cycles for one full job (CSR / testbench). |
| **`k` / `k_max`** | Max refinement iterations in B (discrete set, e.g. {2, 4, 6}). |
| **`ε`** | Early-stop threshold on residual (**Ext-B**). |
| **ROM row** | Offline choice per `(L_bucket, class)` — from exhaustive search, ILP (**Ext-A**), or learned table (**Ext-C**). |

**Cycle budget (worst case):** `TA + k_max × TB_per_iter + TC ≤ L`.

**Actual cycles (early-stop):** `TA + i_done × TB_per_iter + TC` with `i_done ≤ k_max`.

---

## 3. One job (runtime)

1. Operands + **`L`** (+ class) arrive; scheduler returns **`k_max`** (and **ε** if used).
2. **A** → **B** (iterate until early-stop or **`k_max`**) → **C**.
3. Testbench: **error** vs golden; **`cycle_count ≤ L`** (**Ext-D** asserts this for scheduled policies).
4. Log **iterations used** for Ext-B plots.

---

## 4. What you plot

| Figure | Extensions |
|--------|------------|
| **Error vs `L`** | All policies (flagship) — Ext-A baselines |
| **Cycles vs `L`** | Fixed-**k** vs early-stop — **Ext-B** |
| **ROM size / `k` match %** | Gold vs learned — **Ext-C** |
| **ILP vs exhaustive agreement** | **Ext-A** |

---

## 5. Four extensions (quick)

| ID | One line |
|----|----------|
| **Ext-A** | RTL + measured **`TA/TB/TC`**; ROM matches **ILP/exhaustive** oracle |
| **Ext-B** | Stop B early under **`k_max`** cap; still **`cycles ≤ L`** |
| **Ext-C** | Learned/compressed ROM vs gold table |
| **Ext-D** | SVA: **`cycle_count ≤ L`** when job completes (scheduled runs) |

---

## 6. Deliverables

1. Simulatable **RTL** + testbench + `make test`  
2. **`sw/`** scripts: golden, schedule, ILP, train, plot  
3. **`data/schedule.hex`**, optional **`schedule_learned.hex`**, **`timing.json`**  
4. **`docs/RESULTS.md`** with tables and plots above  

---

## 7. Research framing (one sentence)

An **extension** of deadline-aware scheduling for **iterative approximate hardware**: **cycle-accurate RTL**, **early-stop under a cap**, **compressed learned policies**, and **formal deadline checks**—validated against an **offline optimal oracle** on a three-node pipeline graph.

---

*Storyboard · RTL simulation (FPGA optional)*

**Related:** [`00_START_HERE_READ_THESE_FOUR_DOCS.md`](00_START_HERE_READ_THESE_FOUR_DOCS.md) · [`01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md`](01_PROJECT_WALKTHROUGH_STEP_BY_STEP.md) · [`02_RESEARCH_EXTENSIONS_ABCD.md`](02_RESEARCH_EXTENSIONS_ABCD.md) · [`iterative_approximate_dag_diagram.md`](iterative_approximate_dag_diagram.md)
