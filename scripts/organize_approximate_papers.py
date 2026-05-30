#!/usr/bin/env python3
"""Organize reference PDFs into approximate-computing literature folders."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REFS = REPO / "references"
PAPERS = REFS / "DAC(61)" / "papers"

# --- Tier 1: Approximate computing (broad) ---
APPROXIMATE_COMPUTING = [
    # Project core references
    "behroozi2021_iterative_hardware_scheduling_isvlsi.pdf",
    "kemp2021_mipac_iterative_approximate_aspdac.pdf",
    "li2015_joint_precision_optimization_approximate_hls_dac.pdf",
    "ohata2022_ilp_variable_cycle_approximate_hls.pdf",
    "reis2017_approximate_hls_ahls_date.pdf",
    "soni2022_asis_anytime_iterative_approximate_acm_tac.pdf",
    "yao2020_imprecise_computation_dnn_scheduling.pdf",
    "gog2022_d3_dynamic_deadline_driven_eurosys.pdf",
    # DAC'24 — scheduling / HLS / synthesis / anytime
    "a7_Explainable_Fuzzy_Neural_Network_with_Multi-Fidelity_Reinforcement_Learning_for_Micro-.pdf",
    "a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf",
    "a42_MoC_A_Morton-Code-Based_Fine-Grained_Quantization_for_Accelerating_Point_Cloud_Neural.pdf",
    "a52_MERSIT_A_Hardware-Efficient_8-bit_Data_Format_with_Enhanced_Post-Training_Quantization.pdf",
    "a61_Leanor_A_Learning-Based_Accelerator_for_Efficient_Approximate_Nearest_Neighbor_Search_via.pdf",
    "a79_RL-PTQ_RL-based_Mixed_Precision_Quantization_for_Hybrid_Vision_Transformers.pdf",
    "a92_MAFin_Maximizing_Accuracy_in_FinFET_based_Approximated_Real-Time_Computing.pdf",
    "a101_CLUMAP_Clustered_Mapper_for_CGRAs_with_Predication.pdf",
    "a102_MoteNN_Memory_Optimization_via_Fine-grained_Scheduling_for_Deep_Neural_Networks_on_Tiny.pdf",
    "a107_APTQ_Attention-aware_Post-Training_Mixed-Precision_Quantization_for_Large_Language_Models.pdf",
    "a140_Drift_Leveraging_Distribution-based_Dynamic_Precision_Quantization_for_Efficient_Deep_Neural.pdf",
    "a163_RT-MDM_Real-Time_Scheduling_Framework_for_Multi-DNN_on_MCU_Using_External_Memory.pdf",
    "a220_Genetic_Quantization-Aware_Approximation_for_Non-Linear_Operations_in_Transformers.pdf",
    "a230_FQP_A_Fibonacci_Quantization_Processor_with_Multiplication-Free_Computing_and_Topological-.pdf",
    "a259_OPAL_Outlier-Preserved_Microscaling_Quantization_Accelerator_for.pdf",
    "a272_QUQ_Quadruplet_Uniform_Quantization_for_Efficient_Vision.pdf",
    "a278_SAS_-_A_Framework_for_Symmetry-based_Approximate_Synthesis.pdf",
    "a309_Data-driven_HLS_optimization_for_reconfigurable_accelerators.pdf",
    "a311_AdderNet_2.0_Optimal_FPGA_Acceleration_of_AdderNet_with_Activation-Oriented_Quantization.pdf",
    "a317_Bitwise_Adaptive_Early_Termination_in_Hyperdimensional_Computing_Inference.pdf",
    "a336_Ev-Edge_Efficient_Execution_of_Event-based_Vision_Algorithms_on_Commodity_Edge_Platforms.pdf",
    "a351_Late_Breaking_Results_Language-level_QoR_modeling_for_High-Level_Synthesis.pdf",
    "a370_Invited_Achieving_PetaOpsW_Edge-AI_Processing.pdf",
]

# --- Tier 2: AC + modern workloads / rescheduling / reconfigurable HW ---
MODERN_WORKLOADS = [
    "behroozi2021_iterative_hardware_scheduling_isvlsi.pdf",
    "kemp2021_mipac_iterative_approximate_aspdac.pdf",
    "li2015_joint_precision_optimization_approximate_hls_dac.pdf",
    "ohata2022_ilp_variable_cycle_approximate_hls.pdf",
    "reis2017_approximate_hls_ahls_date.pdf",
    "soni2022_asis_anytime_iterative_approximate_acm_tac.pdf",
    "yao2020_imprecise_computation_dnn_scheduling.pdf",
    "gog2022_d3_dynamic_deadline_driven_eurosys.pdf",
    "a7_Explainable_Fuzzy_Neural_Network_with_Multi-Fidelity_Reinforcement_Learning_for_Micro-.pdf",
    "a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf",
    "a92_MAFin_Maximizing_Accuracy_in_FinFET_based_Approximated_Real-Time_Computing.pdf",
    "a101_CLUMAP_Clustered_Mapper_for_CGRAs_with_Predication.pdf",
    "a102_MoteNN_Memory_Optimization_via_Fine-grained_Scheduling_for_Deep_Neural_Networks_on_Tiny.pdf",
    "a107_APTQ_Attention-aware_Post-Training_Mixed-Precision_Quantization_for_Large_Language_Models.pdf",
    "a140_Drift_Leveraging_Distribution-based_Dynamic_Precision_Quantization_for_Efficient_Deep_Neural.pdf",
    "a163_RT-MDM_Real-Time_Scheduling_Framework_for_Multi-DNN_on_MCU_Using_External_Memory.pdf",
    "a220_Genetic_Quantization-Aware_Approximation_for_Non-Linear_Operations_in_Transformers.pdf",
    "a278_SAS_-_A_Framework_for_Symmetry-based_Approximate_Synthesis.pdf",
    "a309_Data-driven_HLS_optimization_for_reconfigurable_accelerators.pdf",
    "a317_Bitwise_Adaptive_Early_Termination_in_Hyperdimensional_Computing_Inference.pdf",
    "a336_Ev-Edge_Efficient_Execution_of_Event-based_Vision_Algorithms_on_Commodity_Edge_Platforms.pdf",
    "a351_Late_Breaking_Results_Language-level_QoR_modeling_for_High-Level_Synthesis.pdf",
    "a370_Invited_Achieving_PetaOpsW_Edge-AI_Processing.pdf",
]

# --- Tier 3: Research question folders (3–5 papers each) ---
RESEARCH_QUESTIONS = {
    "q1_deadline_aware_rescheduling_on_reconfigurable_accelerators": {
        "question": (
            "How can we reschedule approximate compute stages on reconfigurable accelerators "
            "(CGRA/FPGA) under hard per-job latency bounds, when modern streaming workloads "
            "time-multiplex shared fabric?"
        ),
        "gap": (
            "Prior work schedules iterative approximate units (Behroozi) or maps kernels to CGRAs "
            "(PT-Map, CLUMAP), but rarely combines **deadline-aware rescheduling** with "
            "**approximation-aware mapping** on shared reconfigurable hardware for modern DNN/edge "
            "workloads."
        ),
        "papers": [
            "behroozi2021_iterative_hardware_scheduling_isvlsi.pdf",
            "ohata2022_ilp_variable_cycle_approximate_hls.pdf",
            "yao2020_imprecise_computation_dnn_scheduling.pdf",
            "a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf",
            "a101_CLUMAP_Clustered_Mapper_for_CGRAs_with_Predication.pdf",
        ],
    },
    "q2_fixed_approximation_tier_stage_error_energy_allocation": {
        "question": (
            "Given a fixed global approximation level (not per-operator precision search), can a "
            "compiler or scheduler **minimize energy while reallocating error budget across pipeline "
            "stages** for iterative modern applications?"
        ),
        "gap": (
            "Li/Reis optimize precision jointly with HLS; MIPAC tunes iterations at runtime. "
            "Neither fixes a single approximation tier and then optimizes **where error may live** "
            "across stages under energy constraints — closer to your professor's anchor idea."
        ),
        "papers": [
            "li2015_joint_precision_optimization_approximate_hls_dac.pdf",
            "reis2017_approximate_hls_ahls_date.pdf",
            "a92_MAFin_Maximizing_Accuracy_in_FinFET_based_Approximated_Real-Time_Computing.pdf",
            "soni2022_asis_anytime_iterative_approximate_acm_tac.pdf",
            "a7_Explainable_Fuzzy_Neural_Network_with_Multi-Fidelity_Reinforcement_Learning_for_Micro-.pdf",
        ],
    },
    "q3_runtime_workload_aware_remapping_under_quality_constraints": {
        "question": (
            "Can **input- and workload-aware runtime remapping** on reconfigurable platforms beat "
            "static approximate HLS when application behavior shifts (multi-DNN, edge, LLM serving)?"
        ),
        "gap": (
            "Data-driven HLS and multi-DNN schedulers adapt to workloads, and MIPAC adapts accuracy "
            "to inputs — but **coordinated remapping + approximation control** on reconfigurable "
            "hardware for changing modern applications remains largely open."
        ),
        "papers": [
            "kemp2021_mipac_iterative_approximate_aspdac.pdf",
            "a309_Data-driven_HLS_optimization_for_reconfigurable_accelerators.pdf",
            "a102_MoteNN_Memory_Optimization_via_Fine-grained_Scheduling_for_Deep_Neural_Networks_on_Tiny.pdf",
            "a163_RT-MDM_Real-Time_Scheduling_Framework_for_Multi-DNN_on_MCU_Using_External_Memory.pdf",
            "gog2022_d3_dynamic_deadline_driven_eurosys.pdf",
        ],
    },
}


def resolve_pdf(name: str) -> Path:
    direct = REFS / name
    if direct.exists():
        return direct
    matches = list(PAPERS.glob(name[:24] + "*"))
    if len(matches) == 1:
        return matches[0]
    if matches:
        for m in matches:
            if m.name == name:
                return m
        return matches[0]
    raise FileNotFoundError(name)


def link_pdf(src: Path, dest_dir: Path) -> None:
    dest = dest_dir / src.name
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    rel = os.path.relpath(src, dest_dir)
    dest.symlink_to(rel)


def populate(folder: Path, names: list[str]) -> list[str]:
    folder.mkdir(parents=True, exist_ok=True)
    missing = []
    for name in names:
        try:
            link_pdf(resolve_pdf(name), folder)
        except FileNotFoundError:
            missing.append(name)
    return missing


def write_readme(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body}\n")


def main() -> None:
    ac_dir = REFS / "approximate_computing"
    modern_dir = REFS / "approximate_modern_workloads"
    rq_dir = REFS / "research_questions"

    missing_ac = populate(ac_dir, APPROXIMATE_COMPUTING)
    missing_modern = populate(modern_dir, MODERN_WORKLOADS)

    write_readme(
        ac_dir / "README.md",
        "Approximate computing papers",
        "Curated from DAC'24 proceedings split + project references. Includes approximate HLS, "
        "mixed-precision/quantization-as-approximation, anytime/early-termination, imprecise "
        "scheduling, and quality–energy tradeoffs.\n\n"
        f"**Count:** {len(APPROXIMATE_COMPUTING) - len(missing_ac)} papers linked.\n"
        + (f"\n**Missing:** {', '.join(missing_ac)}" if missing_ac else ""),
    )

    write_readme(
        modern_dir / "README.md",
        "Approximate computing × modern workloads / reconfigurable HW",
        "Subset of `approximate_computing/` whose titles or abstracts emphasize **modern workloads "
        "or applications**, **scheduling/rescheduling**, and/or **reconfigurable platforms "
        "(FPGA, CGRA, HLS)** in an approximate or quality–energy context.\n\n"
        f"**Count:** {len(MODERN_WORKLOADS) - len(missing_modern)} papers linked.\n"
        + (f"\n**Missing:** {', '.join(missing_modern)}" if missing_modern else ""),
    )

    rq_missing: dict[str, list[str]] = {}
    for slug, meta in RESEARCH_QUESTIONS.items():
        qdir = rq_dir / slug
        rq_missing[slug] = populate(qdir, meta["papers"])
        paper_list = "\n".join(f"- `{p}`" for p in meta["papers"])
        write_readme(
            qdir / "README.md",
            slug.replace("_", " ").title(),
            f"## Research question\n\n{meta['question']}\n\n"
            f"## Gap (why this is not already solved)\n\n{meta['gap']}\n\n"
            f"## Context papers (3–5)\n\n{paper_list}\n",
        )

    write_readme(
        rq_dir / "README.md",
        "Research question literature folders",
        "Three proposed **open** directions in approximate computing that build on — but do not "
        "duplicate — prior scheduling, HLS, and runtime accuracy-control work. Each subfolder "
        "contains 3–5 linked PDFs for context.\n\n"
        "Review these questions with your professor and refine before treating them as thesis "
        "claims.\n\n"
        + "\n".join(
            f"- `{slug}/` — {meta['question'][:100]}…"
            for slug, meta in RESEARCH_QUESTIONS.items()
        ),
    )

    print("approximate_computing:", len(APPROXIMATE_COMPUTING) - len(missing_ac), "linked")
    print("approximate_modern_workloads:", len(MODERN_WORKLOADS) - len(missing_modern), "linked")
    for slug, miss in rq_missing.items():
        print(f"{slug}:", len(RESEARCH_QUESTIONS[slug]["papers"]) - len(miss), "linked")
    if missing_ac or missing_modern or any(rq_missing.values()):
        print("Missing files:", missing_ac, missing_modern, rq_missing)


if __name__ == "__main__":
    main()
