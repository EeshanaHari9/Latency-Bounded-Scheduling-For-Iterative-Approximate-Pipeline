# Three research directions (novelty-checked)

This document replaces the earlier “open gap” claims with **narrow, falsifiable problems** and **named closest prior art**. None of these are guaranteed novel until you complete a full related-work table and your advisor agrees—but each survives a first-pass literature check better than the original Q1–Q3 folders.

**How to read confidence**

| Level | Meaning |
|-------|---------|
| **High** | We did not find a paper that states the same problem with the same constraints; closest work differs on ≥2 axes. |
| **Medium** | Clear positioning vs named papers, but adjacent systems exist; novelty = formulation + evaluation. |
| **Low** | Would need a very tight experimental wedge to publish. |

---

## Direction A — ε-Slack: one approximation knob, stage-wise error–energy allocation

**Confidence: High (problem formulation) / Medium (full system)**

### One-sentence claim

Given a **single scalar approximation level** ε (e.g., fixed-point format or hardware approx tier), a compiler/runtime **allocates error slack across pipeline stages** to **minimize energy** while meeting a **global quality constraint** Q(ε)—without per-operator bit-width search.

### Why this is not “already done”

| Closest work | What they do | How you differ |
|--------------|--------------|----------------|
| **Li et al., DAC 2015** — joint precision optimization + AHLS | Search **different precisions per operator** | You **fix one global ε**; only **where** error may accumulate changes |
| **Reis et al., DATE 2017** — AHLS | Same: multi-precision design space | Same |
| **Capri** (Proactive Control of Approximate Programs) | **Many knobs**; ML learns knob settings | **One knob** ε; allocation is over **stages**, not independent knobs |
| **Cross-layer DACAH** (TVLSI/DAC flow) | Mix **utilization-weighted** circuit accuracies | Hardware mix for fixed workload stats, not **stage DAG + single contract** |
| **MEANTIME** (USENIX ATC 2016) | Governor lowers accuracy to meet **deadline** on CPU | Reactive timing control, not **compile-time stage error budget** under fixed ε |
| **QUSP** (ACM TECS) | Multiple **quality bounds** drive **pruning** | Training-time pruning schedule, not **runtime stage slack** under one ε |

**Professor anchor:** “Given approximation level ε, optimize energy and error” → sharpened to: **error is allocated across stages; energy minimized s.t. Q(ε).**

### Why it fits you

- Matches your **golden-model / fixed-point** work: ε → format; stages → graph nodes; propagate error analytically (no reading PDFs for the core math).
- Publishable artifact: **ε-Slack compiler pass** + energy/error curves on 2–3 pipelines (CNN layer block, iterative normalize, small LLM subgraph).

### Falsify novelty if you find

A paper that takes **one scalar QoS/ε** and solves **stage-level error budgeting** (not per-op precision) with a similar optimization objective.

### Anchor papers (read these)

1. Li et al. — joint precision AHLS (DAC 2015)  
2. Capri — knob control (ASPLOS 2016)  
3. Behroozi & Kim — iterative unit scheduling (ISVLSI / NSF PAR)  
4. **PAR-CIM** (ICCAD 2025) — precise/approx reconfigurable macro  
5. **Segment-Wise Accumulation** (DATE 2025) — stage-wise numeric approximation in LLM path  

### Suggested title

*ε-Slack: Stage-Wise Error Budgeting Under a Fixed Approximation Contract*

---

## Direction B — PipelineFlow: deadline-feasible scheduling for multi-stage iterative approximate pipelines

**Confidence: High**

### One-sentence claim

For a **DAG of iterative approximate stages** (each stage: accuracy improves with iteration count), compute a **latency-feasible schedule** (iterations per stage + ordering) that **minimizes energy** subject to **deadline D** and **end-to-end quality**—extending single-unit schedulers to **pipelines**.

### Why this is not “already done”

| Closest work | What they do | How you differ |
|--------------|--------------|----------------|
| **Behroozi et al.** — ILP scheduling iterative approx hardware | **One** iterative unit; optimal **iteration count** | **Multiple coupled stages** + **pipeline deadline D** |
| **MIPAC** (ASP-DAC 2021) | **Input-aware** iteration count for **one** kernel | No multi-stage DAG, no **hard D** |
| **ApproxIt** (DAC 2014) | Per-iteration **mode** for iterative methods | Software iterative methods, not **hardware pipeline + ILP under D** |
| **ASIS** (ACM TACO 2022) | Anytime interruptible **programs** | General speculation, not **analytic pipeline scheduling** |
| **EXION** (HPCA 2025) | Diffusion **sparsity** across iterations | **Do not pursue** — different mechanism (reuse/sparsity), already published |
| **Ohata et al.** — ILP HLS variable-cycle approx | **Cyclic HLS** under time, min error | Single datapath schedule, not **multi-stage iterative pipeline** |

