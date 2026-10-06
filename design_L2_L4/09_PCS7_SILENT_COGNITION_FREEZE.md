# 09: PCS7 silent (unwritten) cognition transfer: FREEZE

**Claim tested.** Content that A computed **silently**, never written in any text, transfers into B and is used on a new step, including A's silent **mistakes**.

**Logic.** A answers with no written reasoning, so A's only text is the public problem. A "text handoff" is therefore identical to B restarting. If B, given A's neural state, beats that baseline and follows A's specific silent errors, the transferred content cannot have come from text.

Models: A = Qwen3-4B, B = Qwen3-1.7B, both frozen and pinned per RESOLUTIONS_1 G1. Greedy decoding.

## RQ7 qualification (inference only; run first)
**A prompt.** `chat(P + "\n\nAnswer with only the number.")` with `enable_thinking=False`. A's generated text **must be only the number**. Any other token before the number marks the episode **invalid** (counted as a failure).

**Task families × difficulty**, N = 300 per cell, seed 20261009:
| Family | Description | Cells |
|---|---|---|
| F1 add-chain mod 10 | PCS1 pilot-v2 generator, addition-only | depth 1, 2 |
| F2 two-digit single op mod 100 | `x = (37 + 48) % 100` and `x = (6 × 17) % 100` (operands 10–99, op ∈ {+, ×}) | the + and × cells separately |
| F3 table lookup composition | a 10-entry random digit map g given in P; target g(g(d)) | composition depth 1, 2 |

**Post-handoff U.** `e = (v + m) mod base`, where base is 10 for F1/F3 and 100 for F2. Train m ∈ {1–4}; held-out m ∈ {5–9}.

**B readout.** Greedy ≤ 4 tokens, parsed as an integer.

**Measured per cell:**
- A_silent (A's answer correct);
- B_restart (P + U, answer directly);
- B_restart_reason (P + U, B may reason; descriptive);
- B_oracle (`P + "\nIntermediate result: v = <A's answer>" + U`).

**Gates per cell:**
1. A_silent ≥ 80%, with valid-format ≥ 95%.
2. B_oracle ≥ 70%.
3. B_oracle − B_restart ≥ 25 pts.
4. A's silent mistakes ≥ 30 episodes, projected at full scale (N = 1,600).

**Choice rule.** Among passing cells, take the one with the largest (B_oracle − B_restart). Ties go to the lower A error rate, unless that leaves fewer than 30 mistakes. If no cell passes, stop and report. That would itself be a finding: these models' silent computation is too shallow to test.

## PCS7 main (chosen cell)
- **Data:** 1,600 fresh episodes (seed 20261010). Split train 900 / val 200 / test ≥ 400.
- **Capture:** A's hidden states at the **last 2 prompt positions** (the assistant-turn start, i.e. immediately before the first answer token). Layers 4, 8, …, 36. No trace exists.
- **Bridge:** the PCS2b architecture (4 prefix slots), or the W1 choice if available, trained 40 epochs and selected by val loss.
- **Objective by rule D1 (design 04):**
  - **D1-b default:** future loss on (A's answer + m) plus readback of A's answer, as PCS2b, with A's own answer as the target;
  - **D1-a** if L3 was reached.

**Arms:**
- PCS;
- 3 matched wrong PCS (different A answer, nearest prompt length);
- zero and random;
- B_restart;
- B_restart_reason (descriptive);
- text handoff, which is identical to restart by construction. Assert that the prompts match;
- oracle;
- token-identity ceiling (one-hot of A's answer).

## Positive criteria (test)
0. **Silence verified:** 100% of included episodes have no A-generated tokens before the checkpoint.
1. **Fidelity:** PCS fidelity to A ≥ 60% on train-m, and ≥ 50% on held-out m.
2. **Specificity:**
   - PCS − mean matched wrong ≥ 30 pts, with cluster CI > 0, plus exact McNemar;
   - **swap:** under wrong states, B follows the partner's A-answer ≥ 40%.
3. **Beats text/restart:** PCS − B_restart ≥ 20 pts.
4. **Silent-mistake fidelity:** on test episodes where A is wrong (≥ 20 episodes), PCS follows A's wrong answer ≥ mean wrong-state follow + 25 pts. Report B_restart_reason's follow rate; it is expected to be low.

**Claim if all pass.** "A silently computed result, absent from any text, transfers between frozen models through neural state and is used on new steps, including the source's silent errors."

**Limit.** These models compute only about 1–2 steps silently, so this shows *shallow* unwritten cognition. Depth scales with model size (L7).
