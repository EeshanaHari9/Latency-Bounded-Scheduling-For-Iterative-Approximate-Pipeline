# Latency-bounded approximation orchestration on reconfigurable fabric

## Research question

When both a **fixed latency deadline** and a **global approximation level** are given, how should a runtime **reschedule** which tasks run in precise vs approximate modes on shared FPGA/CGRA fabric serving modern multi-DNN, edge, or LLM workloads?

## Gap (not already solved as stated)

Multi-DNN schedulers (TaiChi, RankMap) and accelerator schedulers (SoMa, PAISE) optimize throughput or memory—not **deadline-feasible rescheduling under a fixed approximation tier**. Iterative schedulers (Behroozi) lack reconfigurable remapping for modern serving workloads.

## Why this fits your project

Connects your systems interest (scheduling, real-time) with hardware you can prototype (FPGA) and papers you already collected (DATE + HPCA scheduling cluster).

## Context papers (target 3–8)

- ✓ TaiChi: Efficient Execution for Multi-DNNs Using Graph-Based Scheduling (DATE_2025)
- ✓ RankMap: Priority-Aware Multi-DNN Manager for Heterogeneous Embedded Devices (DATE_2025)
- ✓ Power- and Deadline-Aware Dynamic Inference on Intermittent Computing Systems (DATE_2025)
- ✓ SoMa: Identifying, Exploring, and Understanding the DRAM Communication Scheduling Space for DNN Accelerators (HPCA_2025)
- ✓ PAISE: PIM-Accelerated Inference Scheduling Engine for Transformer-based LLM (HPCA_2025)
- ✓ Adyna: Accelerating Dynamic Neural Networks with Adaptive Scheduling (HPCA_2025)
- ○ R2T-Tiny: Runtime-Reconfigurable Throughput-Optimized TinyML for Hybrid Inference (ICCAD_2025)
- ○ behroozi2021_iterative_hardware_scheduling_isvlsi.pdf
- ○ a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf

Linked PDFs point to `references/conferences/`. Stubs include UW Library / IEEE search URLs.
