# RQ7 / PCS7 Amendment 1b: B prompt construction (Claude/Opus), 2026-10-05

## Basis
RQ7 v2 smoke (`evidence/rq7_v2_gpu_smoke_2026-10-05/RQ7_RAW.jsonl`).

The B arms embed A's full question ("What is the final value of a?") before the post-handoff question. B then answers the **original** question:
- F3 B_oracle outputs A's value v itself (6 → 6, 7 → 7), not (v + m);
- F2 collapses to `07`.

The RQ1 and PCS2b receiver format, which reached about 78% oracle, never included A's question.

## Change (B arms only; A unchanged)
For every B arm (oracle, restart, restart_reason, and PCS7 PCS/wrong/zero/random), **P_B = the task's statement lines without A's final question line**. Use the RQ1/PCS2b phrasing:

- **oracle:** `P_B + "\nIntermediate result: v = <A's answer>\n\nNow e = (v + <m>) % <base>. What is e? Answer with <one digit | two digits>."`
- **restart:** `P_B + "\n\nLet v be the value asked for above. Now e = (v + <m>) % <base>. What is e? Answer with <…>."`
  - For F1/F3, "the value asked for above" is restated as "let v be the final value of <var>" or "let v = g(g(d))". The question's target stays explicit, but it is never asked as a question.
- **PCS arms:** `P_B + [prefix] + "Now e = (v + m) % base. What is e?…"`, with v defined as in restart.

The readout is unchanged from Amendment 1: pre-fill `The answer is ` and read digit logits.

## Before the full run
- Rerun the ≤10-minute smoke.
- **Proceed to the full RQ7 v2** only if the smoke shows B-oracle accuracy ≥ 50% on F3 depth 1 (n ≥ 10). That is a sanity check, not a gate.
- Otherwise report back.
