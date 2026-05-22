# Reference papers

Open-access or author-hosted PDFs aligned with **latency-bounded iterative approximate pipeline** + extensions **Ext-A … Ext-D**. Use for related work and DAC-oriented writing.

| File | Citation | Alignment to this project |
|------|----------|---------------------------|
| `behroozi2021_iterative_hardware_scheduling_isvlsi.pdf` | S. Behroozi, Y. Yao, H. Yang, Y. Kim, *Scheduling of Iterative Computing Hardware Units for Accuracy and Energy Efficiency*, IEEE ISVLSI 2021. [IEEE](https://ieeexplore.ieee.org/document/9401706) · [NSF PAR](https://par.nsf.gov/servlets/purl/10230395) | **Closest prior work:** ILP scheduling of **iteration latency** on a DAG under total latency budget; input-dependent error model. **Ext-A** implements and validates on A→B→C. |
| `ohata2022_ilp_variable_cycle_approximate_hls.pdf` | K. Ohata, H. Nishikawa, X. Kong, H. Tomiyama, *ILP-Based and Heuristic Scheduling Techniques for Variable-Cycle Approximate Functional Units in HLS*, Computers 11(10):146, 2022. [DOI](https://doi.org/10.3390/computers11100146) | **DAC-relevant:** ILP/list scheduling for **variable-cycle approximate FUs** under time/resource constraints. Parallels offline oracle + ROM scheduling. |
| `li2015_joint_precision_optimization_approximate_hls_dac.pdf` | C. Li, W. Luo, S. Sapatnekar, J. Hu, *Joint Precision Optimization and High Level Synthesis for Approximate Computing*, **DAC 2015**. [ACM](https://dl.acm.org/doi/10.1145/2744769.2744863) | **DAC anchor:** Approximation-aware **HLS scheduling + binding** with ILP; error models for quality under latency. |
| `reis2017_approximate_hls_ahls_date.pdf` | C. Reis et al., *High-Level Synthesis of Approximate Hardware under Joint Quality and Energy Optimization*, DATE 2017. | Approximate **HLS** with scheduling + quality–energy pass; cite for design-automation framing. |
| `kemp2021_mipac_iterative_approximate_aspdac.pdf` | T. Kemp, Y. Yao, Y. Kim, *MIPAC: Dynamic Input-Aware Accuracy Control for Dynamic Auto-Tuning of Iterative Approximate Computing*, ASPDAC 2021. [NSF PAR](https://par.nsf.gov/servlets/purl/10228464) | **Runtime** tuning of **iterations (NOI)** for iterative approximate hardware; complements offline **k** schedule + **Ext-B** early-stop. |
| `soni2022_asis_anytime_iterative_approximate_acm_tac.pdf` | A. Soni et al., *As-Is Approximate Computing* (ACM TACO 2022). [Author PDF](https://jsm.ece.wisc.edu/docs/soni-acmtaco2022.pdf) | **Iterative / anytime** stages with time-proportional refinement; supports **Ext-B** narrative. |
| `yao2020_imprecise_computation_dnn_scheduling.pdf` | S. Yao et al., *Scheduling Real-time Deep Learning Services as Imprecise Computations*, arXiv:2011.01112, 2020. | Maximize accuracy under **deadlines** via mandatory/optional parts; deadline–quality tradeoff (software domain). |
| `gog2022_d3_dynamic_deadline_driven_eurosys.pdf` | I. Gog et al., *D3: A Dynamic Deadline-Driven Approach for Building Autonomous Vehicles*, EuroSys 2022. [NSF PAR](https://par.nsf.gov/servlets/purl/10325774) | **Dynamic deadlines** and runtime accuracy adjustment in **pipelines**; motivation for per-job **L**. |

## Suggested citation order in a DAC paper

1. Behroozi et al. (2021) — position as primary related scheduling work  
2. Ohata et al. (2022) or Li et al. (2015) — HLS / DAC design automation  
3. Kemp et al. (2021) or Soni et al. (2022) — iterative / runtime quality control (**Ext-B**)  
4. Yao et al. (2020) or Gog et al. (2022) — deadline-constrained accuracy  

## Source URLs (if you need to re-download)

```text
https://par.nsf.gov/servlets/purl/10230395          # Behroozi (use Accept: application/pdf)
https://pub.mdpi-res.com/computers/computers-11-00146/article_deploy/computers-11-00146-v2.pdf
http://www.ece.umn.edu/~sachin/conf/dac15-cl.pdf    # Li DAC 2015
http://slam.ece.utexas.edu/pubs/date17.AHLS.pdf     # Reis DATE 2017
https://par.nsf.gov/servlets/purl/10228464          # Kemp MIPAC
https://jsm.ece.wisc.edu/docs/soni-acmtaco2022.pdf
https://arxiv.org/pdf/2011.01112.pdf
https://par.nsf.gov/servlets/purl/10325774          # D3 EuroSys
```

*PDFs are included for literature review in this repository. Copyright remains with the respective publishers and authors.*
