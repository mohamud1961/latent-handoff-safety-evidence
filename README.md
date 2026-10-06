# Latent handoff safety: public evidence

**This repository is evidence only.** Note on provenance: this public copy is a single snapshot commit. The original dated commit history of the designs and results lives in the private repository, and is available to grant reviewers on request.

It contains:
- pre-registered designs and amendments;
- sealed results;
- raw records;
- checksums;
- the statistics code (`analysis/mon2_contract.py`: cluster bootstrap and exact McNemar);
- the post-hoc analysis script.

The experiment code (bridge training, model running, compute launchers) is withheld for now, so as not to release capability-relevant transfer code ahead of the safety work. It is **available to grant reviewers on request**, and will be released with the final report. The `scripts/...` paths in the "Code" column refer to that private repository.

The evidence behind a BlueDot Rapid Grant application. The question: when AI models pass internal working state directly to each other (latent communication), can that handoff be monitored, given limited authority, and controlled before the receiver acts?

**Experiments use open models** (Qwen3 0.6B–8B, Qwen2.5-0.5B, Phi-4-mini), with total cloud compute of about $120 (`SPEND.md`).

**Method:**
- Success criteria are committed before data collection (`design_L2_L4/`). Amendments are dated and disclosed; two came after a gate result but before the affected outcome data.
- Controls: another sender's state, no state, random state, restarted receiver, text handoff.
- Statistics: task-clustered bootstrap (10,000 resamples, seed 0) and exact McNemar tests.
- Results are sealed with SHA-256 checksums (`evidence/*/SHA256SUMS.txt`). See `SCRUB_MANIFEST.md` for the 16 files changed by publication scrubbing.
- **Failures are kept.**

## Claim → design → code → evidence

| Claim (plain English) | Design (pre-registered) | Code | Sealed evidence |
|---|---|---|---|
| Early-warning firewall: the pre-output handoff predicts obeying a hidden unauthorised instruction (AUROC 0.967); blocking flagged handoffs cuts receiver harm 47% → 4% at 6.3% clean false alarms | `design_L2_L4/17_*`, `MON3B_AMENDMENT_1_*` (MON3 freeze `11_*`) | `scripts/mon3b_routine_intent.py`, `scripts/mon3_unauthorised_intent.py` | `evidence/mon3b_rerun_full_2026-10-05/`; recompute from `evidence/mon3b_supplement_2026-10-06/` |
| *Post-hoc:* 96% caught at a threshold locked for 1% validation false alarms (1.3% on test); within-wording AUROC 0.934; text + latent beats text by +8.7 | `design_L2_L4/MON3B_POSTHOC_ANALYSIS_PLAN_OPUS.md` (committed before computing) | `analysis/mon3b_posthoc.py` | `evidence/mon3b_posthoc_2026-10-06/`; per-episode records + scores: `evidence/mon3b_supplement_2026-10-06/` |
| Wrong inherited state beats correct verified text (66% vs 16%) | `design_L2_L4/15_*` | `scripts/interfere1.py` | `evidence/interfere1_full_2026-10-05/` |
| Authority gate: verified wins 100% (prompting 18%); spoof text 0% | `design_L2_L4/19_*` | `scripts/auth1.py` | `evidence/auth1_full_2026-10-05/` |
| LatentMAS: transfer 90.6% vs 8.8%; authority conflict **does not** reproduce | `design_L2_L4/21_*` + EXT1 amendments 1–3 | `scripts/ext1.py`, `third_party/LatentMAS` (pinned, licence included) | `evidence/ext1_full_2026-10-06/` |
| C2C: injection doesn't measurably propagate; a 4-bit payload decoded at 74% per bit (partial channel; pre-set 95% bar missed) | `design_L2_L4/13_*` | `scripts/s5_c2c_security.py` | `evidence/s5_c2c_full_2026-10-05/` |
| Read / edit the handoff: readable ~6× chance; edits not selective; prediction fails baseline | `design_L2_L4/20_*` | `scripts/cogmon1.py` | `evidence/cogmon1_full_2026-10-05/`, `evidence/s4_dev_2026-10-05/` |
| Generalisation 87.7% on unseen combos (earlier runs varied) | `design_L2_L4/18_*` | `scripts/gen1.py` | `evidence/gen1_full_2026-10-05/`, `evidence/pcs7b_full_2026-10-05/` |
| 8B → 4B transfer passes all 11 criteria | `design_L2_L4/12_*` | `scripts/scale1_pcs2b.py` | `evidence/scale1_sup_full_2026-10-05/` |

**Failures and incomplete runs:**
- MON3 stopped at its gate (`mon3_full`);
- the "silent reasoning" false positive (`pcs7_full`);
- four label-free nulls (`pcs4v4_*`, `pcs4v2*`);
- cross-family Qwen → Phi (`scale1_xfam_full`);
- three-value fidelity (`pcs3c_confirm`);
- S2 covert channel timed out (`s2_full_timeout`);
- RQ6 stopped.

**Amendments** are in `design_L2_L4/*AMENDMENT*`, each with a date and reason. Two were applied after a gate (MON3b format threshold; EXT1 gate clarification), and both are disclosed in their results.

Every number in the claim map can be checked against the raw records in `evidence/` (JSON/JSONL). The bootstrap and McNemar statistics can be recomputed with `analysis/mon2_contract.py`.
