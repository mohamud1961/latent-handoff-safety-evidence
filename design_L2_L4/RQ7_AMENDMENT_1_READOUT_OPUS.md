# RQ7 / PCS7 Amendment 1: answer readout (Claude/Opus, designer), 2026-10-05

## Basis
`evidence/rq7_full_2026-10-04/RQ7_DIAGNOSIS.md`. RQ7 v1 stopped (`STOP_NO_CELL_PASSES`) because of a **design flaw in the readout**, not a harness bug and not silent-cognition capacity:
- Both models open with prose ("We are given…") despite "Answer with only the number."
- B's 4-token readout never reached a number: 0/319 oracle and 0/1,800 restart outputs began with a digit.
- A's strict format gate measured instruction-following, not silent computation. Where A did comply, it was accurate: F3 depth 1 was 91.9% correct among 234 valid answers.

## Change (readout only; everything else in design 09 is unchanged)
1. **Answer anchor for every model call** (A, and all B arms). Generation starts from the assistant turn **pre-filled** with `The answer is `, using the chat template with `enable_thinking=False`.
2. **Digit-restricted readout** (the PCS2b method):
   - **Base 10 (F1/F3):** argmax over the digit tokens `0`–`9` at the first position.
   - **Base 100 (F2):** argmax over digit tokens at position 1, append it, then argmax over digit tokens at position 2. A two-digit answer is required, because operands are 10–99 and results are taken mod 100 with zero-padding: the prompt states "answer as two digits", e.g. `07`.
3. **Silence.**
   - A writes **no tokens** before the answer digit. The pre-fill is fixed text identical across episodes and contains no task content.
   - The freeze's "valid format ≥ 95%" gate is replaced by **gate 0′**: the A checkpoint is the last pre-fill token, and A has generated 0 free tokens. This holds by construction, and the code asserts it.
   - **PCS7 capture** is A's hidden states at the last 2 positions of the pre-filled prompt, i.e. immediately before the answer digit.
4. **B_restart_reason (descriptive only):** cap 256 tokens, then pre-fill `\nThe answer is ` and read digits as in point 2.
5. **Unchanged:**
   - gates 1–4 thresholds (A_silent ≥ 80%; B_oracle ≥ 70%; oracle − restart ≥ 25; ≥ 30 projected mistakes);
   - the choice rule, N, seeds and families;
   - all PCS7 main criteria.

## Run status
- **RQ7 v1:** stays sealed as `STOP_NO_CELL_PASSES (readout design flaw)`.
- **RQ7 v2:** runs with this amendment under a new code SHA.
- **One rerun only.**
