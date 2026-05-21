# One-page storyboard: deadline-aware scheduling for a 3-stage iterative pipeline

**Theme:** A tiny “factory line” in hardware: three stations in a row, each can run **fast/rough** or **slow/careful**, under a **hard time budget**. This matches research on **iterative approximate arithmetic** and **scheduling** (DAG, latency limit, discrete quality modes).

---

## 1. Cast (what each block is)

| Role | Working name | What it does (plain English) |
|------|----------------|------------------------------|
| **Station A** | `STAGE_MUL` | Multiplies two fixed-point numbers. **Exact** in one shot (fixed latency). |
| **Station B** | `STAGE_NORM` | **Divides** (or normalizes) using an **iterative** method: repeat “improve guess” **k** times. **Larger k** → more accurate, more cycles. This is your main **dial**. |
| **Station C** | `STAGE_ACC` | Adds the result into a running sum (or applies one more exact op). **Exact**, fixed latency. |
| **Manager** | `SCHEDULER` | Before each **job** (or each **segment**), picks **k** for Station B from a **small table** so **total cycles ≤ deadline** and **final error** is minimized under a **simple error model**. |

**Data path (order):** `A → B → C` (no feedback loop in v1).

---

## 2. The “dials” (what you actually configure)

- **Deadline `L`:** Maximum cycles allowed for **one full pass** A→B→C (CSR or static for first version).
- **Modes for Station B:** Only **2–3 choices**, e.g. `k ∈ {2, 4, 6}` iterations (each iteration = fixed cycle cost in your RTL).
- **Offline table:** For each `(deadline bucket, optional input class)` you **precompute** which `k` is best using a script (small search or ILP). Hardware stores **only the answer** (ROM or registers).

**Rule of thumb:** Fewer iterations when the clock is tight; more when you can afford them.

---

## 3. Scene-by-scene flow (one “job”)

1. **Start:** New operands arrive at A; **Scheduler** has already chosen **k** for this segment.
2. **Station A** finishes multiply; result passes to B.
3. **Station B** runs **exactly k** refinement steps (or stops early only if you add that extension later), outputs normalized value.
4. **Station C** accumulates (or finishes the chain).
5. **End:** Assert **total cycle count ≤ L**; record **final output** and **golden** reference from a software model.

---

## 4. What you plot at the end (success looks like)

- **X-axis:** Deadline `L` (tight → loose).  
- **Y-axis:** **Final error** (e.g. vs double-precision reference) or **miss rate** if you use thresholds.  
- **Curves:**  
  - **Naive:** always use **max k** (best quality, may **violate** deadline — mark failures).  
  - **Scheduled:** use **table-chosen k** (meets deadline, **lower** error than always-min-k when `L` is large enough).

**Optional:** Bar chart of **encoding**: which `k` the scheduler picked for each deadline.

---

## 5. Mini glossary (terms you will see)

| Term | Plain meaning |
|------|----------------|
| **RTL** | Text description of digital logic; you simulate it before (optionally) putting it on an FPGA. |
| **Fixed-point** | Numbers as integers with an agreed **binary point** (no floating hardware required). |
| **Iterative** | Same step repeated; answer gets better each repeat. |
| **DAG** | “Who runs before whom” picture; here a simple **chain** A→B→C. |
| **CSR** | Control/status register: software or testbench sets **deadline** or **mode**. |
| **Golden model** | Trusted answer from **C/Python** math used to score hardware output. |

---

## 6. What you deliver (concrete artifacts)

1. **Simulatable RTL** for A, B (iterative **k**), C, and Scheduler/table interface.  
2. **Testbench** that runs many jobs, sweeps `L`, logs **cycles** and **error**.  
3. **Short report:** 1 figure (plot above) + 1 paragraph linking to **deadline vs quality** tradeoff and **error propagation** (early stages matter).

---

*Storyboard for: iterative approximate DAG scheduling project · RTL simulation (FPGA optional)*

**Related:** Detailed diagrams and module map → [`iterative_approximate_dag_diagram.md`](iterative_approximate_dag_diagram.md)
