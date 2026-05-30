#!/usr/bin/env python3
"""Build ideas/ literature workspace from 2025 conference catalogs and local PDFs."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REFS = REPO / "references"
IDEAS = REPO / "ideas"
CONF_ROOT = REFS / "conferences"
CONFS = ("DATE_2025", "ISLPED_2025", "ICCAD_2025", "ICCD_2025", "ISCA_2025", "HPCA_2025")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from organize_conference_papers import (  # noqa: E402
    AC_KW,
    MODERN_KW,
    DOWNLOADS,
    build_catalog,
    ezproxy_host,
    paper_publisher_url,
    paper_url_hint,
    proceedings_url_hint,
    slugify,
    uw_patron,
)

DAC61 = REFS / "DAC(61)" / "papers"

# Foundational PDFs (often not in 2025 proceedings); link if present under references/
FOUNDATION = {
    "behroozi2021_iterative_hardware_scheduling_isvlsi.pdf": {
        "title": "Iterative hardware scheduling for approximate computing (ISVLSI 2021)",
        "note": "Behroozi et al. — iterative approximate unit scheduling.",
        "url": "https://ieeexplore.ieee.org/document/9480182",
    },
    "li2015_joint_precision_optimization_approximate_hls_dac.pdf": {
        "title": "Joint precision optimization for approximate HLS (DAC 2015)",
        "note": "Li et al. — precision vs energy in approximate HLS.",
        "url": "https://ieeexplore.ieee.org/document/7167244",
    },
    "reis2017_approximate_hls_ahls_date.pdf": {
        "title": "Approximate HLS (AHLS) (DATE 2017)",
        "note": "Reis et al. — approximate high-level synthesis framework.",
        "url": "https://ieeexplore.ieee.org/document/7927098",
    },
    "soni2022_asis_anytime_iterative_approximate_acm_tac.pdf": {
        "title": "ASIS: Anytime iterative approximate computing (ACM TAC 2022)",
        "note": "Soni et al. — anytime quality under iterative refinement.",
        "url": "https://dl.acm.org/doi/10.1145/3508392",
    },
    "kemp2021_mipac_iterative_approximate_aspdac.pdf": {
        "title": "MIPAC: Iterative approximate computing (ASP-DAC 2021)",
        "note": "Kemp et al. — input-aware accuracy control at runtime.",
        "url": "https://dl.acm.org/doi/10.1145/3394885.3432109",
    },
    "ohata2022_ilp_variable_cycle_approximate_hls.pdf": {
        "title": "ILP variable-cycle approximate HLS",
        "note": "Ohata et al. — timing/approximation in HLS.",
        "url": None,
    },
    "yao2020_imprecise_computation_dnn_scheduling.pdf": {
        "title": "Imprecise computation for DNN scheduling",
        "note": "Yao et al. — scheduling under approximate execution.",
        "url": None,
    },
    "gog2022_d3_dynamic_deadline_driven_eurosys.pdf": {
        "title": "D3: Dynamic deadline-driven scheduling (EuroSys 2022)",
        "note": "Gog et al. — deadlines with dynamic inference.",
        "url": None,
    },
    "a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf": {
        "title": "PT-Map: Program transformation for CGRA (DAC 2024)",
        "note": "CGRA mapping — reconfigurable target.",
        "url": None,
    },
    "a309_Data-driven_HLS_optimization_for_reconfigurable_accelerators.pdf": {
        "title": "Data-driven HLS for reconfigurable accelerators (DAC 2024)",
        "note": "Workload-aware HLS on reconfigurable platforms.",
        "url": None,
    },
}

RESEARCH_QUESTIONS = {
    "q1_latency_bounded_approximation_on_reconfigurable_fabric": {
        "title": "Latency-bounded approximation orchestration on reconfigurable fabric",
        "question": (
            "When both a **fixed latency deadline** and a **global approximation level** are given, "
            "how should a runtime **reschedule** which tasks run in precise vs approximate modes on "
            "shared FPGA/CGRA fabric serving modern multi-DNN, edge, or LLM workloads?"
        ),
        "gap": (
            "Multi-DNN schedulers (TaiChi, RankMap) and accelerator schedulers (SoMa, PAISE) "
            "optimize throughput or memory—not **deadline-feasible rescheduling under a fixed "
            "approximation tier**. Iterative schedulers (Behroozi) lack reconfigurable remapping "
            "for modern serving workloads."
        ),
        "why_you": (
            "Connects your systems interest (scheduling, real-time) with hardware you can prototype "
            "(FPGA) and papers you already collected (DATE + HPCA scheduling cluster)."
        ),
        "papers": [
            ("DATE_2025", "TaiChi: Efficient Execution for Multi-DNNs Using Graph-Based Scheduling"),
            ("DATE_2025", "RankMap: Priority-Aware Multi-DNN Manager for Heterogeneous Embedded Devices"),
            ("DATE_2025", "Power- and Deadline-Aware Dynamic Inference on Intermittent Computing Systems"),
            ("HPCA_2025", "SoMa: Identifying, Exploring, and Understanding the DRAM Communication Scheduling Space for DNN Accelerators"),
            ("HPCA_2025", "PAISE: PIM-Accelerated Inference Scheduling Engine for Transformer-based LLM"),
            ("HPCA_2025", "Adyna: Accelerating Dynamic Neural Networks with Adaptive Scheduling"),
            ("ICCAD_2025", "R2T-Tiny: Runtime-Reconfigurable Throughput-Optimized TinyML for Hybrid Inference"),
            ("foundation", "behroozi2021_iterative_hardware_scheduling_isvlsi.pdf"),
            ("foundation", "a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf"),
        ],
    },
    "q2_fixed_approximation_tier_error_energy_stage_budget": {
        "title": "Fixed approximation tier — stage-wise error vs energy budgeting",
        "question": (
            "Given a **single user-specified approximation level** (not free per-operator precision "
            "search), can a compiler or runtime **minimize energy** by **allocating where error is "
            "allowed across pipeline stages** while meeting a quality target—especially for iterative "
            "or multi-stage modern applications?"
        ),
        "gap": (
            "Joint precision HLS (Li, Reis) searches bit-widths; MIPAC adapts iterations to inputs. "
            "Neither fixes one global tier then optimizes **stage-wise error placement vs energy**—"
            "the anchor your professor suggested."
        ),
        "why_you": (
            "Bridges your golden-model / fixed-point mindset with a clear optimization story "
            "(energy + error under one knob) and strong 2025 mixed-precision evidence."
        ),
        "papers": [
            ("DATE_2025", "Efficient Approximate Logic Synthesis with Dual-Phase Iterative Framework"),
            ("DATE_2025", "Segment-Wise Accumulation: Low-Error Logarithmic Domain Computing for Efficient Large Language Model Inference"),
            ("ICCAD_2025", "ApproxGNN: A Pretrained GNN for Parameter Prediction in Design Space Exploration for Approximate Computing"),
            ("ICCAD_2025", "PAR-CIM: A Precise/Approximate Reconfigurable Digital CIM Macro with 0.35-4b Fractional Mixed-Bitwidth Quantization"),
            ("ICCD_2025", "Early Termination with Activation Sign Prediction for Energy-Efficient CNN Inference Using Sum-of-Power-of-Two Quantization"),
            ("HPCA_2025", "Panacea: Novel DNN Accelerator using Accuracy-Preserving Asymmetric Quantization and Energy-Saving Bit-Slice Sparsity"),
            ("foundation", "li2015_joint_precision_optimization_approximate_hls_dac.pdf"),
            ("foundation", "reis2017_approximate_hls_ahls_date.pdf"),
        ],
    },
    "q3_iteration_aware_approximate_pipelines_under_deadline": {
        "title": "Iteration-aware approximate pipelines under deadline",
        "question": (
            "For **iterative** modern workloads (diffusion steps, speculative decoding, incremental "
            "inference): **which iterations or layers** should run at full vs reduced fidelity so "
            "both **deadline** and **error** constraints are met—without re-tuning the whole model?"
        ),
        "gap": (
            "EXION and SpecEE exploit sparsity/early exit per iteration or layer, but do not unify "
            "**deadline-bounded scheduling** with a **fixed approximation budget** across an "
            "iterative pipeline. ASIS/MIPAC are closest in spirit but pre-LLM/diffusion era."
        ),
        "why_you": (
            "Most publishable angle for 'iterative approximate pipeline' in the project title—timely, "
            "learnable (model + scheduler), and grounded in papers you already downloaded."
        ),
        "papers": [
            ("HPCA_2025", "EXION: Exploiting Inter- and Intra-Iteration Output Sparsity for Diffusion Models"),
            ("DATE_2025", "Cocktail: Chunk-Adaptive Mixed-Precision Quantization for Long-Context LLM Inference"),
            ("DATE_2025", "SparseInfer: Training-free Prediction of Activation Sparsity for Fast LLM Inference"),
            ("ISCA_2025", "SpecEE: Accelerating Large Language Model Inference with Speculative Early Exiting"),
            ("ICCAD_2025", "SpecMamba: Accelerating Mamba Inference on FPGA with Speculative Decoding"),
            ("ICCAD_2025", "Diff-DiT: Temporal Differential Accelerator for Low-bit Diffusion Transformers on FPGA"),
            ("HPCA_2025", "Lincoln: Real-Time 50~100B LLM Inference on Consumer Devices with LPDDR-Interfaced, Compute-Enabled Flash Memory"),
            ("foundation", "soni2022_asis_anytime_iterative_approximate_acm_tac.pdf"),
        ],
    },
}

# Extra DATE/HPCA downloads that are AC-relevant but not in catalog yet
EXTRA_CATALOG = [
    ("DATE_2025", "TaiChi: Efficient Execution for Multi-DNNs Using Graph-Based Scheduling", True, True),
    ("DATE_2025", "RankMap: Priority-Aware Multi-DNN Manager for Heterogeneous Embedded Devices", True, True),
    ("DATE_2025", "Power- and Deadline-Aware Dynamic Inference on Intermittent Computing Systems", True, True),
    ("DATE_2025", "SparseInfer: Training-free Prediction of Activation Sparsity for Fast LLM Inference", True, True),
    ("DATE_2025", "Filter-Based Adaptive Model Pruning for Efficient Incremental Learning on Edge Devices", True, True),
    ("DATE_2025", "MCTA: A Multi-Stage Co-Optimized Transformer Accelerator with Energy-Efficient Dynamic Sparse Optimization", True, True),
    ("HPCA_2025", "SoMa: Identifying, Exploring, and Understanding the DRAM Communication Scheduling Space for DNN Accelerators", True, True),
    ("HPCA_2025", "PAISE: PIM-Accelerated Inference Scheduling Engine for Transformer-based LLM", True, True),
    ("HPCA_2025", "Adyna: Accelerating Dynamic Neural Networks with Adaptive Scheduling", True, True),
    ("HPCA_2025", "Lincoln: Real-Time 50~100B LLM Inference on Consumer Devices with LPDDR-Interfaced, Compute-Enabled Flash Memory", True, True),
    ("HPCA_2025", "GoPIM: GCN-Oriented Pipeline Optimization for PIM Accelerators", True, True),
]


def norm_words(s: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-z0-9]{3,}", s)}


def find_pdf_for_title(conf: str, title: str) -> Path | None:
    papers_dir = CONF_ROOT / conf / "papers"
    if not papers_dir.is_dir():
        return None
    title_w = norm_words(title)
    best: tuple[int, Path] | None = None
    for pdf in papers_dir.glob("*.pdf"):
        stem_w = norm_words(pdf.stem)
        overlap = len(title_w & stem_w)
        if overlap >= max(3, len(title_w) // 3):
            if best is None or overlap > best[0]:
                best = (overlap, pdf)
    return best[1] if best else None


def find_foundation(name: str) -> Path | None:
    for base in (REFS, DAC61):
        p = base / name
        if p.is_file():
            return p
        matches = list(base.glob(name[:20] + "*"))
        if matches:
            return matches[0]
    return None


def link_or_stub(src: Path | None, dest_dir: Path, label: str, meta: dict) -> str:
    dest_dir.mkdir(parents=True, exist_ok=True)
    if src and src.exists():
        dest = dest_dir / src.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(os.path.relpath(src, dest_dir))
        return "linked"
    stub = dest_dir / (slugify(label, "ref") + ".txt")
    lines = [f"Title: {label}", "PDF not found locally.", ""]
    if meta.get("url"):
        lines.append(f"IEEE/ACM: {meta['url']}")
        lines.append(f"UW proxy: {uw_patron(meta['url'])}")
    if meta.get("library_search_url"):
        lines.append(f"UW Library search: {meta['library_search_url']}")
    if meta.get("publisher_search_url"):
        lines.append(f"Publisher search: {meta['publisher_search_url']}")
    if meta.get("note"):
        lines.append(f"Note: {meta['note']}")
    stub.write_text("\n".join(lines) + "\n")
    return "stub"


def enrich_catalog(catalog: dict) -> dict:
    for conf, title, ac, modern in EXTRA_CATALOG:
        catalog.setdefault(conf, [])
        seen = {e["title"] for e in catalog[conf]}
        if title not in seen:
            catalog[conf].append({"title": title, "ac": ac, "modern": modern})
    return catalog


def collect_all_pdfs() -> list[Path]:
    pdfs = []
    for conf in CONFS:
        d = CONF_ROOT / conf / "papers"
        if d.is_dir():
            pdfs.extend(d.glob("*.pdf"))
    return pdfs


def main() -> None:
    catalog = enrich_catalog(build_catalog())
    pdf_by_key: dict[str, Path] = {}

    for conf, entries in catalog.items():
        for e in entries:
            title = e["title"]
            key = f"{conf}::{title}"
            pdf = find_pdf_for_title(conf, title)
            if pdf:
                pdf_by_key[key] = pdf

    # Tier 1: all AC from six conferences
    ac_dir = IDEAS / "01_approximate_computing_all"
    modern_dir = IDEAS / "02_modern_reconfigurable_workloads"
    ac_dir.mkdir(parents=True, exist_ok=True)
    modern_dir.mkdir(parents=True, exist_ok=True)

    ac_manifest = []
    modern_manifest = []

    for conf in CONFS:
        for e in catalog.get(conf, []):
            if not e.get("ac"):
                continue
            title = e["title"]
            key = f"{conf}::{title}"
            pdf = pdf_by_key.get(key)
            meta = {
                "library_search_url": paper_url_hint(conf, title, e),
                "publisher_search_url": uw_patron(pub) if (pub := paper_publisher_url(conf, title)) else None,
            }
            status = link_or_stub(pdf, ac_dir, title, meta)
            rec = {"conference": conf, "title": title, "status": status, "local": pdf.name if pdf else None}
            ac_manifest.append(rec)
            if e.get("modern"):
                link_or_stub(pdf, modern_dir, title, meta)
                modern_manifest.append(rec)

    # Also scan loose PDFs in conference folders for AC titles not in catalog
    for pdf in collect_all_pdfs():
        stem = pdf.stem.replace("_", " ")
        if not AC_KW.search(stem):
            continue
        conf = pdf.parts[-3] if len(pdf.parts) >= 3 else "unknown"
        if conf not in CONFS:
            continue
        already = any(pdf.name == (m.get("local") or "") for m in ac_manifest)
        if not already:
            meta = {"note": f"Auto-included from {conf} downloads (filename match)."}
            status = link_or_stub(pdf, ac_dir, stem, meta)
            ac_manifest.append(
                {"conference": conf, "title": stem, "status": status, "local": pdf.name, "auto": True}
            )
            if MODERN_KW.search(stem):
                link_or_stub(pdf, modern_dir, stem, meta)
                modern_manifest.append(
                    {"conference": conf, "title": stem, "status": status, "local": pdf.name, "auto": True}
                )

    (ac_dir / "manifest.json").write_text(json.dumps(ac_manifest, indent=2) + "\n")
    (modern_dir / "manifest.json").write_text(json.dumps(modern_manifest, indent=2) + "\n")

    ac_linked = sum(1 for m in ac_manifest if m["status"] == "linked")
    mod_linked = sum(1 for m in modern_manifest if m["status"] == "linked")

    (ac_dir / "README.md").write_text(
        f"# Approximate computing — all 2025 conference hits\n\n"
        f"Papers from **DATE, ISLPED, ICCAD, ICCD, ISCA, HPCA (2025)** flagged as approximate-computing "
        f"related (mixed precision, quantization, early exit, approximate arithmetic/synthesis, etc.).\n\n"
        f"- **Catalog entries:** {len(ac_manifest)}\n"
        f"- **PDFs linked locally:** {ac_linked}\n"
        f"- **Stubs (paywalled):** {len(ac_manifest) - ac_linked}\n\n"
        f"Source PDFs remain in `references/conferences/<CONF>/papers/`. This folder uses symlinks.\n"
    )

    (modern_dir / "README.md").write_text(
        f"# Modern workloads × reconfigurable / scheduling\n\n"
        f"Subset of approximate-computing papers whose titles emphasize **modern workloads** (LLM, DNN, "
        f"edge, diffusion, serving) and/or **scheduling, rescheduling, runtime reconfiguration, FPGA, "
        f"CGRA, pipeline, deadline, or latency**.\n\n"
        f"- **Entries:** {len(modern_manifest)}\n"
        f"- **PDFs linked:** {mod_linked}\n\n"
        f"See `manifest.json` for the full list.\n"
    )

    # Research question folders
    rq_root = IDEAS / "research_questions"
    rq_root.mkdir(parents=True, exist_ok=True)
    rq_index = []

    for slug, meta in RESEARCH_QUESTIONS.items():
        qdir = rq_root / slug
        qdir.mkdir(parents=True, exist_ok=True)
        ctx = []
        for kind, ref in meta["papers"]:
            if kind == "foundation":
                finfo = FOUNDATION.get(ref, {"title": ref, "url": None, "note": ""})
                src = find_foundation(ref)
                status = link_or_stub(src, qdir, finfo["title"], finfo)
                ctx.append({"ref": ref, "kind": "foundation", "status": status})
            else:
                conf = kind
                title = ref
                key = f"{conf}::{title}"
                pdf = pdf_by_key.get(key) or find_pdf_for_title(conf, title)
                entry = next((x for x in catalog.get(conf, []) if x["title"] == title), {})
                m = {
                    "library_search_url": paper_url_hint(conf, title, entry),
                    "publisher_search_url": uw_patron(pub)
                    if (pub := paper_publisher_url(conf, title))
                    else None,
                }
                status = link_or_stub(pdf, qdir, title, m)
                ctx.append({"conference": conf, "title": title, "status": status})

        (qdir / "context_manifest.json").write_text(json.dumps(ctx, indent=2) + "\n")
        paper_lines = "\n".join(
            f"- {'✓' if c.get('status') == 'linked' else '○'} "
            + (c.get("title") or c.get("ref", ""))
            + (f" ({c.get('conference', 'foundation')})" if c.get("conference") else "")
            for c in ctx
        )
        (qdir / "README.md").write_text(
            f"# {meta['title']}\n\n"
            f"## Research question\n\n{meta['question']}\n\n"
            f"## Gap (not already solved as stated)\n\n{meta['gap']}\n\n"
            f"## Why this fits your project\n\n{meta['why_you']}\n\n"
            f"## Context papers (target 3–8)\n\n{paper_lines}\n\n"
            f"Linked PDFs point to `references/conferences/`. Stubs include UW Library / IEEE search URLs.\n"
        )
        rq_index.append({"slug": slug, "title": meta["title"], "papers": len(ctx)})

    (rq_root / "README.md").write_text(
        "# Research question folders\n\n"
        "Three **proposed open directions** in approximate computing. Each builds on 2025 venue papers "
        "plus foundational work—not duplicating a single prior paper.\n\n"
        "Discuss with your professor which question to pursue; Q2 aligns with the *fixed approximation "
        "level → optimize energy and error* idea.\n\n"
        + "\n".join(f"- [`{r['slug']}/`]({r['slug']}/) — {r['title']}" for r in rq_index)
        + "\n"
    )

    (IDEAS / "README.md").write_text(
        "# Ideas workspace\n\n"
        "Literature organized for approximate-computing research planning (2025 venues).\n\n"
        "## Structure\n\n"
        "| Folder | Purpose |\n"
        "|--------|--------|\n"
        "| [`01_approximate_computing_all/`](01_approximate_computing_all/) | All AC-related papers from DATE, ISLPED, ICCAD, ICCD, ISCA, HPCA |\n"
        "| [`02_modern_reconfigurable_workloads/`](02_modern_reconfigurable_workloads/) | AC papers × modern workloads / scheduling / reconfigurable HW |\n"
        "| [`research_questions/`](research_questions/) | Three unique directions + 3–8 context papers each |\n\n"
        "## Conferences covered\n\n"
        + ", ".join(CONFS)
        + "\n\n"
        f"**PDFs linked in AC folder:** {ac_linked} / {len(ac_manifest)}  \n"
        f"**PDFs linked in modern folder:** {mod_linked} / {len(modern_manifest)}\n\n"
        "Original downloads live under `references/conferences/<CONF>/papers/`.\n"
    )

    print(f"ideas/ built: AC={len(ac_manifest)} ({ac_linked} linked), modern={len(modern_manifest)} ({mod_linked} linked)")
    print(f"research_questions: {len(RESEARCH_QUESTIONS)} folders")


if __name__ == "__main__":
    main()
