# Design L2–L4 build report

**Date:** 2026-10-04
**Branch:** `chatgpt/pcs-corrected-path-20260930`
**Review state:** the original build handoff below is historical. `RESOLUTIONS_1_OPUS.md` resolved the listed protocol questions; current execution and dependency status is recorded in the addendum at the end. Read that addendum first.

## Summary

- MON2 was corrected per `REVIEW_MON2_OPUS.md`. The authorized 20-program real-model smoke completed through A, the frozen PCS2b bridge, and B on Modal L4. It is smoke evidence only, not a scientific result or authorization for the full run.
- PCS4v4's neural contrastive path, W1, and the S4/S2/RQ6/PCS3c/PCS6 build work are present. Tests and synthetic CPU smokes pass.
- S4, S2, RQ6, PCS3c and PCS6 remain blocked or preparation-only where the frozen protocols leave scientific choices open. Their preflights fail closed; no model or GPU work was used for them.
- The MON2 freeze leaves three analysis details unresolved, and the existing model/tokenizer snapshots are not immutably pinned. These are review questions, not choices made by this build.
- No full experiment was launched. The only Modal model run was the authorized MON2 smoke. No other GPU job, Kaggle job, model download or external service was used.

## Deliverables and state

| Item | Build and validation | State before any scientific run |
|---|---|---|
| **MON2** | 95% source-parse threshold, 98% exact-checkpoint threshold, invalid-pair exclusion/reporting, and exact PCS2b receiver prompts. Unit tests and CPU smoke pass. Real smoke: 20 programs / 40 paired episodes; 100% parsed, 100% exact checkpoints, 0 exclusions; bridge SHA matched; ten receiver arms ran. | Full run still needs review of the three MON2 interpretation items below and model/tokenizer custody. The smoke's test scores were not evaluated. |
| **PCS4v4** | Neural-only contrastive loss on the PCS4v3 information-weighted objective; three train-only matched negatives; sealed source/bridge checks and reducer. The unchanged token-identity arm remains the writer ceiling. Focused tests and objective/reducer synthetic smokes pass. Local entrypoint now verifies the PCS4v3 trigger and required Modal profile before spawning. | Triggered by the recorded PCS4v3 TI-pass/neural-null result. No PCS4v4 GPU run. Review model/tokenizer custody before launch. |
| **S4-dev** | Filter, metric, protocol-validation and Modal scaffolds; 11 focused tests and synthetic CPU smoke pass. Profile and custody gates fail closed. | Prep only. Bridge path/SHA/profile access and F-train/MLP probe settings remain unresolved. |
| **S2** | Attack/defense math and metric helpers, protocol validator and disabled Modal scaffold; 13 focused tests and synthetic CPU smoke pass. | Prep only. No PCS2b extraction/training/evaluation executor. Nine protocol choices remain unresolved and `S2_EXECUTOR_READY` is false. |
| **W1** | Train/validation-only writer sweep, sealed `W1_CHOICE.json` output path and detached launcher. The CPU smoke exercised the canonical PCS3 `train_bridge` and `evaluate` paths with synthetic data and fake model/tokenizer adapters; 13 focused tests pass. | Scientific runner is implemented, but model/tokenizer snapshot custody and source-feature model provenance must be pinned before a reproducible run. No provider run occurred. |
| **RQ6** | Strict parsers, frozen-threshold scoring helpers and no-model preflight; 11 focused tests and synthetic CPU smoke pass. | Blocked on 15 protocol conflicts, notably the required `s0`–`s11` / `FINAL:` trace versus the mandated PCS4v2 `s0`–`s8` / `FINAL_SUMMARY:` prompt/parser. No inference launcher was added. |
| **PCS3c** | Pure scoring, McNemar/bootstrap helpers and blocked preflight; 9 focused tests and synthetic CPU smoke pass. | No scientific executor or Modal launcher. Preflight reports 11 blockers, including W1 choice, pool/split/order, parser/checkpoint mapping, model custody and evaluation commitments. |
| **PCS6-A / PCS6-B** | Pure scoring helpers, D1 decision validation, swap-state propagation, literal-string exploratory scoring and fail-closed preflights; 10 focused tests and both synthetic CPU smokes pass. | Both preflights report 21 blockers, including RQ6 conflicts, no qualified RQ6 gate or sealed W1 choice, unresolved model/data custody and no scientific executor. No inference or training launcher was added. |

Full itemized protocol blockers are recorded in [`BUILD_QUESTIONS.md`](BUILD_QUESTIONS.md). Synthetic smoke outputs are engineering checks only and do not count as experiment results.

## MON2 smoke record

Evidence: [`evidence/mon2_gpu_smoke_2026-10-04/SMOKE_REPORT.md`](../evidence/mon2_gpu_smoke_2026-10-04/SMOKE_REPORT.md).

