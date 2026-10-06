# PCS7 silent-cognition transfer: sealed and audited (Claude), 2026-10-05

Run `fc-01M4519Q2CMZMZ86Z5RPQPKQ4D`, profile modal-account-B, runner sha `d8235468…`. Cell F1_add_depth1 (RQ7 v2 choice, sha verified), D1-b, 40 epochs. Bridge sealed before evaluation (`PCS7_EVAL_SEAL.json`). Exit 22 is the not-positive exit code. Classification: **PCS7_NOT_POSITIVE**.

Test set: 500 states, 1,000 queries. A silent accuracy 90%, 50 A-wrong test states. Silence verified 100%.

| Criterion (freeze 09) | Value | Pass |
|---|---|---|
| 0. Silence | 100% | ✅ |
| 1. Fidelity: train-m ≥ 60%, held-out ≥ 50% | 84.2% / 79.0% | ✅ |
| 2. Specificity: PCS − mean wrong ≥ 30 | **+8.0**, CI [6.0, 10.1] | ❌ (CI > 0; McNemar p < 1e-10 for 2 of 3 partners, p = 0.09 for the third) |
| 2. Swap ≥ 40% | 4.7% | ❌ |
| 3. PCS − B_restart ≥ 20 | +72.2 | ✅ |
| 4. Silent-mistake excess ≥ 25 (n = 50 ≥ 20) | 23% vs 15% = +8 | ❌ |

## Audit: why it failed (the key finding)
**Matched wrong states make B produce A's answer 73.6% of the time**, versus 81.6% with A's real state and 9.4% with no prefix (restart). So the trained prefix mainly acts as a **task-enabling soft prompt**. With any well-formed prefix, B computes the one-step mod-10 sum itself. B's direct-answer restart readout is near chance without a prefix.

The RQ7 gate (oracle − restart ≥ 25) assumed restart measures B's own ability, but B can solve this cell when suitably prompted. So "beats restart" (criterion 3) is not evidence of transfer here. Specificity is the real test, and it is small: **+8 points of A-specific content, significant (CI > 0), far below the pre-registered 30**. A's silent mistakes pass on weakly: +8 points.

## Allowed claim
"A small but statistically significant amount of A-specific silently computed content (+8 pts over matched wrong states) crosses through the neural state. Most of the apparent transfer on this task is non-specific: the receiver can recompute the answer."

The pre-registered silent-cognition claim is **not** made.

## Lesson for design
A silent-cognition test needs a task where **B cannot recompute A's result from the public input**, for example when A's silent computation depends on private information only A saw. This is the same non-specificity trap PCS1 found in C2C. The causal controls caught it, which is what they are for.
