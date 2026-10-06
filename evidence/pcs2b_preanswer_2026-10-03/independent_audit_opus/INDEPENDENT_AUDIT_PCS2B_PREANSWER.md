# Independent audit: PCS2b pre-answer state realization

Auditor: Claude (Opus), acting as independent auditor. ChatGPT is the executor.
Date: 2026-10-03.
Kernel: `kaggle-user/pcs2b-preanswer-state-realization`. Outputs were fetched once, directly from Kaggle.

Method:
- I re-implemented every metric in `audit_preanswer.py`. The executor's `pcs2b_audit.py` was not used.
- I rebuilt the wrong-state partners from the source cache.
- I added three analyses the executor did not report:
  - which belief the receiver follows under a wrong state;
  - a per-layer linear probe;
  - a check of what the source trace already contains.

## Verdict

**The core causal claim survives:** a Qwen3-4B neural state, translated into 4 prefix slots, makes frozen Qwen3-1.7B act on *A's* belief.

**Two framings must be narrowed** before this goes to funders (details below):
1. The transferred content is a value A had already written in its private trace, not unwritten cognition.
2. "PCS beats text" is not supported by this run.

## Checks that passed
| Check | Result |
|---|---|
| Custody | All 4 files match `PCS2B_RUN_MANIFEST.json` sha256 (results, source cache, bridge, runner) |
| Split integrity | train/val/test share 0 ids and 0 problem texts; all 2,304 records are test-split |
| Held-out interventions | m=5..9 never used in training or model selection (val loss uses m=1..4 only; verified in runner code) |
| Record consistency | 0 rows disagree with the source cache on A_belief, X or targets |
| Checkpoint | for every test state, A's next-token argmax at the checkpoint is the answer token |
| Headline recomputation | every number reproduces exactly (table below) |

## Recomputed results (state-cluster bootstrap, 10k resamples, 256 states)
| | All m (2,304 rows) | Held-out m=5..9 (1,280 rows) |
|---|---|---|
| PCS fidelity to A | 87.41% [85.46, 89.41] | 77.34% [73.83, 80.94] |
| Exact-state text oracle | 76.35% | 69.53% |
| Wrong states (3) | 2.17 / 2.73 / 1.95% | 3.91 / 4.92 / 3.52% |
| Zero / random prefix | 12.07 / 11.81% | 13.28 / 12.66% |
| Restart | 12.98% | 14.22% |
| Readback | 100% | 100% |
| **Δ_specific (PCS − mean wrong)** | **+85.13 [+83.23, +87.05]** | **+73.23 [+69.82, +76.69]** |

## New evidence: the strongest causal test in the run
The wrong-state partners are well matched:
- same target variable in 100% of cases;
- mean checkpoint-length difference of about 3.7 tokens;
- a different belief by construction.

**Given a partner's state, B outputs the partner's belief-implied answer 84.5–86.3% of the time** (control 0: 85.46%, 1: 84.51%, 2: 86.33%).

So the receiver doesn't just get worse with a wrong state. **Swapping the source state swaps B's answer to the source's value.** That is direct evidence the bridge carries A-specific content. The executor did not report this.

Source-mistake fidelity reproduces:
- On the 15 states where A was wrong, PCS follows A's wrong belief in 84.44% [74.81, 93.33] of rows and hits the truth in only 4.44%.
- Caveat: n=15 states, hence the wide interval.

## Required claim corrections

### 1. What is transferred is a value A had already written down, not unwritten cognition
- In **98.8% (253/256)** of test states, the last computed result in A's private trace, e.g. `b = (0 + 8) % 10 = 8`, already equals A's belief before the checkpoint. The checkpoint is the token before the final digit of `Final: b = <digit>`.
- A linear probe decodes A's belief from the checkpoint state at **100%** from layer 24 upward, and at 74–90% even at layers 4–20.

So the source state encodes a scalar A has just computed, written in its private context, and is about to emit. That is neural-to-neural transfer B never sees as text, which makes it a real result. But it is "transfer of A's committed working-memory value", **not** pre-verbal or unwritten cognition. The authority doc's "pre-final-answer-token, not pre-linguistic" wording is right and should be kept.

**Funder-facing wording:**

> "A frozen receiver can be made to hold and use a source model's committed internal belief, including its errors, via a learned 4-slot neural prefix."

### 2. "PCS beats text handoff" is not supported here
- **The text-trace arm is not a fair baseline.** It scores 26.6% even though the trace contains the answer. That looks like receiver format confusion (the trace holds many variable values), not a measure of text handoff. Do not cite PCS 87% vs text 27%.
- **The fair comparator is the exact-state text oracle.** PCS beats it by +11.07 pts [+8.81, +13.37], and by +7.81 [+4.77, +10.94] held-out.
- **The gap is probably not "latent carries more".** The bridge is trained end to end against B, so its slots can also act as a learned soft prompt that improves B's arithmetic. The oracle prompt gets no such tuning.
- **A missing control would separate the two:** a soft prompt trained the same way but without source state, combined with the text oracle. Until that runs, state the result as "PCS matches or exceeds an explicit-value text oracle".

### 3. Supervision
The bridge is trained on A's parsed belief, through readback and future targets. This is stated correctly in the authority doc. PCS4 (label-free, sealed unanticipated probes) remains the necessary next step.

## Reproduce
```
# raw files: kaggle kernels output kaggle-user/pcs2b-preanswer-state-realization -p raw/
python audit_preanswer.py        # needs torch (CPU ok); prints AUDIT_OUTPUT.txt sections 1-6
```
- The trace check (section 7 of `AUDIT_OUTPUT.txt`) is a short inline analysis of `A_trace` in the source cache: the last `= <digit>` before `Final:` is compared with `A_belief`.
- `pcs2b_results.json.gz` is the raw results file, sha256 `07fd9ad6…e230be558` when uncompressed.
- The 42 MB source cache is not committed. It is identified by its manifest hash.
