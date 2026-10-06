# RQ6 Amendment 2: receiver prompt parity and pre-registered retry ladder (Claude, designer), 2026-10-05

**Trigger.** The receiver probe (`evidence/rq6_build_2026-10-04/receiver_probe_2026-10-05/PROBE_REPORT.md`, call `fc-01M44ZKPSS1CB47YTZ1CVSG9TS`) shows B-oracle fidelity of 16.7% against the 70% gate. B copies the supplied s8 state into s9–s11 and writes no calculation lines. In RQ7, B solved one-step problems at 100% when allowed to reason. So this is a **prompt/behaviour** failure of B in this format, not proof of incapacity.

The diagnosis: A's source prompt includes a worked example of the required style; B's prompt has none.

**This amendment changes the receiver prompt only.** Gate thresholds, splits, seeds and every PCS6 criterion are unchanged. RQ6 is a qualification step, so receiver-format fixes are legitimate here, before any test data exists.

## Ladder (probe on 32 generated D=11 episodes, seed 20261006, indices 0–31; oracle_state + restart; stop at the first rung with oracle ≥ 70%)
- **R1, prompt parity.** B receives **A's own source prompt template** (the PCS4v2 amendment-1 prompt generalised to D, *including its worked example*), with the program numbered as in the current pin. Then the handoff content (oracle line, partial text or prefix). Then: "Continue from update 9. For each remaining update write ONE short calculation line, then the STATE line, exactly as in the example. Then FINAL_SUMMARY:". `enable_thinking=False`. Receiver cap raised to 200 tokens.
- **R2, R1 plus pre-registered M = 2.** D = 10, so B applies only updates 9–10. This is the original design-04 retry, per RESOLUTIONS_1.
- **R3, R2 with B thinking allowed.** `enable_thinking=True`, cap 600 tokens. The parse reads only the text after `</think>`. The thinking trace is recorded but never scored. This applies **identically to all receiver arms**, including restart and PCS, so the comparison stays fair. The claim wording becomes "B continues A's state with its own reasoning".

## Decision
- **First rung with oracle ≥ 70%:** pin it in `RQ6_PROTOCOL.json` and run full RQ6 with it.
- **No rung passes:** RQ6 = STOP_RECEIVER_INCAPABLE. That is a finding: "a 1.7B receiver cannot continue multi-step state updates from an explicit handoff in this format". PCS6-A moves to the post-grant scale phase (a larger receiver). PCS6-B (GSM8K) stays exploratory and runs only if its own RQ6 GSM8K gates pass.

**Cost:** three probes of ≤ 10 min each.
