# Project diagrams: latency-bounded iterative approximate pipeline (detailed)

Use a Markdown viewer with **Mermaid**, or [mermaid.live](https://mermaid.live). **ASCII** sections work in any terminal.

**Notation:** `W` = fixed-point width (e.g. 16 or 24). `k` = iteration count for Station B. `L` = max cycles per end-to-end **job**.

---

## 1. System context (everything on one canvas)

```mermaid
flowchart TB
  subgraph OFF["Offline toolchain"]
    CHAR["Characterize Station B:<br/>error vs k on sample inputs"]
    MODEL["Error model:<br/>e_C ≈ g(e_A, e_B(k))"]
    OPT["Optimizer:<br/>exhaustive search or tiny ILP<br/>per (L_bucket, class)"]
    ART["Artifacts:<br/>schedule.hex, report.json"]
    CHAR --> MODEL
    MODEL --> OPT
    OPT --> ART
  end

  subgraph DUT["RTL design under test"]
    TOP["top_iter_pipeline"]
  end

  subgraph TB["HDL testbench (Verilator / SV)"]
    CLK["clk, rst_n"]
    DRV["Driver:<br/>valid/ready or fixed-rate stimulus"]
    MON["Monitor:<br/>cycle counter, handshake"]
    GOLD["Golden:<br/>double or wide fixed ref"]
    CHK["Scoreboard:<br/>|y - y_ref|,<br/>cycles ≤ L,<br/>k ∈ allowed set"]
    CLK --> TOP
    DRV --> TOP
    TOP --> MON
    MON --> CHK
    GOLD --> CHK
  end

  ART -.->|"$readmemh at t=0"| TOP
```

---

## 2. Top-level RTL blocks and **main signals**

Logical grouping only; your RTL may merge registers differently.

```mermaid
flowchart LR
  subgraph Ports["External / TB facing"]
    rst["rst_n"]
    clk["clk"]
    v_in["job_valid"]
    rdy["job_ready"]
    x["x[W-1:0]"]
    y["y[W-1:0]"]
    z0["acc_init[W-1:0]"]
    cls["segment_class_id"]
    Lcsr["csr_deadline_L"]
    v_out["out_valid"]
    y_out["result[W-1:0]"]
    busy["busy"]
    cyc["cycle_count_seen"]
  end

  subgraph TOP["top_iter_pipeline"]
    REGS["CSR / status regs"]
    SCH["scheduler_lut"]
    CTRL["pipeline_controller_fsm"]
    A["stage_mul"]
    B["stage_norm_iter"]
    C["stage_acc"]
    REGS --> SCH
    REGS --> CTRL
    SCH -->|"k[log2 Kmax:0]"| CTRL
    CTRL --> A
    A -->|"p[W-1:0]"| B
    B -->|"q[W-1:0]"| C
    C --> y_out
    CTRL --> busy
    CTRL --> cyc
  end

  rst & clk & v_in & x & y & z0 & cls & Lcsr --> TOP
  TOP --> v_out & y_out & busy & cyc & job_ready
```

**Suggested semantics**

| Signal | Role |
|--------|------|
| `job_valid` / `job_ready` | One **job** accepted when both high (or use fixed start every N cycles). |
| `x`, `y` | Operands into **Station A** (e.g. multiply inputs). |
| `z0` | Initial accumulator for **Station C** (often 0). |
| `segment_class_id` | Selects **row** in schedule table (e.g. “quiet” vs “busy” input regime). |
| `csr_deadline_L` | Max **total** cycles for A+B+C for this job (or use discrete **bucket** index). |
| `k` | Latency–quality dial for **B** only; comes from LUT output. |
| `cycle_count_seen` | Exposed for TB to assert **≤ L**. |

---

## 3. Scheduler: how the **ROM row** is chosen

```mermaid
flowchart TD
  subgraph Inputs["Inputs each job (or each segment)"]
    Lb["L or L_bucket_id"]
    C["segment_class_id"]
  end

  subgraph IDX["Address formation"]
    ADDR["rom_addr = concat(L_bucket_id, class_id)<br/>or addr = L_bucket * N_CLASS + C"]
  end

  subgraph ROW["One ROM word (example fields)"]
    K["k : 2..Kmax"]
    FLAGS["valid, reserved"]
  end

  subgraph CHECK["Optional runtime guard"]
    TA["cycles_A (const or field)"]
    TB["cycles_B = k * per_iter"]
    TC["cycles_C (const)"]
    SUM["TA + TB + TC"]
    CMP["SUM ≤ L ?"]
  end

  Lb & C --> ADDR
  ADDR --> ROW
  ROW --> K
  K --> TB
  Lb --> CMP
  SUM --> CMP
  CMP -->|"if fail: clamp k or flag error"| CTRL_NOTE["controller / status bit"]
```

**V1 simplification:** Precompute rows only for **feasible** `(L_bucket, class)` so **SUM ≤ L** always holds; ROM then only stores **k**.

---

## 4. Datapath with **pipeline registers** (optional but realistic)

```mermaid
flowchart LR
  subgraph S0["Stage A"]
    MUL["combinational or pipelined<br/>multiply: p = x * y"]
  end

  subgraph R0["Reg R0 (optional)"]
    R0b["hold p[W-1:0]"]
  end

  subgraph S1["Stage B"]
    NORM["iterative norm / div<br/>input: p, implicit divisor<br/>or p as dividend, const divisor"]
  end

  subgraph R1["Reg R1 (optional)"]
    R1b["hold q[W-1:0]"]
  end

  subgraph S2["Stage C"]
    ACC["acc_next = z0 + q<br/>or acc += q"]
  end

  MUL --> R0b --> NORM --> R1b --> ACC
```

**Semantic choice (pick one and stick to it):**  
- **A** outputs **product** `p`; **B** treats `p` as **dividend** and uses **fixed divisor** from CSR for **normalize**, **or**  
- **A** outputs `p = x*y`; **B** computes `q ≈ p / scale` with **iterative reciprocal** of `scale`.

---

## 5. Station B **internal** (iterative refinement datapath)

Example: **multiplicative** normalize using **reciprocal** of normalized divisor `b` (Behroozi / SAADI-flavored).

```mermaid
flowchart TD
  subgraph IN["Inputs"]
    p["p from A (dividend mantissa path)"]
    b["divisor b normalized to [0.5,1)"]
  end

  subgraph NORMREG["Normalize b (leading-one)"]
    LZD["leading-zero detect"]
    SH["barrel shift → b_norm"]
    EXP["exponent diff e_a - e_b (optional)"]
  end

  subgraph INIT["Init"]
    R0["R ← initial guess<br/>(e.g. linear approx)"]
    i["i ← 0"]
  end

  subgraph LOOP["Repeat while i < k"]
    NR["Newton–Raphson style:<br/>R ← R * (2 - b_norm * R)<br/>or Taylor partial on (1-x)"]
    M1["fixed-point mult(s)"]
    iinc["i ← i + 1"]
  end

  subgraph FIN["Finalize"]
    Qhat["q_approx ← p_norm * R<br/>(mult + exp adjust)"]
  end

  p --> FIN
  b --> LZD --> SH --> INIT
  INIT --> LOOP
  LOOP --> M1 --> NR --> iinc
  iinc --> LOOP
  LOOP -->|"i = k"| FIN
```

**RTL detail:** Each **NR** step might be **2–3 cycle pipelined mult**; total **B latency** ≈ `k * (cycles per iteration) + overhead`.

---

## 6. **Top-level controller** FSM (conceptual states)

```mermaid
stateDiagram-v2
  [*] --> IDLE
  IDLE --> FETCH_K : job_valid && job_ready
  FETCH_K --> RUN_A : lut_valid
  RUN_A --> RUN_B : a_done
  RUN_B --> RUN_B : iter < k - 1 / next_iter
  RUN_B --> RUN_C : iter == k - 1 && b_done
  RUN_C --> DONE : c_done
  DONE --> IDLE : out_ack / auto
  FETCH_K --> ERR : rom_invalid
  ERR --> IDLE
```

**Counters to expose to TB:** `cycle_job` cleared on job start; increment every clk; compare to `L` at **DONE**.

---

## 7. **Sequence** diagram: one job, TB vs DUT

```mermaid
sequenceDiagram
  participant TB as Testbench
  participant TOP as top_iter_pipeline
  participant SCH as scheduler_lut
  participant A as stage_mul
  participant B as stage_norm_iter
  participant C as stage_acc

  TB->>TOP: assert job_valid, x,y,z0, class, L
  TOP->>SCH: lookup(L_bucket, class)
  SCH-->>TOP: k
  Note over TOP: cycle_count := 0
  TOP->>A: start multiply
  A-->>TOP: p, a_done
  loop k iterations
    TOP->>B: refine step
    B-->>TOP: partial state
  end
  B-->>TOP: q, b_done
  TOP->>C: accumulate
  C-->>TOP: result, c_done
  TOP-->>TB: out_valid, result, cycle_count
  TB->>TB: assert cycle_count <= L<br/>score vs golden
```

---

## 8. **Offline** flow (what Python does before sim)

```mermaid
flowchart TD
  subgraph P0["0. Characterize"]
    S0["For each k in K_set:<br/>simulate or model B alone"]
    S1["Record max/avg error e_B(k)"]
  end

  subgraph P1["1. Compose"]
    S2["Assume e_A small or zero<br/>(exact A)"]
    S3["Propagate to output:<br/>e_final ≈ h(e_A, e_B(k))"]
  end

  subgraph P2["2. Optimize per row"]
    S4["For each L_bucket, class:<br/>maximize k s.t. TA + k*TB + TC ≤ L<br/>and e_final ≤ budget (optional)"]
    S5["Or minimize e_final subject to latency"]
  end

  subgraph P3["3. Emit"]
    S6["schedule.hex + metadata"]
  end

  S0 --> S1 --> S2 --> S3 --> S4 --> S5 --> S6
```

This mirrors the **paper-style** story: **input-dependent** error is simplified to **per-mode** statistics in student scope.

---

## 9. **Timing budget** (cycles per job)

Replace numbers with your real `TA`, `TB_per_iter`, `TC`, `Kmax`.

**One-line formula:** `cycles_total = TA + k * TB_per_iter + TC` → must satisfy `cycles_total ≤ L`.

**Example bar (conceptual):**

| Segment | Cycles (example) | Notes |
|--------|-------------------|--------|
| A | `TA = 3` | Fixed |
| B | `k × TB_per_iter` e.g. `4 × 3 = 12` | Scales with **k** |
| C | `TC = 3` | Fixed |
| **Sum** | `18` | |
| **Slack** | `L - sum` e.g. `20 - 18 = 2` | Room for FSM overhead if you budget it |

If `L=20`, `TA=3`, `TB_per_iter=3`, `TC=3`: then `k_max = floor((L - TA - TC) / TB_per_iter) = floor(14/3) = 4`. Scheduler picks `k ≤ k_max` for that **L** row.

```mermaid
flowchart LR
  subgraph budget["Cycle budget for one job"]
    A9["A: TA"]
    B9["B: k·TB_per_iter"]
    C9["C: TC"]
    SL["+ FSM overhead"]
  end
  SUM["total cycles"]
  A9 --> SUM
  B9 --> SUM
  C9 --> SUM
  SL --> SUM
  SUM --> CMP9{"≤ L ?"}
```

---

## 10. **Testbench** architecture (detailed)

```mermaid
flowchart TB
  subgraph GEN["Stimulus generator"]
    RND["random x,y in legal range"]
    CLS["pick class_id"]
    LSW["sweep L or L_bucket"]
    FILE["optional: $readmemh vectors"]
  end

  subgraph DUT2["DUT wrapper"]
    DUT["top_iter_pipeline"]
  end

  subgraph REF["Reference path"]
    PYREF["C double / Python via DPI<br/>or precomputed golden file"]
  end

  subgraph SB["Scoreboard"]
    ABS["absolute error |y-y_ref|"]
    REL["optional relative ULP"]
    LAT["cycles ≤ L"]
    KOK["k matches ROM expectation"]
    LOG["CSV: L,k,error,cycles"]
  end

  GEN --> DUT2
  DUT2 --> SB
  REF --> SB
```

---

## 11. Error propagation (toy model you might implement offline)

```mermaid
flowchart LR
  eA["e_A<br/>(A output error)"]
  eB["e_B(k)<br/>(B local)"]
  eC["e_C<br/>(C: often exact)"]

  eA --> COMB["combine:<br/>e.g. quadrature sum<br/>or affine model"]
  eB --> COMB
  COMB --> eF["e_final"]
  eC --> eF
```

**V1:** Treat **A,C exact**; only **e_B(k)** matters for ranking **k**.

---

## 12. ASCII — detailed bus-level picture

```
                         OFFLINE
  +----------+    +-----------+    +----------------------+    +-------------+
  | Sample   |    | Fit e_B(k)|    | For each (L_bkt,cls): |    | schedule.   |
  | inputs   |--->| per stage |--->| choose k (and maybe   |--->| hex + meta  |
  +----------+    +-----------+    | verify TA+k*TB+TC≤L)  |    +------+------+
                                   +----------------------+           |
                                                                        | $readmemh
                         RTL ON CHIP / SIM                             v
  +----------------------------------------------------------------------------------+
  |  csr_deadline_L  segment_class_id   x[W] y[W] z0[W]   job_valid                  |
  |       |                |               |    |    |         |                     |
  |       v                v               v    v    v         v                     |
  |  +---------+     +-----------+    +----------------------------------+           |
  |  | map L to |     | ROM addr  |    | pipeline_controller_fsm         |           |
  |  | L_bucket |---->| decode    |--->| idle/fetch_k/run_a/run_b/run_c  |           |
  |  +---------+     +-----+-----+    +----+-----------+----+----------+             |
  |                        |               |           |    |                        |
  |                        v               | start     |    | done                   |
  |                  +-----v-----+          |           |    |                       |
  |                  | sched_rom |          |           |    |                       |
  |                  | row: k    |----------+           |    |                       |
  |                  +-----------+                      |    |                       |
  |                                                     v    v                       |
  |                                            +--------+----+--------+              |
  |                                            | stage_mul     | TA cycles           |
  |                                            | p = x * y     |                     |
  |                                            +-------+-------+                     |
  |                                                    | p[W]                        |
  |                                                    v                             |
  |                                            +-------+-------+                     |
  |                                            | stage_norm    | k * TB cycles       |
  |                                            | iterative R   |                     |
  |                                            +-------+-------+                     |
  |                                                    | q[W]                        |
  |                                                    v                             |
  |                                            +-------+-------+                     |
  |                                            | stage_acc     | TC cycles           |
  |                                            | out = z0+q    |                     |
  |                                            +-------+-------+                     |
  |                                                    |                             |
  |  job_ready  out_valid  result[W]  cycle_count  status (err,overflow) <---------+
  +----------------------------------------------------------------------------------+
                                        |
  TESTBENCH                             v
  +----------------+    +-----------------------+    +------------------+
  | drive jobs     |    | golden y_ref          |    | CSV / assertions |
  | sweep L, class |--->| (C model or file)     |--->| cycles<=L, error |
  +----------------+    +-----------------------+    +------------------+
```

---

## 13. File / module checklist (implementation map)

| Block | Suggested RTL module | Notes |
|-------|----------------------|--------|
| Schedule storage | `sched_rom.sv` | `$readmemh`; width = `k` + optional flags. |
| Address | `sched_addr_gen.sv` | Concatenate **L_bucket** and **class_id**. |
| FSM | `pipeline_ctrl.sv` | Drives `start_a`, `en_b_iter`, `start_c`, `busy`. |
| Multiply | `stage_mul.sv` | Fixed-point; document **Q format**. |
| Iter norm | `stage_norm_iter.sv` | **k**-bounded loop; internal mult pipeline. |
| Accum | `stage_acc.sv` | Wide enough to avoid overflow for test range. |
| CSR | `csr_regs.sv` | **L**, **class**, **status** (done, err). |
| Top | `top_iter_pipeline.sv` | Tie + parameters `W`, `KMAX`. |

---

## File reference

- Storyboard: `iterative_approximate_dag_storyboard.md`  
- Earlier short diagrams: merged and superseded by this file for detail.
