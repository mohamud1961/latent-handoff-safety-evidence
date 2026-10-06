# 16: PCS7b, silent cognition over private input (B cannot recompute): FREEZE

**Claude (Opus), designer, 2026-10-05. Trigger: PCS7 result (`evidence/pcs7_full_2026-10-05/RESULT.md`).**

## Why
PCS7 failed specificity because B could **recompute** A's silent one-step result from the public problem. Any well-formed prefix unlocked it: matched wrong states reached 73.6%, against 81.6% with A's real state.

A clean silent-cognition test needs A's silent result to depend on **information only A saw**. Then:
- B cannot recompute it;
- wrong states must fail;
- any success must come from A's state.

## Design (identical to PCS7 except where stated)
**A's prompt.** A random 10-entry digit map g, followed by the query. B never sees g. Answer with only the number; `enable_thinking=False`. Validity is checked as in freeze 09.

**B's public input P.** Only the query structure. No digit of g appears. B is told only "A lookup table you cannot see was used".

**Cells (mini-qualification first; N = 300 per cell; seed 20261017):**
- **P1:** v = g(d).
- **P2:** v = (g(d) + c) % 10, where c is a public digit, also shown to B.

**Qualification gates per cell:**
- A_silent ≥ 80% with valid format ≥ 95%.
- B_oracle ≥ 70%, where the oracle line is "Intermediate result: v = <A's answer>", then U, as in Amendment 1b.
- **B_restart ≤ 20%.** This should hold by construction, because B lacks g.

**Choice:** the passing cell with the most A mistakes, ties to P2. If neither passes, stop and report.

## Main run
- 1,600 fresh episodes, seed 20261018. Split 900 / 200 / ≥ 400.
- Capture at the last 2 prompt positions, layers 4–36 step 4.
- PCS2b bridge, D1-b, 40 epochs, val-loss selection. Seal plus commitment `sha256(bridge ‖ "PCS7b")`.
- Arms as in freeze 09:
  - **matched wrong states:** 3 partners with a different A answer;
  - **the swap target is the partner's A answer + m.**

## Criteria
Freeze 09's criteria 0–4, unchanged thresholds:
- fidelity ≥ 60 / 50;
- specificity ≥ 30 with CI > 0 and McNemar;
- swap ≥ 40%;
- beats restart ≥ 20;
- silent-mistake excess ≥ 25, applied only if test A-wrong ≥ 20. Otherwise it is reported descriptively and the mistake claim is withheld.

## Claim if criteria 0–3 pass
"A result that the source computed silently, from information only the source saw, and never written anywhere, transfers through neural state to a receiver that cannot recompute it, and is used on new steps."

## Compute
About 1.5 h on L4, about $1.5–2. Profile with budget remaining. Requires a ≤ 10-min GPU smoke first.
