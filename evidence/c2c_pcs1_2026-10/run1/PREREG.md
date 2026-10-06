# PREREG: Does the C2C bridge transfer the sharer's beliefs, or just help?

Written 2026-10-01, before any result exists. Not edited after the first run; deviations are logged in `results.json["deviations"]`.

**Setup (fixed).** Cache-to-Cache (C2C, arXiv 2510.03215, code pinned at commit `3ca0e98`). Receiver Qwen3-0.6B, sharer Qwen2.5-0.5B-Instruct, released fuser `nics-efc/C2C_Fuser/qwen3_0.6b+qwen2.5_0.5b_Fuser/final`. Greedy, seed 0, no CoT, no thinking. Every condition uses C2C's own prompt builder and the same readout: argmax over the four letter logits (" A".." D") after "The correct answer is" (C2C `answer_method: logits`). Ties go to the lower letter.

**Question.** On items where sharer and receiver alone disagree, does the fused receiver adopt the *sharer's* answer even when that answer is wrong (belief transfer), or does it behave as a generic helper?

## Part A: plumbing (not a hypothesis test)
200 random OpenBookQA test items. Receiver, sharer, C2C under (i) the paper's protocol (generate <=64 tokens, C2C `extract_answer_from_content`) and (ii) the logit readout. Paper (Table 4, N=500): 39.2 / 45.6 / 52.6. **Plumbing OK** iff no non-finite logits AND C2C beats receiver alone with a paired-bootstrap 95% CI excluding 0 under the generation readout AND Rosetta-with-projection-off matches plain receiver argmax on >=95% of items. If not OK, Part B is uninterpretable and is flagged as such.

## Part B: fidelity test (the experiment)
**Items (N=2000, fixed seeded sample):** 1000 MMLU-Redux (C2C's filter: drop `no_correct_answer`/`expert`; use corrected key for `wrong_groundtruth`), 600 ARC-Challenge test (4-option items), 400 OpenBookQA test. Items longer than 1536 prompt tokens are dropped (C2C trained at <=2048). Reserve of +1000 MMLU-Redux is used only if a cell below has <150 items.

**Per item:** R receiver alone; S sharer alone fed the exact tokens the fuser feeds it; S_nat sharer with its own chat template (sensitivity only); C C2C-fused; C_mm C2C with the sharer cache computed on a *different same-length prompt* (null for "any cache perturbation"); T text handoff "Another model answered: X" (X = S's letter); T2 same plus the sharer's own one-sentence rationale. C_mm, T and T2 are computed only on D; C_mm only for items with an exact-length partner prompt (coverage is reported).
**Disagreement set** D = {S != R}, split into A (S right, R wrong), B (S wrong, R right), W (both wrong, different). Need |A|,|B| >= 150.
**Metrics (bootstrap 95% CI, 10,000 resamples over items; paired where conditions share items):**
- Inh(X|cell) = P(X == S). Inh(R) = 0 on D by construction, hence the null C_mm.
- **Primary: E_B = Inh(C|B) - Inh(C_mm|B)** (sharer wrong, receiver right). Secondary: E_A, E_W, E_{B+W}.
- Truth-tracking asymmetry Inh(C|A) - Inh(C|B); bridge/text ratio E_B / Inh(T|B).
- Accuracy of R, S, C, C_mm, T overall and on D.

**Reading (thresholds fixed now):**
| Outcome | Meaning |
|---|---|
| lower CI of E_B >= 0.10 | **Belief transfer**: receiver abandons a correct answer for the sharer's wrong one beyond null. Larger if E_A is similar (correctness-blind). |
| E_B upper CI < 0.10 and E_A >= 0.10 | **Truth-biased helper**: follows the sharer only when it is right. Carries competence, not beliefs. |
| E_A, E_B CIs inside +/-0.05 and the paired CI of acc(C) - acc(C_mm) on D includes 0 | **Non-specific perturbation**: any accuracy gain is not about the sharer's content. |
| anything else | Mixed or underpowered; no claim. |
With n=150 per cell, CI half-width is about 0.08, so effects below ~0.08 are not resolvable.

## Part C: planted belief (exploratory)
500 items from Part B. A random wrong letter w is planted: the sharer sees "Reference note: the correct answer to the question below is w." before the question; the receiver sees masked padding of equal length (C2C's own alignment mechanism), so it never sees the premise. Control: sharer sees the same note with "X". Delta_bridge = P(C_plant == w) - P(C_ctrl == w), on items where the sharer itself adopted w (S_plant == w and S_ctrl != w). Text reference Delta_text: receiver is told the note directly. Lower CI of Delta_bridge >= 0.05 means the bridge carries sharer-private information. The fuser was trained only on identical inputs, so this is out-of-distribution; a null does not refute the main result.

## Known limits
Weak near-chance models; accuracy is 35-45%, so many "beliefs" are noise. One pair, one fuser. Logit readout differs from the paper's generation readout (Part A reports both). fp16 on a T4 is gated by a sanity check against fp32 and falls back to fp32.
