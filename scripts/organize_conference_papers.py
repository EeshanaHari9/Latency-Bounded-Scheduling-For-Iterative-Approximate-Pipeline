#!/usr/bin/env python3
"""Download, classify, and organize 2025 conference papers for approximate computing."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[1]
REFS = REPO / "references"
SCRIPT = Path(__file__).resolve().parent
DATA = json.loads((SCRIPT / "conference_papers_2025.json").read_text())

# Extended AC catalog from program/TOC mining (2025 only)
EXTENDED = {
    "DATE_2025": [
        "Dancer: Dynamic Compression and Quantization Architecture for Deep Graph Convolutional Network",
        "Cocktail: Chunk-Adaptive Mixed-Precision Quantization for Long-Context LLM Inference",
        "MPTorch-FPGA: A Custom Mixed-Precision Framework for FPGA-Based DNN Training",
        "FineQ: Software-Hardware Co-Design for Low-Bit Fine-Grained Mixed-Precision Quantization of LLMs",
        "LT-OAQ: Learnable Threshold Based Outlier-Aware Quantization and Its Energy-Efficient Accelerator for Low-Precision On-Chip Training",
        "LightMamba: Efficient Mamba Acceleration on FPGA with Quantization and Hardware Co-Design",
        "De2r: Unifying DVFS and Early-Exit for Embedded AI Inference Via Reinforcement Learning",
        "Late Breaking Results: Approximated LUT-Based Neural Networks for FPGA Accelerated Inference",
        "Late Breaking Results: Leveraging Approximate Computing for Carbon-Aware DNN Accelerators",
        "RGHT-Q: Reconfigurable GEMM Unit for Heterogeneous-Homogeneous Tensor Quantization",
        "Efficient Approximate Logic Synthesis with Dual-Phase Iterative Framework",
        "Efficient Approximate Nearest Neighbor Search Via Data-Adaptive Parameter Adjustment in Hierarchical Navigable Small Graphs",
        "Gradient Approximation of Approximate Multipliers for High-Accuracy Deep Neural Network Retraining",
        "EVASION: Efficient KV CAche CompreSsion vIa PrOduct QuaNtization",
        "SoftEx: A Low Power and Flexible Softmax Accelerator with Fast Approximate Exponentiation",
        "Timing-Driven Approximate Logic Synthesis Based on Double-Chase Grey Wolf Optimizer",
        "Segment-Wise Accumulation: Low-Error Logarithmic Domain Computing for Efficient Large Language Model Inference",
    ],
    "ISLPED_2025": [
        "Accelerating LLM Inference with Flexible N:M Sparsity via A Fully Digital Compute-in-Memory Accelerator",
        "GAVINA: flexible aggressive undervolting for bit-serial mixed-precision DNN acceleration",
        "Hybrid Systolic Array Accelerator with Optimized Dataflow for Edge Large Language Model Inference",
        "QuAKE: Speeding up Model Inference Using Quick and Approximate Kernels for Exponential Non-Linearities",
        "Revisiting Reconfigurable Acceleration of Vision Transformer with Patch Pruning",
        "TruncQuant: Truncation-Ready Quantization for DNNs with Flexible Weight Bit Precision",
        "Efficient Precision-Scalable Hardware for Microscaling (MX) Processing in Robotics Learning",
        "A Compact, Low Power Transprecision ALU for Smart Edge Devices",
        "RIMIX: RISC-V Core with MIXed-Precision SIMD Instruction Extensions Supported by Oracle-Assisted Sub-Network Search for Efficient TinyML",
    ],
    "ICCAD_2025": [
        "SERA-Float: A Soft Error Resilient Approximate Floating-Point Computing Format",
        "PAR-CIM: A Precise/Approximate Reconfigurable Digital CIM Macro with 0.35-4b Fractional Mixed-Bitwidth Quantization",
        "ApproxGNN: A Pretrained GNN for Parameter Prediction in Design Space Exploration for Approximate Computing",
        "MiCo: End-to-End Mixed Precision Neural Network Co-Exploration Framework for Edge AI",
        "BARQ: Boundary-Aware Regularized Training for Accurate Inference on Computing-in-Memory Accelerators with Low-Precision A/D Conversion",
        "Discriminate Weight Approximation for Efficient DSP Packing in LLM Accelerators",
        "Diff-DiT: Temporal Differential Accelerator for Low-bit Diffusion Transformers on FPGA",
        "SiST: Token Similarity and Sparsity Aware Optimization for Transformers on FPGA",
        "SpecMamba: Accelerating Mamba Inference on FPGA with Speculative Decoding",
        "R2T-Tiny: Runtime-Reconfigurable Throughput-Optimized TinyML for Hybrid Inference",
        "QUARK: Quantization-Enabled Circuit Sharing for Transformer Acceleration by Exploiting Common Patterns in Nonlinear Operations",
    ],
    "ICCD_2025": [
        "DMP-BFP: Dynamic Mixed-Precision Block Floating-Point and Exponent-Guided Precision Adjustment",
        "Hardware Efficient Multiplier design using an Optimal mix of Approximate Booth Encodings",
        "Enhancing Transformer Inference Efficiency on FPGA through Fully Fusion and Integer-Only Quantization Techniques",
        "PACE-lite: Compact and Efficient Piecewise Polynomial Approximation for Transformer Nonlinearity Acceleration",
        "QuFi: Adaptive Tiled Gustavson Output Reuse for Edge Sparse DNN Accelerators",
        "Flame: A Multiplier-Free LLM Accelerator with Dynamic Block Floating Point",
        "Early Termination with Activation Sign Prediction for Energy-Efficient CNN Inference Using Sum-of-Power-of-Two Quantization",
    ],
    "ISCA_2025": [
        "AQB8: Energy-Efficient Ray Tracing Accelerator through Multi-Level Quantization",
        "SpecEE: Accelerating Large Language Model Inference with Speculative Early Exiting",
        "Oaken: Fast and Efficient LLM Serving with Online-Offline Hybrid KV Cache Quantization",
        "ANSMET: Approximate Nearest Neighbor Search with Near-Memory Processing and Hybrid Early Termination",
        "MicroScopiQ: Accelerating Foundational Models through Outlier-Aware Microscaling Quantization",
        "LightNobel: Improving Sequence Length Limitation in Protein Structure Prediction Model via Adaptive Activation Quantization",
        "Process Only Where You Look: Hardware and Algorithm Co-optimization for Efficient Gaze-Tracked Foveated Rendering in Virtual Reality",
    ],
    "HPCA_2025": [
        "Panacea: Novel DNN Accelerator using Accuracy-Preserving Asymmetric Quantization and Energy-Saving Bit-Slice Sparsity",
        "FIGLUT: An Energy-Efficient Accelerator Design for FP-INT GEMM Using Look-Up Tables",
        "MANT: Efficient Low-bit Group Quantization for LLMs via Mathematically Adaptive Numerical Type",
        "VQ-LLM: High-performance Code Generation for Vector Quantization Augmented LLM Inference",
        "BitMoD: Bit-serial Mixture-of-Datatype LLM Acceleration",
        "EXION: Exploiting Inter- and Intra-Iteration Output Sparsity for Diffusion Models",
        "LUT-DLA: Lookup Table as Efficient Extreme Low-Bit Deep Learning Accelerator",
    ],
}

MODERN_KW = re.compile(
    r"schedul|reconfigur|fpga|cgra|\bhls\b|runtime|dynamic|mapping|workload|deadline|"
    r"latency|pipeline|iterative|real.?time|reschedul|edge|llm|transformer|dnn|"
    r"early.?exit|early.?termin|adaptive|mixed.?precision|quantiz|mamba|tinyml|"
    r"autonomous|serving|inference",
    re.I,
)
AC_KW = re.compile(
    r"approximat|mixed.?precision|quantiz|early.?exit|early.?termin|imprecis|"
    r"anytime|inexact|low.?precision|bitwidth|transprecision|sparsity|pruning|"
    r"product.?quant|microscal|outlier.?aware|logic.?synthesis|lut.?based|"
    r"softmax|exponent|foveated|carbon.?aware",
    re.I,
)

DOWNLOADS = DATA.get("downloads", {})

# UW–Madison off-campus access. NOTE: login.ezproxy…/login?url= drops the target
# URL (400). Use patron splash or hostname rewrite instead.
UW_AUTH_SPLASH = "https://patron.library.wisc.edu/authn/splash?url="
UW_LIBRARY_SEARCH = "https://search.library.wisc.edu/?q="

# Official proceedings entry points (unproxied); wrapped at use time.
CONFERENCE_PROC_URLS = {
    "DATE_2025": "https://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=10992638",
    "ISLPED_2025": "https://ieeexplore.ieee.org/document/11261780/",
    "ICCAD_2025": "https://ieeexplore.ieee.org/xpl/conhome/11240608/proceeding",
    "ICCD_2025": "https://ieeexplore.ieee.org/xpl/conhome/11310786/proceeding",
    "ISCA_2025": "https://dl.acm.org/doi/proceedings/10.1145/3695053",
    "HPCA_2025": "https://ieeexplore.ieee.org/xpl/conhome/10946282/proceeding",
}

RESEARCH_Q_PAPERS = {
    "q1_deadline_aware_rescheduling_on_reconfigurable_accelerators": [
        ("existing", "behroozi2021_iterative_hardware_scheduling_isvlsi.pdf"),
        ("existing", "ohata2022_ilp_variable_cycle_approximate_hls.pdf"),
        ("existing", "yao2020_imprecise_computation_dnn_scheduling.pdf"),
        ("existing", "a14_PT-Map_Efficient_Program_Transformation_Optimization_for_CGRA.pdf"),
        ("DATE_2025", "De2r: Unifying DVFS and Early-Exit for Embedded AI Inference Via Reinforcement Learning"),
        ("ICCAD_2025", "R2T-Tiny: Runtime-Reconfigurable Throughput-Optimized TinyML for Hybrid Inference"),
    ],
    "q2_fixed_approximation_tier_stage_error_energy_allocation": [
        ("existing", "li2015_joint_precision_optimization_approximate_hls_dac.pdf"),
        ("existing", "reis2017_approximate_hls_ahls_date.pdf"),
        ("existing", "soni2022_asis_anytime_iterative_approximate_acm_tac.pdf"),
        ("ICCAD_2025", "ApproxGNN: A Pretrained GNN for Parameter Prediction in Design Space Exploration for Approximate Computing"),
        ("ICCAD_2025", "PAR-CIM: A Precise/Approximate Reconfigurable Digital CIM Macro with 0.35-4b Fractional Mixed-Bitwidth Quantization"),
        ("ICCD_2025", "Early Termination with Activation Sign Prediction for Energy-Efficient CNN Inference Using Sum-of-Power-of-Two Quantization"),
    ],
    "q3_runtime_workload_aware_remapping_under_quality_constraints": [
        ("existing", "kemp2021_mipac_iterative_approximate_aspdac.pdf"),
        ("existing", "a309_Data-driven_HLS_optimization_for_reconfigurable_accelerators.pdf"),
        ("existing", "gog2022_d3_dynamic_deadline_driven_eurosys.pdf"),
        ("ISLPED_2025", "Revisiting Reconfigurable Acceleration of Vision Transformer with Patch Pruning"),
        ("DATE_2025", "Cocktail: Chunk-Adaptive Mixed-Precision Quantization for Long-Context LLM Inference"),
        ("HPCA_2025", "MANT: Efficient Low-bit Group Quantization for LLMs via Mathematically Adaptive Numerical Type"),
    ],
}


def slugify(title: str, conf: str) -> str:
    short = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")[:70]
    prefix = conf.lower().replace("_", "")
    return f"{prefix}_{short}"


def first_words(title: str, n: int = 4) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    return "_".join(words[:n]).lower()


def uw_patron(url: str) -> str:
    """Send user through UW NetID login, then to the publisher URL."""
    # patron splash expects a plain (not percent-encoded) url= value; encoding causes 400.
    return UW_AUTH_SPLASH + url


def uw_library_search(title: str, conf: str) -> str:
    """Search UW Libraries (recommended starting point per campus IT)."""
    year = conf.split("_")[-1]
    short = re.sub(r"\s+", " ", title).strip()
    # First ~8 words usually identify the paper in catalog search.
    words = short.split()[:8]
    query = quote(" ".join(words) + f" {year}")
    return UW_LIBRARY_SEARCH + query


def ezproxy_host(url: str) -> str:
    """Direct EZproxy hostname rewrite (works after one-time NetID login)."""
    from urllib.parse import urlparse

    p = urlparse(url)
    if not p.hostname:
        return url
    host = p.hostname.replace(".", "-")
    path = p.path or "/"
    if p.query:
        path = f"{path}?{p.query}"
    return f"https://{host}.ezproxy.library.wisc.edu{path}"


def paper_url_hint(conf: str, title: str, meta: dict) -> str:
    """Best-effort link for finding/downloading a paywalled paper via UW proxy."""
    if meta.get("url"):
        return meta["url"]
    arxiv_id = meta.get("arxiv")
    if arxiv_id:
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    if title in DOWNLOADS:
        return DOWNLOADS[title]

    return uw_library_search(title, conf)


def paper_publisher_url(conf: str, title: str) -> str | None:
    """Publisher-side search/proceedings URL (for patron splash / hostname rewrite)."""
    year = conf.split("_")[-1]
    short = re.sub(r"\s+", " ", title).strip()
    if conf == "ISCA_2025":
        query = quote(f'"{short}"', safe="")
        return (
            f"https://dl.acm.org/action/doSearch?AllField={query}"
            f"&startPage=0&pageSize=25"
        )
    query = quote(f'"{short}" {year}', safe="")
    return (
        "https://ieeexplore.ieee.org/search/searchresult.jsp"
        f"?queryText={query}&highlight=true&returnType=SEARCH"
    )


def proceedings_url_hint(conf: str) -> str:
    base = CONFERENCE_PROC_URLS.get(conf)
    return uw_patron(base) if base else "N/A"


def download(url: str, dest: Path) -> bool:
    try:
        result = subprocess.run(
            ["curl", "-fsSL", "-o", str(dest), url],
            capture_output=True,
            timeout=180,
        )
        return result.returncode == 0 and dest.exists() and dest.stat().st_size > 1000
    except Exception as exc:
        print(f"  download failed: {dest.name}: {exc}")
        return False


def build_catalog() -> dict[str, list[dict]]:
    catalog: dict[str, list[dict]] = {}
    for conf, entries in DATA.items():
        if conf == "downloads":
            continue
        catalog.setdefault(conf, [])
        seen = {e["title"] for e in catalog[conf]}
        for e in entries:
            if e["title"] not in seen:
                catalog[conf].append(e)
                seen.add(e["title"])
    for conf, titles in EXTENDED.items():
        catalog.setdefault(conf, [])
        seen = {e["title"] for e in catalog[conf]}
        for title in titles:
            if title in seen:
                continue
            ac = bool(AC_KW.search(title))
            modern = bool(MODERN_KW.search(title))
            catalog[conf].append({"title": title, "ac": ac, "modern": modern})
            seen.add(title)
    return catalog


def ensure_pdf(conf: str, title: str, conf_dir: Path) -> Path | None:
    papers_dir = conf_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    fname = slugify(title, conf) + ".pdf"
    dest = papers_dir / fname
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    url = DOWNLOADS.get(title)
    if url and download(url, dest):
        print(f"  downloaded {fname}")
        return dest
    return None


def link_or_note(src: Path | None, dest_dir: Path, title: str, conf: str, meta: dict) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    if src and src.exists():
        dest = dest_dir / src.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        rel = os.path.relpath(src, dest_dir)
        dest.symlink_to(rel)
    else:
        stub = dest_dir / (slugify(title, conf) + ".txt")
        lib_search = paper_url_hint(conf, title, meta)
        proc = proceedings_url_hint(conf)
        pub = paper_publisher_url(conf, title)
        lines = [
            f"Title: {title}",
            f"Conference: {conf}",
            "PDF not available locally (likely paywalled).",
            "",
            "Try these in order (sign in with NetID when prompted):",
            f"1. UW Library search (easiest): {lib_search}",
        ]
        if pub:
            lines.append(f"2. IEEE/ACM search via UW login: {uw_patron(pub)}")
            lines.append(f"3. IEEE/ACM search (hostname proxy): {ezproxy_host(pub)}")
        lines.append(f"4. Full proceedings via UW login: {proc}")
        stub.write_text("\n".join(lines) + "\n")


def resolve_existing(name: str) -> Path | None:
    direct = REFS / name
    if direct.exists():
        return direct
    dac = list((REFS / "DAC(61)" / "papers").glob(name[:20] + "*"))
    return dac[0] if dac else None


def main() -> None:
    catalog = build_catalog()
    conf_roots: dict[str, Path] = {}
    pdf_registry: dict[str, Path] = {}

    for conf, entries in catalog.items():
        conf_dir = REFS / "conferences" / conf
        conf_roots[conf] = conf_dir
        conf_dir.mkdir(parents=True, exist_ok=True)
        index = []
        for e in entries:
            title = e["title"]
            pdf = ensure_pdf(conf, title, conf_dir)
            key = f"{conf}::{title}"
            if pdf:
                pdf_registry[key] = pdf
            index.append(
                {
                    **e,
                    "local_pdf": pdf.name if pdf else None,
                    "slug": slugify(title, conf),
                    "library_search_url": paper_url_hint(conf, title, e),
                    "proceedings_url": proceedings_url_hint(conf),
                    "publisher_search_url": uw_patron(pub)
                    if (pub := paper_publisher_url(conf, title))
                    else None,
                }
            )
        (conf_dir / "paper_index.json").write_text(json.dumps(index, indent=2) + "\n")
        ac_n = sum(1 for x in index if x["ac"])
        mod_n = sum(1 for x in index if x["ac"] and x["modern"])
        pdf_n = sum(1 for x in index if x["local_pdf"])
        (conf_dir / "README.md").write_text(
            f"# {conf.replace('_', ' ')}\n\n"
            f"Curated approximate-computing-related papers from the **2025** program/proceedings.\n\n"
            f"- **AC-related:** {ac_n}\n"
            f"- **AC + modern workloads / reconfigurable:** {mod_n}\n"
            f"- **PDFs downloaded locally:** {pdf_n}\n"
            f"- Remaining entries are indexed in `paper_index.json` (paywalled or no open PDF found).\n"
        )
        print(f"{conf}: {ac_n} AC, {mod_n} modern, {pdf_n} PDFs")

    # Tier 1 & 2 across new conferences
    ac_dir = REFS / "approximate_computing" / "from_conferences_2025"
    modern_dir = REFS / "approximate_modern_workloads" / "from_conferences_2025"
    ac_dir.mkdir(parents=True, exist_ok=True)
    modern_dir.mkdir(parents=True, exist_ok=True)

    for conf, entries in catalog.items():
        for e in entries:
            if not e.get("ac"):
                continue
            title = e["title"]
            key = f"{conf}::{title}"
            pdf = pdf_registry.get(key)
            link_or_note(pdf, ac_dir, title, conf, e)
            if e.get("modern"):
                link_or_note(pdf, modern_dir, title, conf, e)

    # Update top-level README snippets
    ac_readme = REFS / "approximate_computing" / "README.md"
    if ac_readme.exists():
        text = ac_readme.read_text()
        if "from_conferences_2025" not in text:
            ac_readme.write_text(
                text.rstrip()
                + "\n\n## 2025 conferences (DATE, ISLPED, ICCAD, ICCD, ISCA, HPCA)\n\n"
                "See `from_conferences_2025/` for symlinks/stubs from "
                "`references/conferences/*/`. Source PDFs live under each conference folder.\n"
            )

    modern_readme = REFS / "approximate_modern_workloads" / "README.md"
    if modern_readme.exists():
        text = modern_readme.read_text()
        if "from_conferences_2025" not in text:
            modern_readme.write_text(
                text.rstrip()
                + "\n\n## 2025 conferences\n\nSee `from_conferences_2025/` for the modern-workload subset.\n"
            )

    # Research question folders — add 2025 papers alongside existing links
    rq = REFS / "research_questions"
    for slug, items in RESEARCH_Q_PAPERS.items():
        qdir = rq / slug
        qdir.mkdir(parents=True, exist_ok=True)
        lines = []
        for kind, ref in items:
            if kind == "existing":
                src = resolve_existing(ref)
                if src:
                    dest = qdir / src.name
                    if dest.exists() or dest.is_symlink():
                        dest.unlink()
                    dest.symlink_to(os.path.relpath(src, qdir))
                    lines.append(f"- `{src.name}` (existing reference)")
                else:
                    lines.append(f"- `{ref}` (missing)")
            else:
                conf = kind
                title = ref
                key = f"{conf}::{title}"
                pdf = pdf_registry.get(key)
                entry = next(
                    (x for x in catalog.get(conf, []) if x["title"] == title),
                    {},
                )
                link_or_note(pdf, qdir, title, conf, entry)
                lines.append(f"- `{slugify(title, conf)}` — {title} ({conf})")

        readme = qdir / "README.md"
        base = readme.read_text() if readme.exists() else ""
        if "## 2025 conference context papers" not in base:
            readme.write_text(
                base.rstrip()
                + "\n\n## 2025 conference context papers\n\n"
                + "\n".join(lines)
                + "\n"
            )

    summary = REFS / "conferences" / "README.md"
    proc_rows = "\n".join(
        f"| {c.replace('_', ' ')} | `{c}/` | [Proceedings via UW proxy]({proceedings_url_hint(c)}) |"
        for c in sorted(catalog)
    )
    summary.write_text(
        "# 2025 conference literature (approximate computing)\n\n"
        "Organized by venue. Each subfolder contains:\n\n"
        "- `paper_index.json` — classified titles (`ac`, `modern` flags) + UW proxy URLs\n"
        "- `papers/` — downloaded PDFs when openly available (mostly arXiv preprints)\n\n"
        "Off-campus access: use **UW Library search** or "
        "`patron.library.wisc.edu/authn/splash` links in each stub; "
        "sign in with NetID when prompted.\n\n"
        "| Conference | Folder | Proceedings (UW proxy) |\n|------------|--------|------------------------|\n"
        + proc_rows
        + "\n\nAggregated symlinks/stubs: `../approximate_computing/from_conferences_2025/` "
        "and `../approximate_modern_workloads/from_conferences_2025/`.\n"
    )
    print("Done.")


if __name__ == "__main__":
    main()
