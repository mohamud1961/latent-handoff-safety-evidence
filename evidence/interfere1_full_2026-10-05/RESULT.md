# INTERFERE1 inherited vs resident cognition: sealed and audited (Claude), 2026-10-05 — CONTRAST 1 PASSES

**Runs.**
- First attempt `fc-01M454YCY811G592NBPB0GWCW4` crashed in exact McNemar (overflow) and wrote no results. Its exit code is preserved.
- **Rerun `fc-01M45FV2ZW7Y1G7VNMC7HMR0EB`** with the fixed contract. Inference only, so a rerun is identical by construction.

Setup: modal-account-A. Sealed PCS2b bridge `87de8fb8…` and cache `42f419d6…`, verified in the container. 256 sealed test states, 43,520 queries. Classification: **INTERFERE1_CONTRAST1_PASS**.

## Outcome table (rate of B's answer following A's value / the wrong state's value / the note)
| Prefix \ note | none | weak conflict | strong conflict ("Verified: v = X") | strong agree ("Verified: v = v_A") |
|---|---|---|---|---|
| **A's state** | 88.7 / 1.7 / 1.3 | 62.7 / 2.5 / 17.1 | **66.0 / 2.7 / 15.2** | 88.5 / 2.0 / 1.5 |
| **wrong state W** | 2.0 / 86.9 / 1.3 | 2.5 / 62.3 / 18.3 | 2.1 / 66.1 / 16.1 | **16.4 (A, true) / 66.4 (W)** / 2.0 |
| zero prefix | 12.0 / 10.0 / 9.2 | 9.3 / 9.1 / 19.1 | 7.9 / 6.9 / 35.6 | 40.7 / 6.9 / 6.4 |

- **Contrast 1, residual inheritance under explicit conflict:** follow-A with A's prefix vs W's prefix = 66.0% vs 2.1%. **Δ = +63.9, CI [61.1, 66.5]**, McNemar 1,656 vs 21. ✅
- **Contrast 2, text override:** a verified conflicting note lowers follow-A from 88.7% to 66.0% (−22.7, CI [20.2, 25.3]). B follows the note in only 15.2% [13.7, 16.7].
- **Reinforcement:** a true note adds nothing (−0.2, n.s.).
- **Blend curve** (λ·A + (1−λ)·W): graded, with a crossover near λ = 0.5. There, 31.7% of answers follow neither source (incoherence).

## Audit and interpretation
1. **Inherited cognition dominates explicit resident text.** Told "Verified: v = X", B still acts on the inherited state about 4× more often than on the verified text.
2. **Most striking: inherited state overrides *true* explicit information.** When the prefix is a wrong state and the note correctly states A's value, B follows the wrong inherited state 66.4% of the time and the true text 16.4%. A text-level correction does not reliably fix a bad inherited state.
3. **By query type:** future queries (B applies an update) follow A 71.4% under conflict. Readback queries ("what is v?") follow A only 18% and lean more toward the note. Inherited state drives *use in computation* more than *stated belief*. This is worth noting: a receiver may *say* the text's value while *acting* on the inherited one.
4. **Mixing two sources yields incoherence** (32% neither at λ = 0.5), not a clean average.

## Allowed claim
"When a receiver's explicit, verified context conflicts with an inherited latent state, the inherited state largely governs the receiver's computations (+64 pts, CI [61, 67]), even when the explicit text is correct. Text-level instructions do not guarantee control over inherited cognition."
