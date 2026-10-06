# 05: Build spec for the implementer (Luna Max / Codex)

You **build**. You do **not** launch any GPU job. Claude (Opus) reviews, and then Codex launches. The designs in `01`–`04` are frozen: never change a gate, threshold, split, seed, control or criterion. If something is impossible as written, stop and write `design_L2_L4/BUILD_QUESTIONS.md`.

## Repo and branch
- **Repo:** `modal-account-A/pcs-e001-experiment`, branch `chatgpt/pcs-corrected-path-20260930`.
- **Worktree:** use your **own** worktree, e.g. `git worktree add ../pcs-wt-codex origin/chatgpt/pcs-corrected-path-20260930`. Do not use Claude's `pcs-wt-corrected` folder.
- **Commits:** small commits, then push to the same branch, rebasing first.

## Reuse (do not rewrite)
| Component | Location |
|---|---|
| PCS3 runner (canonical) | `scripts/pcs3_multi_register_bridge.py` (sha256 `20b0191e…`) |
| PCS3 multi-position driver and token-identity arm | `scripts/pcs3_multipos_bridge.py` |
| Multi-position capture and gates | `scripts/pcs_multipos_capture.py` |
| PCS4v2 source prompt and parser (amendment 1) | `scripts/pcs4v2_source_preflight.py` |
| PCS4v3 information-weighted loss | `--weighted` path in `scripts/pcs4v2_stage_b_train_bridges.py`, with its test in `tests/test_pcs4v3_weighting.py` |
| Modal launcher pattern | `scripts/modal_pcs3_multipos_bridge_launch.py`: `add_local_file` to bake code into the image, in-container sha assertions, detached `spawn`, volumes `pcs-core-artifacts` and `pcs-core-hf-cache`, L4 |

**The repo is private, so remote jobs must not `git clone`.**

## Deliverables (one launcher each; nothing launched)
| ID | Design | Script(s) | Profile | GPU estimate |
|---|---|---|---|---|
| W1 | 01 Part A | `scripts/w1_writer_sweep.py`; writes `W1_CHOICE.json` | modal-account-A | L4, about 1–2 h |
| PCS3c | 01 Part B | `scripts/pcs3c_confirm.py` (source generation with seed 20261005, multi-position capture, gates, bridge using the config read from `W1_CHOICE.json`, eval) | modal-account-A | L4, about 2–3 h |
| S4-dev | 03 | `scripts/s4_selective_filter.py` (loads the PCS3b bridge and features; F-LEACE, F-train, F-rand, none) | modal-account-B | L4, under 1 h |
| PCS4v4 | 02 | a `--contrastive` flag on the PCS4v3 Stage B path; launcher prepared but marked CONDITIONAL | modal-account-B | L4, about 3–4 h |
| RQ6 | 04 RQ6 (6A and 6B) | `scripts/rq6_qualification.py` (inference only, gate JSON) | either, or Kaggle | about 2–3 h |
| PCS6-A | 04 6A | `scripts/pcs6a_continuation.py` (implements D1-a and D1-b behind a flag; refuses to run unless the RQ6 gates pass) | modal-account-A | about 3–4 h |
| S2 | 07 | `scripts/s2_covert_channel.py` (attack k∈{1,4,16}, D-PCA/quant/noise, adaptive attacker, detection monitor) | modal-account-B | L4, about 1–2 h |
| MON2 | 08 | `scripts/mon2_compromised_state.py` (paired clean/injected generation, held-out templates, M-PCS/ACT/RECV/PUBLIC/TEXT monitors, firewall, harm-to-B) | modal-account-B | L4, about 1.5–2 h |
| RQ7 and PCS7 | 09 | `scripts/rq7_qualification.py` (inference only) and `scripts/pcs7_silent.py` (refuses to run unless the RQ7 choice is sealed) | modal-account-B | about 1 h and about 2 h |
| CAP1 | 10 | `scripts/cap1_capacity_ladder.py` (6 arms plus TI ceilings; FULLSEQ needs per-token capture of layers 16 and 28) | modal-account-A | about 3–5 h (FULLSEQ is the heaviest) |
| PCS6-B | 04 6B | `scripts/pcs6b_gsm8k.py` (refuses to run unless RQ6-B passes) | modal-account-B | about 3–4 h |

## Required in every runner
1. A `--smoke` mode: tiny model (Qwen3-0.6B) or a few episodes, CPU or 1 GPU minute. Run it locally where possible and commit its log.
2. **Gates first.** Write a gate JSON and **exit non-zero** before any training if a gate fails.
3. **Raw per-record outputs** in JSON. Record every arm's prediction, the targets, the episode id and the wrong-partner ids.
4. **Seal:** write bridge sha256 values and the probe-seed commitment before evaluation probes are built. The evaluation step re-verifies them.
5. **Summary JSON** with all metrics and criteria evaluated mechanically, plus the classification string. Use the state-cluster bootstrap (10,000) and exact McNemar where the design specifies them.
6. **Paths:** output to `/artifacts/<exp>-<script sha12>/`, and write `EXIT_CODE.txt`, `run.log` and `CODE_SHAS.json`.
7. **Unit tests** for new maths (contrastive loss, LEACE, swap-target computation, continuation parsing), under `tests/`.

## Hand-back
When every deliverable is built and smoke-tested, write `design_L2_L4/BUILD_REPORT.md` containing:
- the files and commits;
- the smoke results;
- the exact launch command for each item;
- runtime and cost estimates;
- any deviation or open question.

**Then stop.** Claude reviews before anything launches.
