# COGMON1 read → predict → intervene at the handoff: sealed and audited (Claude), 2026-10-05 — MIXED

Run `fc-01M46QVYY7VG3K8ZK3X9011AGP`, `modal-new-account`, runner sha `97bdae46…`.

Setup:
- Sealed PCS3c bridge `317b1ff3…`, source bundle `23d09853…`, handoff manifest `90e479c5…`, all verified.
- Monitor fitted on train/val only and sealed before test.
- 959 test states.

Classification: **MIXED**.

| Stage | Result | Criterion |
|---|---|---|
| **Read** (A's three registers from the handoff, before B acts) | balanced accuracy a 62.0 / b 62.4 / c 62.5% (chance 10%); all three jointly 38.8% | ✅ |
| **Predict** (B's actual answer, before B runs) | 50.3% vs the "B = A's value" baseline at 58.0% (−7.6 [−10.1, −5.2]); P-only 26.3% | ❌ |
| **Intervene: on target** (edit register r, then B reports the new value) | **46.2% vs random-direction 4.9%** (+41.3 [39.3, 43.3]); McNemar 1,230 vs 41 | ✅ |
| **Intervene: off target** (the other registers unchanged) | 47.6% preserved vs random 79.7% | ❌ |

## Audit
1. **Read: yes.** Several independently varying properties of A's state can be recovered from the transferred handoff object before the receiver acts, at about 6× chance.
2. **Steer: yes, but not selectively.** A targeted edit moves B's answer for that register to the chosen new value 46% of the time, vs 5% for a same-norm random edit. That is a causal handle on transferred state. But the edit **disturbs the other two registers** (47.6% preserved vs 79.7%). The three registers are entangled in the 64-dim handoff, matching S4-dev's finding that selective removal is hard at this bridge size.
3. **Predict: no.** A linear monitor on H does not predict B's actual answer better than simply assuming B will report A's value. Its errors come from B's imperfect decoding (PCS3c fidelity 58%), which the linear monitor does not capture.
4. Implication: **selective, side-effect-free control is the open problem.** That is precisely Stage II's "selective inheritance" workstream.

## Allowed claim
"The transferred handoff state is readable (three independent properties at about 6× chance) and causally steerable: a targeted edit changes the receiver's corresponding answer 9× more often than a random edit. But edits are not yet selective (they disturb other properties), and a linear monitor does not predict the receiver's behaviour beyond a simple baseline."

The full "observable and selectively controllable" claim is **not** made.

**Stop rule:** COGMON1 is mixed. Per `PRE_GRANT_STOP_RULE_OPUS.md`, no COGMON2 before applying.
