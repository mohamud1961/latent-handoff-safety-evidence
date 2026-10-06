# PCS7b silent cognition over private input: sealed and audited (Claude), 2026-10-05 — NEAR MISS

Run `fc-01M45GWEK0V7PMKR483VSXQAMW`, modal-account-A, runner sha `8708a83d…`, chained qualification → main.
- **Qualification:** P1 (private lookup, v = g(d)) selected; P2 failed (A silent accuracy too low).
- **Main:** 1,600 episodes, seed 20261018, D1-b, 40 epochs, bridge sealed before evaluation.

Exit 22 is the not-positive exit code. Classification: **PCS7B_NOT_POSITIVE**.

The map g appears only in A's prompt; B never sees it. A silent accuracy 100%. Silence verified.

| Criterion (freeze 16 = freeze 09 thresholds) | Value | Pass |
|---|---|---|
| 0. Silence | 100% | ✅ |
| 1. Fidelity train-m ≥ 60 / held-out ≥ 50 | **100% / 48.8%** | ❌ (held-out misses by 1.2 pts) |
| 2. Specificity: PCS − mean wrong ≥ 30, CI > 0 | **+70.6, CI [68.2, 72.9]** (PCS 74.4% vs wrong 3.8%) | ✅ |
| 2. Swap ≥ 40% | **69.1%** | ✅ |
| 3. PCS − B_restart ≥ 20 | +64.0 (restart 10.4%) | ✅ |
| 4. Silent-mistake excess | not testable: A made 0 test errors (claim withheld, as the design allows) | — |

Oracle (B told A's answer explicitly): 70.0%. Token-identity ceiling: 100%.

## Audit
1. **This fixes PCS7's confound and works.** B cannot recompute A's result (it lacks the table). Yet with A's latent state it produces A's silently computed value 74% of the time, vs 4% with wrong states.
2. **Under a partner's state, B follows *the partner's* value 69% of the time** (swap). The state carries the specific content.
3. Overall PCS (74.4%) slightly exceeds the explicit text oracle (70%).
4. **The single failure is generalisation to held-out update values** (m = 5–9): 48.8% vs the 50% bar. Train-m is 100%. The same pattern appeared in X-FAM: the bridge partly learns m-specific shortcuts.
5. A never erred on P1, so silent-*mistake* transfer is untested here.

## Allowed claim (descriptive; the pre-registered claim is not made because criterion 1 failed)
"A value computed silently by the source from private information the receiver never saw transfers through latent state with +71-point specificity and 69% partner-swap. Use on unseen update values reaches 48.8%, just under the pre-registered 50%."
