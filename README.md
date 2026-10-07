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

## Why this matters: AI systems are becoming stateful

Most AI agents today carry continuity between steps as text. Each step, the model rebuilds its internal state from a written record, and anything not written down is lost. That is changing:
- deployed systems already store internal state (prompt caching);
- research systems pass it directly between agents (LatentMAS, C2C).

As more of an agent's working state is carried forward or shared as internal representations rather than text, the part humans can read shrinks. Making such systems safe needs two things this project studies:
1. translating and inspecting state across models;
2. monitoring and authorising what carried state is allowed to influence.

My own longer-term interest in persistent cognitive state is part of why I take this seriously. In line with my application, I am building the safety layer before pushing that capability further.

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

---

## Results added after submission (7 October 2026)

These results were produced **after** the BlueDot application was submitted on 6 October 2026. Every claim above is unchanged. Both pilots are **exploratory**: each analysis plan was committed before computing, and they are labelled post-hoc where that applies. They extend the early-warning result from *whether* a model will act to *which specific action* it is about to take, which is grant Gate 1 territory.

| Result (plain English) | Plan | Analysis code | Evidence |
|---|---|---|---|
| **Pilot 0:** before writing anything, the model's internal state predicts its first tool at **96.2%**, against **91.2%** from the full visible prompt (+4.9 [3.5, 6.4]). The second tool, two steps ahead, is not readable beyond text on held-out actions (−7.1). | `design_L2_L4/PILOT0_ACTION_FROM_STATE_PLAN_OPUS.md` | `analysis/pilot0_action_from_state.py` | `evidence/pilot0_action_from_state_2026-10-07/` |
| **Pilot 1 (live, multi-turn agent loop, 1,200 tasks):** before each call, internal state predicts the next tool at **98.2%**, against **85.5%** from the whole visible conversation (+12.7 [10.1, 15.1]). | `design_L2_L4/PILOT1_LIVE_PREFETCH_PLAN_OPUS.md` | `analysis/pilot1_analyse.py` | `evidence/pilot1_live_prefetch_2026-10-07/` |
| *Post-hoc:* **which file** it will read is not readable before output (35% vs 33% text). Once the model has written `read_file(`, it is readable at 83% (vs 33%). The tool is decided first; the file is chosen while writing. | `design_L2_L4/PILOT1_AMENDMENT_1_FILE_NAME_READOUT_OPUS.md` | `analysis/pilot1_analyse_names.py` | `evidence/pilot1_live_prefetch_2026-10-07/amendment1/` |

**Limits:**
- one model (Qwen3-4B), one synthetic file-assistant task family;
- in Pilot 1, 10% of turns were excluded because the model invented tools;
- no real latency was measured.

**Read-only prefetch from internal state** worked for argument-free calls (97.5% of `list_dir` calls) but not yet for file reads, and its wrong-prefetch rate exceeded the 5% target on test (7.6%). Speculative execution from internal state should therefore stay limited to read-only actions behind a permission check, with writes always requiring an explicit call.

The Pilot 1 raw turn records are in the evidence folder. The 252 MB feature tensor is available on request.

### What this could lead to (to be tested, not yet shown)

- **Earlier, more specific safety checks.** A harness could see *which* action an agent is about to take, such as a network upload or a read of a credentials file, before the call is written. It could then pause, ask for approval or block it. Today's text and output monitors only see the action once it has been written.
- **Knowing where to put the checks.** The results suggest the type of action is decided before output, and its target is chosen while the call is being written. Checks could be placed at each stage, rather than only at the end.
- **Oversight when there is no transcript.** In systems where models pass internal state to each other directly (latent communication), there may be no readable text to monitor. These results suggest internal state can still reveal intended actions, which is the premise of the funded work.
- **Faster agents, safely.** For harmless read-only actions, results could be fetched while the model is still deciding, behind a permission check. Writes always wait for an explicit call.

**What would have to hold first (the funded gates):**
- the signal must hold on other models and real tasks;
- it must survive a model trained to hide it (Gate 3);
- it must work at fixed, low false-alarm rates;
- it must add value beyond ordinary permissions and sandboxing (Gate 4).

