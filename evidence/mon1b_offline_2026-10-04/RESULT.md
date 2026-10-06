# MON1b offline result (2026-10-04) - gate 2 FAILED

Implements `MON1B_PRE_OUTPUT_ERROR_MONITOR_FREEZE_2026-10-04.md`. CPU only. Script: `scripts/mon1b_offline.py`. Numbers: `RESULT.json`. Data: PCS4v2 source preflight v2 cache (896 episodes, Qwen3-4B, splits 512/128/256).

**M-PCS: pending a working bridge** (Arm F bridge failed). MON1b positive criteria 1-3 are all M-PCS-dependent and cannot be assessed.

## Label and gates
- `err` = A's last written `STATE s8` triple (runner's `parse_states`) differs from symbolic truth. The checkpoint sits before `FINAL_SUMMARY:`, so the summary sentence is not in the feature text. The s8 line is written before the checkpoint. The sentence agrees with s8 in 896/896 traces, which are all parseable (0 excluded).
- Errors: train 54/512, val 17/128, test 28/256, total 99. **Gate 1 (>=60 total, >=15 test): PASS.**
- **Gate 2 (M-ACT val AUROC >= 0.70): FAIL.** Best layer by val is L32 with val AUROC 0.633. All 9 layers are in 0.53-0.63. Per the freeze this means stop and report. The test numbers below were computed anyway by the script, so they are descriptive, post-gate-fail, and not a claim.

## Test results (n=256, 28 errors; 95% bootstrap CI over episodes, 2000 resamples)
Balanced accuracy (bacc) uses the val-chosen threshold. M-TEXT's threshold is fixed at "any inconsistency". Precision at 80% recall is abbreviated P@R80. Base rate is 0.109.

| Monitor | val AUROC | test AUROC | test bacc | test P@R80 |
|---|---|---|---|---|
| M-ACT best layer by val (L32) | 0.633 | 0.613 [0.47,0.76] | 0.581 [0.49,0.68] | 0.112 [0.08,0.17] |
| M-ACT L4 / L8 / L12 | 0.597 / 0.620 / 0.536 | 0.564 / 0.561 / 0.534 | 0.53 / 0.55 / 0.50 | 0.12-0.13 |
| M-ACT L16 / L20 / L24 | 0.526 / 0.547 / 0.616 | 0.614 / 0.625 / 0.612 | 0.56 / 0.56 / 0.53 | 0.12-0.16 |
| M-ACT L28 / L36 | 0.590 / 0.565 | 0.649 / 0.651 | 0.63 / 0.59 | 0.12 / 0.13 |
| M-ACT multipos, best single (position, layer) by val: s7_line_end, L36 | 0.775 | 0.658 [0.53,0.77] | 0.605 [0.51,0.69] | 0.139 [0.09,0.24] |
| M-ACT multipos, 10 positions concatenated, best layer by val (L24) | 0.691 | 0.673 [0.56,0.78] | 0.627 [0.54,0.72] | 0.142 [0.10,0.23] |
| M-PUBLIC (program structure) | 0.439 | 0.569 [0.46,0.68] | 0.535 | 0.126 |
| M-PUBLIC-SYM (truth-based difficulty) | 0.677 | 0.465 [0.35,0.58] | 0.424 | 0.113 |
| M-TEXT (recompute each step; flag if any STATE line is inconsistent) | n/a | **0.975 [0.96,0.99]** | 0.976 [0.96,0.99] | 0.718 [0.58,0.86] |
| M-MAJ | n/a | 0.500 | 0.500 | n/a |
| Shuffled control (M-ACT L32, 5 permutations) | n/a | 0.29, 0.34, 0.31, 0.67, 0.44 | first seed 0.38 | 0.109 |

Test AUROC CI width is about 0.3 for the activation monitors. M-ACT confidence intervals include 0.5 for L4-L12 and L24, and approach 0.5 for the others.

## Findings
- **The activation signal at the checkpoint is weak or absent.** Test AUROC is about 0.6 with CIs near 0.5, and no layer clears gate 2 on val. Multi-position features (downloaded, 408 MB, sha256 matches the manifest) peak at val 0.775 for a single cell, and 0.69 for the concatenation. Both are selected over 90 or 9 candidates on only 17 val errors, so this is likely selection noise. Their test AUROC is 0.66-0.67, and the CI lower bounds are 0.53-0.56.
- **Public baselines are at chance on test.** M-PUBLIC is 0.57 and M-PUBLIC-SYM is 0.47, so the errors are not explained by program-structure difficulty.
- **M-TEXT is near-perfect, and this is a caveat rather than a win.** Every error episode (99/99) contains a written step that is inconsistent with A's previous written state, so errors here are arithmetic slips visible in text. The text includes the s8 line that defines the label, which is the same leakage the freeze flagged for MON1 v12. M-TEXT is descriptive only, as the freeze states.
- **The shuffled control is not exactly 0.5.** Seeds range 0.29-0.67 around a chance level of 0.5, which is consistent with n_err=28 noise.
- **The multipos checkpoint slice differs from the single-position tensor.** The max absolute difference is 0.44 (fp16 and batching effects). I used each file as given.

## Choices not fixed by the freeze
- Logistic regression: standardise on train, `class_weight=balanced`, C grid 1e-5..1, C selected by val AUROC.
- M-PUBLIC features: initial values, per-register target and source counts, operation counts, constant histogram, and per-step op and rhs kind.
- M-PUBLIC-SYM features: multiplication counts, carry counts, zero results, backward-slice size, and truth s8 summaries.
- Position and layer selection for multipos is by val AUROC.