- Modal call: `fc-01M43VDBBS53H80J8S4Q4ZV92J` on profile `modal-account-B`; 600-second timeout, L4, 32 GiB.
- Runner SHA-256: `ff37b674ed97cc786e07ff33e39b69bb5a0c7a5694b12a30c6baa8f851eaf371`.
- Remote output: `pcs-core-artifacts:mon2-gpu-smoke-ff37b674ed97/`.
- It exercised generation, capture, bridge prefixes, monitors fitted on the 15-program training split, and the receiver arms. It did not fit/score on validation or test or enforce study-scale gates.
- Two earlier detached attempts exited before model loading due to the input-gate constant and neutral-note formatting; both were fixed and covered by regression tests. The successful call used the final runner SHA above. The launcher now also checks the expected Modal profile before spawning; its remote model-execution function was not changed by that guard.
- At the 600-second timeout, the published base-rate upper bound is about **$0.18**; the actual billed duration is not available in the local evidence.

## Validation

The final focused suite passed **102 tests**: the new MON2, PCS4v4, S4, S2, W1, RQ6, PCS3c and PCS6 tests, plus the existing PCS4v3 weighting regression test. Evidence and command output are in [`evidence/build_validation_2026-10-04/`](../evidence/build_validation_2026-10-04/). `py_compile` passed for all changed/new runner and launcher Python files, and `git diff --check` was clean.

The deterministic CPU smokes also passed for MON2, PCS4v4 Stage B and reducer, S4, S2, W1, RQ6, PCS3c, PCS6-A and PCS6-B. For RQ6/PCS3c/PCS6, the default preflight was separately run and correctly exited nonzero with `BLOCKED`; this is the expected result, not a test failure.

The W1 smoke emits a PyTorch warning from the unchanged canonical PCS3 runner when converting a gradient-bearing loss tensor to a scalar; the smoke completed with exit code 0. It is recorded in the W1 smoke log.

## Review blockers before full runs

1. **MON2 public-input baseline:** Task 2's injected rows vary by program, so M-PUBLIC can predict A's susceptibility. M-PUBLIC is reported for COMP/REJ, but the freeze only gives it a near-chance check for injection detection. Decide whether Task 2 needs a public-baseline comparison/criterion or narrow the claim.
2. **MON2 shuffled control:** the freeze says shuffled AUROC should be approximately 0.5 but sets no tolerance. The runner reports it diagnostically and excludes it from the mechanical classification. Set a reviewed range or confirm diagnostic-only treatment.
3. **MON2 firewall aggregation:** the current candidate is `p(INJ) × p(COMP | INJ)`. The freeze says to combine Tasks 1 and 2 but does not specify the formula. Approve it or amend the protocol before interpreting the firewall criterion.
4. **Model custody:** manifests pin code, bridges and feature files, but not the underlying Qwen model/tokenizer snapshots. The MON2 smoke proves that the current model paths execute; it does not prove identity with snapshots used to train the frozen PCS2b bridge. Pin immutable revisions or local hashes and record source-feature provenance before full MON2, PCS4v4 or W1 runs. PCS3c/RQ6/PCS6 also carry experiment-specific custody blockers.
5. **S4/S2/RQ6/PCS3c/PCS6:** see [`BUILD_QUESTIONS.md`](BUILD_QUESTIONS.md). Their omitted protocol values or incomplete executors must be reviewed before scientific execution. In particular, S2 dispatch is disabled and RQ6's prompt/parser conflict must be amended before any PCS6 run.

## Commands and estimated runtime/cost

Only commands for implemented reviewable entrypoints are listed as launch candidates. They were **not** run for full experiments. S4/S2/RQ6/PCS3c/PCS6 have no runnable scientific launch command in this build; their preflight-only paths and blockers are documented in `BUILD_QUESTIONS.md`.

| Item | Post-review command or current boundary | Planned runtime | Approximate Modal compute cost |
|---|---|---:|---:|
| MON2 full | `MODAL_PROFILE=modal-account-B modal run --detach scripts/modal_mon2_compromised_state.py` | 1.5–2 h; 4 h timeout | $1.78–$2.38 at 48 GiB |
| PCS4v4 | `MODAL_PROFILE=modal-account-B modal run --detach scripts/modal_pcs4v4_contrastive.py` | 3–4 h | $3.57–$4.75 at 48 GiB |
| W1 | `MODAL_PROFILE=modal-account-A modal run --detach scripts/modal_w1_writer_sweep.py` | 1–2 h | $1.06–$2.12 at 32 GiB |
| S4-dev | No launch command yet; launcher refuses without bridge SHA/profile custody and a resolved protocol. | <1 h | <$1.06 at 32 GiB if resolved |
| S2 | No launch command; Modal dispatch is explicitly disabled. | 1–2 h | $1.19–$2.38 at 48 GiB if completed/resolved |
| RQ6 | No inference executor/launcher; preflight only. | 2–3 h | $2.12–$3.18 assuming 32 GiB L4 |
| PCS3c | No scientific executor/launcher; preflight only. | 2–3 h | $2.12–$3.18 assuming 32 GiB L4 |
| PCS6-A | No scientific executor/launcher; preflight only. | 3–4 h | $3.18–$4.24 assuming 32 GiB L4 |
| PCS6-B | No scientific executor/launcher; preflight only. | 3–4 h | $3.18–$4.24 assuming 32 GiB L4 |

