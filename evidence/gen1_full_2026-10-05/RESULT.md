# GEN1 compositional generalisation: sealed and audited (Claude), 2026-10-05 — COMP PASSES

Run `fc-01M46BY7Y5VTZT6CC9F8G6VWS4`, `modal-new-account`, runner sha `292560ea…`. Exit 0. Classification: **GEN1_COMP_PASS**.

Setup:
- PCS7b P1 regime: A has a private map g; B never sees it.
- 1,600 fresh episodes; test set 500 states.
- Source gate passed: A silent accuracy 100%, format 100%.
- Bridges sealed before evaluation: COMP `cf623acc…`, REP `d9b06740…`.

| | COMP (all m; 20 (v, m) combos held out) | REP (train m 1–4; test m 5–9) |
|---|---|---|
| **Held-out primary: PCS follows A** | **87.7%** | **80.6%** |
| Matched wrong | 0.0% | 1.6% |
| Specificity (PCS − wrong) | **+87.7 [85.5, 89.7]** | +79.0 [76.6, 81.3] |
| Swap (follows partner) | **99.9%** | 86.8% |
| B_restart / zero / random | 10.1 / 11.9 / 10.1% | 10.4 / 10.2 / 8.0% |
| Text oracle | 68.0% | 64.2% |
| Seen combos / seen m | 100% | 100% |
| Two-step unseen composition | 1.6% (below restart) | 18.6% |

**COMP criteria:** fidelity ≥ 60 ✅, specificity ≥ 30 with CI > 0 and McNemar ✅, swap ≥ 40 ✅, beats restart by ≥ 20 (+77.6) ✅.

## Audit (important nuance)
1. **The bridge carries a reusable value.** On value–update combinations never seen in training, B uses A's privately computed value 87.7% of the time with ~0% wrong-state leakage and 99.9% partner swap. That beats the *explicit text* oracle (68%).
2. **REP did NOT reproduce the earlier failure.** It generalised to unseen update values at 80.6%, versus PCS7b's 48.8% on the same regime with a different data seed. So the freeze's interpretation clause, "the near misses were a training-distribution artefact", is **not cleanly supported**. Both recipes generalise on this data.
   - The better-supported reading: the earlier unseen-update failures were **not a stable property** of the bridge. They look like **run-to-run variability** in bridge training (seed and data).
   - The memorisation objection is weakened either way: two independent bridges here generalise.
   - The variance itself is now a stated limitation and a funded-phase item: report multiple seeds.
3. **Two-step composition fails** (COMP 1.6%, REP 18.6%), but the text oracle is only 25.2% there. B cannot do the two-step mod arithmetic in this format even when told v, so this is a receiver limitation, not evidence against transfer. It is descriptive.
4. A never erred (0 A-wrong states), so mistake transfer is untested here.

## Allowed claim
"With a sealed, pre-registered held-out design, a latent bridge carries a privately computed value that the receiver uses on value–update combinations never seen in training: 87.7% fidelity, +88 pts over wrong states, 99.9% partner swap, above an explicit-text handoff."

**Licenses** (per freeze 18): PCS7c and PCS3d as new pre-registered experiments. Given note 2, multi-seed replication should be part of them.
