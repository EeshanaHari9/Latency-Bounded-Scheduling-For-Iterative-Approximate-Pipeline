# Fixed approximation tier — stage-wise error vs energy budgeting

## Research question

Given a **single user-specified approximation level** (not free per-operator precision search), can a compiler or runtime **minimize energy** by **allocating where error is allowed across pipeline stages** while meeting a quality target—especially for iterative or multi-stage modern applications?

## Gap (not already solved as stated)

Joint precision HLS (Li, Reis) searches bit-widths; MIPAC adapts iterations to inputs. Neither fixes one global tier then optimizes **stage-wise error placement vs energy**—the anchor your professor suggested.

## Why this fits your project

Bridges your golden-model / fixed-point mindset with a clear optimization story (energy + error under one knob) and strong 2025 mixed-precision evidence.

## Context papers (target 3–8)

- ✓ Efficient Approximate Logic Synthesis with Dual-Phase Iterative Framework (DATE_2025)
- ✓ Segment-Wise Accumulation: Low-Error Logarithmic Domain Computing for Efficient Large Language Model Inference (DATE_2025)
- ○ ApproxGNN: A Pretrained GNN for Parameter Prediction in Design Space Exploration for Approximate Computing (ICCAD_2025)
- ✓ PAR-CIM: A Precise/Approximate Reconfigurable Digital CIM Macro with 0.35-4b Fractional Mixed-Bitwidth Quantization (ICCAD_2025)
- ○ Early Termination with Activation Sign Prediction for Energy-Efficient CNN Inference Using Sum-of-Power-of-Two Quantization (ICCD_2025)
- ✓ Panacea: Novel DNN Accelerator using Accuracy-Preserving Asymmetric Quantization and Energy-Saving Bit-Slice Sparsity (HPCA_2025)
- ○ li2015_joint_precision_optimization_approximate_hls_dac.pdf
- ○ reis2017_approximate_hls_ahls_date.pdf

Linked PDFs point to `references/conferences/`. Stubs include UW Library / IEEE search URLs.
