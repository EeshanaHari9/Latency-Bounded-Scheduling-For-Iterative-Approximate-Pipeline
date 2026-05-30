# Iteration-aware approximate pipelines under deadline

## Research question

For **iterative** modern workloads (diffusion steps, speculative decoding, incremental inference): **which iterations or layers** should run at full vs reduced fidelity so both **deadline** and **error** constraints are met—without re-tuning the whole model?

## Gap (not already solved as stated)

EXION and SpecEE exploit sparsity/early exit per iteration or layer, but do not unify **deadline-bounded scheduling** with a **fixed approximation budget** across an iterative pipeline. ASIS/MIPAC are closest in spirit but pre-LLM/diffusion era.

## Why this fits your project

Most publishable angle for 'iterative approximate pipeline' in the project title—timely, learnable (model + scheduler), and grounded in papers you already downloaded.

## Context papers (target 3–8)

- ✓ EXION: Exploiting Inter- and Intra-Iteration Output Sparsity for Diffusion Models (HPCA_2025)
- ✓ Cocktail: Chunk-Adaptive Mixed-Precision Quantization for Long-Context LLM Inference (DATE_2025)
- ✓ SparseInfer: Training-free Prediction of Activation Sparsity for Fast LLM Inference (DATE_2025)
- ○ SpecEE: Accelerating Large Language Model Inference with Speculative Early Exiting (ISCA_2025)
- ✓ SpecMamba: Accelerating Mamba Inference on FPGA with Speculative Decoding (ICCAD_2025)
- ✓ Diff-DiT: Temporal Differential Accelerator for Low-bit Diffusion Transformers on FPGA (ICCAD_2025)
- ✓ Lincoln: Real-Time 50~100B LLM Inference on Consumer Devices with LPDDR-Interfaced, Compute-Enabled Flash Memory (HPCA_2025)
- ○ soni2022_asis_anytime_iterative_approximate_acm_tac.pdf

Linked PDFs point to `references/conferences/`. Stubs include UW Library / IEEE search URLs.
