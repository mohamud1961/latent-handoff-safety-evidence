# Results: C2C fidelity test, run 3 (2026-10-02)

Kaggle T4, fp16, 147 min, $0. Kernel `kaggle-user/pcs-c2c-fidelity-run3`. Raw output in `run3/kaggle_out/`.
PREREG_run3.md sha256 `c4f81b1a…565a4`, frozen before push.
Pair: sharer Qwen3-4B → receiver Qwen3-0.6B, released general fuser (the paper's own pair).

## Pre-registered results
- **Plumbing: OK.** Reproduces the paper on OBQA (gen readout):

  | | Ours | Paper |
  |---|---|---|
  | Receiver | 35.0 | 39.2 |
  | Sharer | 77.5 | 79.4 |
  | C2C | 55.5 | 55.2 |

  All paper values fall inside our CIs.
- **MC set (N=2800, logit readout):**

  | Condition | Accuracy |
  |---|---|
  | R | 37.7 |
  | Rcal (calibrated receiver, no sharer) | 47.8 |
  | C_mm (3 wrong-question caches) | 46.1–48.0 |
  | C2C | 51.8 |
  | S | 77.0 |

  - **Δ_specific = C − mean C_mm: +5.4 pts [+4.3, +6.4]**; +6.8 on the disagreement set. It holds after calibrating both (+5.3).
  - C − Rcal = +4.0 [+2.0, +5.9].
  - C agrees with each wrong-question cache on ~85% of items.
- **Belief inheritance (cell B, sharer wrong / receiver right, n=173):** C2C adopts the sharer's wrong answer 36.4% of the time vs 30.4% for the null. Excess +5.8 [+1.2, +10.5].
- **Planted false belief (exploratory):**
  - Sharer effect: +35.6 pts.
  - Bridge effect: +2.8 [+1.4, +4.4], or +4.5 on sharer-susceptible items. It is below the pre-set 0.05 bar, so it is labelled "no detectable transfer", but its CI excludes 0.
- **Numeric task (GSM8K exact answer, n=145; the soft deadline cut the target of 300):**

  | Condition | Accuracy |
  |---|---|
  | R | 46.9 |
  | S | 60.0 |
  | C2C | 40.7 |
  | Wrong-question cache | 42.8 |

  - C − C_mm −2.1 [−9.7, +5.5].
  - No numeric inheritance: P(C's number = S's number) equals the null.
  - Verdict: null (underpowered).
- **FINAL pre-registered reading: PARTIAL, some genuine transfer; accuracy overstates it.** The MC task passes the content bar; the numeric task does not corroborate it.

## Reading
For the paper's own strong→weak pair, the bridge's +14.1-pt MC gain splits into:
- **~10 pts generic**, matched by a label-free letter-prior calibration of the receiver alone, and by C2C fed a wrong question's cache;
- **~5 pts question-specific**, the real communication. That is about 14% of the 39-pt receiver→sharer gap.

Other comparisons:
- **Text with rationale beats the bridge.** On the disagreement set, a text handoff with the sharer's one-sentence rationale scores 46.6% vs C2C's 41.3%.
- **The bridge hurts math.** In free-form math generation the bridge lowers accuracy and shows no sign of carrying the sharer's answer.

Post-hoc note: wrong-question caches pull the receiver toward the *partner's* sharer letter at 28.4% vs 25% chance. Part of the specific signal may therefore be the sharer's answer-letter preference rather than richer question understanding.

## Across runs 1–3
| Pair | C2C − R | Generic part (≈ Rcal / C_mm) | Question-specific Δ |
|---|---|---|---|
| 0.5B → 0.6B | +9.5 | all of it | ~0 |
| 1.5B → 1.7B | −5.4 | all of it (hurts) | +0.7 |
| 4B → 0.6B | +14.1 | ~10 | **+5.4** |