Costs use Modal's currently published L4 rate of `$0.000222/s`, CPU rate of `$0.0000131` per core-second, requested memory rate of `$0.00000222` per GiB-second, and the default 0.125 CPU core. They are planning estimates only; they exclude storage, network egress, model transfer and regional pricing differences. RQ6/PCS3c/PCS6 values assume 32 GiB because no launcher's resource request exists yet. Rates: [Modal pricing](https://modal.com/pricing).

## Execution and new-build addendum (2026-10-04)

This section supersedes earlier “blocked/preparation-only/not launched” statements where they conflict.

- **MON2 full** is detached on profile `modal-account-B`: call `fc-01M44J32EWZBVCZH2H9H0NV1R5`, runner SHA `dd1093e0e9e1738dd9bf7bafa877c8c3e282ae58f56ff276b521bc75649de9ba`, output `/artifacts/mon2-compromised-state-dd1093e0e9e1/`. This uses the G1 pinned models, the reviewed 95% source gate, and the resolved MON2 task/firewall rules. The prior bounded smoke is recorded in `evidence/mon2_gpu_smoke_resolved_2026-10-04/`.
- **W1 full** is detached on profile `modal-account-A`: call `fc-01M44J32AWYZB3GQE1TVNT09Z2`, runner SHA `f49f19039167f656c50da911c30972009c4bc0d9c19d7dabe2fee9d35a122ba3`, output `/artifacts/w1-writer-sweep-f49f19039167/`. It uses the pinned G1 models and the frozen PCS3 source features. Its sealed `W1_CHOICE.json` is a required input to PCS3c.
- **PCS4v4** remains the other authorized first-batch full run, but its current neural-only implementation is undergoing final root review and a bounded real-model smoke before its full launch. Its output namespace is separate from prior smoke output.
- **RQ7 full** completed with 1,800 episodes and `STOP_NO_CELL_PASSES`; no choice artifact exists. The full raw/result bundle and interpretation are in `evidence/rq7_full_2026-10-04/`. **PCS7** now has a tested executor and a completed bounded real-model smoke, but its scientific run is correctly gated off because the required passing RQ7 choice does not exist. Details are in `evidence/pcs7_build_2026-10-04/BUILD_REPORT.md`.
- **CAP1** has a separate post-PCS3c capture and capacity-ladder executor under construction/review. It requires a hash-sealed, completed PCS3c confirmatory handoff and cannot run its science analysis before that handoff; PCS3c currently has no completed confirmatory run to provide it. Review of original FULLSEQ token-ID custody, external capture SHA custody, weighted validation loss, and complete wrong-control coverage is in progress.
- **S2** has a completed end-to-end executor and successful bounded real-model smoke; it is not a full run. **S4** has completed its bounded real-model smoke; it is not a full run. **RQ6** executor work continues, and PCS3c/PCS6 remain downstream of W1/RQ6 and the remaining implementation gates.

No full PCS7 or CAP1 analysis was started. Apart from the two detached MON2/W1 runs above, no other full scientific job is active from this addendum.

## Commits

Implementation and evidence are separated into small commits on the requested branch:

| Commit | Contents |
|---|---|
| `b86ceaa` | MON2 fixes, tests and bounded smoke evidence |
| `370844b` | PCS4v4 contrastive path, seal/reducer, tests and smoke evidence |
| `f9afe26` | S4 preparation scaffold, local gates, tests and smoke evidence |
| `53a2e71` | S2 preparation scaffold, disabled dispatch, tests and smoke evidence |
| `71fedd7` | W1 runner/launcher, tests and CPU smoke evidence |
| `726debe` | RQ6 scoring/preflight, tests and synthetic evidence |
| `8786eae` | PCS3c scoring/preflight, tests and synthetic evidence |
| `8465388` | PCS6-A/B scoring/preflights, tests and synthetic evidence |
| `5b38e85` | Protocol questions and aggregate validation evidence |
| `b71b663` | Cross-build model-custody review blocker and refreshed PCS6 evidence hashes |

The final reviewed report is written after these implementation commits. Full-run approval is outside this handoff.