**This is the cleanest match to your project title:** *Latency-Bounded Scheduling For Iterative Approximate Pipeline.*

### Why it fits you

- You can implement the scheduler in Python (Gurobi/OR-Tools) using **models from your characterization scripts** (energy vs iterations, error vs iterations per stage).
- Evaluation: synthetic pipelines + 1 real chain (e.g., iterative L2-norm → quantized layer → …) using papers you already have (**IterL2Norm**, **De2r**, **Power- and Deadline-Aware** as baselines).

### Falsify novelty if you find

“ILP scheduling of multi-stage iterative approximate pipelines under deadline D” with the same constraints.

### Anchor papers

1. Behroozi et al. — iterative unit scheduling  
2. MIPAC — input-aware iterations  
3. **Power- and Deadline-Aware Dynamic Inference** (DATE 2025)  
4. **TaiChi / RankMap** (DATE 2025) — multi-DNN scheduling (deadline/throughput, not iterative approx)  
5. **SoMa** (HPCA 2025) — accelerator scheduling space  

### Suggested title

*PipelineFlow: ILP Scheduling for Latency-Bounded Iterative Approximate Pipelines*

---

## Direction C — AccelContract: (ε, D) admission and mapping on shared reconfigurable accelerators

**Confidence: Medium**

### One-sentence claim

On a **shared FPGA/CGRA** with **multiple pre-built approximate bitstreams per ε**, an **admission controller** maps incoming jobs to **(ε, deadline D)** contracts by choosing **bitstream + start time + optional preemption (DPR)** to minimize **expected energy** while guaranteeing **no deadline miss**.

### Why this is not “already done”

| Closest work | What they do | How you differ |
|--------------|--------------|----------------|
| **MEANTIME** | **CPU** governor: accuracy ↔ meet deadline | **Accelerator** contracts + **reconfiguration**, not OS governor |
| **Rodriguez-Canal et al.** — preemptive FPGA + DPR | Preemption for **urgency**, not **approximation tier ε** | Add **ε as first-class contract parameter** |
| **TaiChi / RankMap** (DATE 2025) | Multi-DNN **graph scheduling** on edge | Throughput/priority, not **(ε, D) admission** |
| **R2T-Tiny** (ICCAD 2025) | Runtime **reconfigurable throughput** for TinyML | No **multi-tenant deadline contracts** |
| **De2r** (DATE 2025) | DVFS + early-exit **RL** for embedded AI | Learning policy, not **provable admission under (ε, D)** |

### Why it fits you

- Systems + architecture story; can simulate before FPGA using **measured reconfig latency + energy** from literature/constants.
- Harder than A/B in hardware effort—position as **scheduling + simulation** paper first, FPGA case study second.

### Falsify novelty if you find

FPGA admission/scheduling with explicit **(accuracy tier, hard deadline)** contracts and preemptive DPR.

### Anchor papers

1. MEANTIME — deadline + approximate (CPU)  
2. Rodriguez-Canal — preemptive DPR FPGA scheduling  
3. **R2T-Tiny** (ICCAD 2025)  
4. **De2r** (DATE 2025)  
5. **PAISE** (HPCA 2025) — inference scheduling engine  

### Suggested title

*AccelContract: Admission and Rescheduling for Approximate Accelerators under Latency Contracts*

---

## What we rejected (and why)

| Rejected idea | Killer prior art |
|-------------|------------------|
| “Per-iteration quality for diffusion under deadline” | **EXION**, **DeeDiff/AdaDiff**, **Nested Diffusion** (anytime) |
| “Speculative early exit for LLMs” | **SpecEE** (ISCA), **SpecMamba** (ICCAD), many others |
| “Multi-knob ML to tune approximation” | **Capri** |
| “Input-aware iteration count” alone | **MIPAC** |
| “Deadline + approximate” on general CPUs | **MEANTIME** |

---

## Recommendation

| Priority | Direction | For professor | For your skills | Paper weight |
|----------|-----------|---------------|-----------------|--------------|
| **1** | **B — PipelineFlow** | Clear extension of Behroozi to pipelines + deadlines | Scheduling + modeling; aligns with repo name | Strong |
| **2** | **A — ε-Slack** | Directly addresses fixed-ε energy/error | Fixed-point / golden model | Strong |
| **3** | **C — AccelContract** | Modern reconfigurable systems | More systems-heavy | Good if simulated well |

**Do not** pitch EXION-style diffusion sparsity or SpecEE-style early exit as your thesis core—they are crowded.

---

## Next step (1 hour, high value)

For your chosen direction, build a **5-column related-work table** (20 rows):  
*Paper | Fixed global ε? | Deadline? | Multi-stage pipeline? | Reconfigurable HW?*  
If no row has all “yes” for your column pattern, novelty is defensible.
