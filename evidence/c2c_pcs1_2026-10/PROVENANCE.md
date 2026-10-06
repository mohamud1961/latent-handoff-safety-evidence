# C2C fidelity audit (runs 1–3) and PCS1: sealed evidence

Sealed 2026-10-02 by Claude (Opus), from the work folder `~/Downloads/pcs-c2c-audit/` on the user's Mac. This sealing responds to the custody request in `PCS_C2C_PCS1_INDEPENDENT_REVIEW_AND_NEXT_GATE_2026-10-02.md`.

## Verify
```
cd evidence/c2c_pcs1_2026-10
shasum -a 256 -c MANIFEST.sha256     # every sealed file
python3 audit.py                      # raw-result hashes + recomputed headline numbers (~4 min, stdlib only)
```
`AUDIT_OUTPUT.txt` holds the audit output at sealing time. Every raw-result hash matched, and every headline number reproduced from the per-item records.

## What is here
| Folder | Kaggle kernel (private, user `kaggle-user`) | Pair (sharer → receiver) | Wall time |
|---|---|---|---|
| `run1/` | `pcs-c2c-fidelity` v1 | Qwen2.5-0.5B-Instruct → Qwen3-0.6B | 26.9 min |
| `run2/` | `pcs-c2c-fidelity-run2` | Qwen2.5-1.5B-Instruct → Qwen3-1.7B | 40.6 min |
| `run3/` | `pcs-c2c-fidelity-run3` | Qwen3-4B → Qwen3-0.6B | 147 min |
| `pcs1_pilot_v1/` | `pcs1-pilot` (v2 push; v1 failed in setup) | Qwen3-4B → Qwen3-0.6B, mod-10 mixed ops | 6.2 min |
| `pcs1_pilot_v2/` | `pcs1-pilot` (later version) | same, addition-only | 4.9 min |
| `pcs1/` | `pcs1-new-deduction` | same, depth 1, N=3000 | 63.3 min |

Each folder contains:
- the notebook exactly as pushed;
- `kernel-metadata.json`;
- the PREREG and RESULTS write-ups;
- the Kaggle log (`kaggle.log`);
- the raw per-item outputs (`results.json.gz`).

`RAW_RESULTS_ORIGINAL_SHA256.txt` gives the sha256 of each *uncompressed* original `results.json`. `audit.py` checks the decompressed bytes against it.

Left out deliberately:
- `results_partial.json`: mid-run checkpoints, superseded by the final file;
- local venvs;
- the C2C clone (pinned by commit below).

The PCS1 pilot v2 qualification table is in `pcs1/PREREG_pcs1.md`.

## Pinned versions
- C2C code: `thu-nics/C2C` @ `3ca0e98020bac1f36000623afcb8dfc6f8c29bdf`.
- Fuser weights: `nics-efc/C2C_Fuser` @ `f01fc3258b305e280e04c7238f4f2cf31b7dc70d`. This snapshot hash appears in every run log. Sub-folders used:
  - `qwen3_0.6b+qwen2.5_0.5b_Fuser/final`
  - `qwen3_1.7b+qwen2.5_1.5b_Fuser/final`
  - `qwen3_0.6b+qwen3_4b_Fuser/final`
- Model weights: the notebooks did not log these revisions. The HF `main` revisions at sealing time are below. Each was last modified before the runs (2025 dates), so these are the revisions that ran.

  | Model | Revision | Last modified |
  |---|---|---|
  | Qwen/Qwen3-0.6B | `c1899de289a04d12100db370d81485cdf75e47ca` | 2025-07-26 |
  | Qwen/Qwen3-1.7B | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` | 2025-07-26 |
  | Qwen/Qwen3-4B | `1cfa9a7208912126459214e8b04321603b3df60c` | 2025-07-26 |
  | Qwen/Qwen2.5-0.5B-Instruct | `7ae557604adf67be50417f59c2c2f167def9a775` | 2024-09-25 |
  | Qwen/Qwen2.5-1.5B-Instruct | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | 2024-09-25 |
- Environment for all runs:
  - Kaggle Tesla T4, fp16 (gated against fp32);
  - torch 2.10.0+cu128 (Kaggle default);
  - transformers 4.52.4, tokenizers 0.21.4, huggingface_hub 0.34.3 (C2C's pins);
  - seed 0, greedy decoding.
- Datasets: loaded at run time via `datasets` (MMLU-Redux, AI2 ARC-Challenge, OpenBookQA, GSM8K). Item ids are in the per-item records. Wrong-state partners, the same-length derangements, are recorded per item in the `partner` field of each `C_mm*` entry.

## Headline (recomputed by `audit.py`)
| Run | C2C − receiver | C2C − wrong-state (Δ_specific) | Pre-registered reading |
|---|---|---|---|
| 1 | +9.5 | −0.2 [−1.1, +0.6] | non-specific perturbation |
| 2 | −5.4 | +0.7 [+0.1, +1.4] | mixed / no claim |
| 3 | +14.1 | **+5.4 [+4.4, +6.4]**; exact McNemar vs each of 3 wrong states p ≤ 3.5e-11 | partial |
| PCS1 | 0.0 | −0.1 [−0.4, +0.3] | null (receiver fails explicit-state gate: text oracle 17%) |

### Run 3 detail
Run 3's Δ_specific is concentrated where the source is right and the receiver alone is wrong: +9.7 [+8.1, +11.3].

On items where the source is **wrong**, C2C's agreement with the source's (wrong) answer exceeds the wrong-state controls by +4.6 [+2.7, +6.6]. That is weak but real inheritance of source beliefs, including mistakes.

The paper-reproduction score (Part A: OBQA N=200, generation readout, C2C 55.5% vs paper 55.2%) uses a different subset and readout from the main audit's 51.8%. Keep them separate.

### Post-hoc / independent analyses
These are labelled post-hoc where applicable. They include:
- the calibration re-implementation in `audit.py`: its fold assignment differs from the notebooks', so Rcal differs by a few tenths of a point;
- all run-3 splits;
- the McNemar tests.
