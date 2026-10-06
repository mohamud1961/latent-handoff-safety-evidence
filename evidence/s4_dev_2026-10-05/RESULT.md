# S4-dev selective filter: sealed and audited (Claude), 2026-10-05

Run `fc-01M44PPHZC68JSHC26Z6GE8A08`, profile modal-account-A. Bridge: PCS3b ep40, C = 16, sha `575ea8df…52bf`. Test pool: 459 states from PCS3b, reused, so this is development evidence. Exit code 0. Classification: **S4_DEV_NO_POSITIVE_CLAIM**.

Belief fidelity per selector (a / b / c) on the test pool:

| Filter (target c) | a | b | c |
|---|---|---|---|
| none | 0.660 | 0.706 | 0.662 |
| **F-LEACE (rank 9), primary** | 0.381 | 0.340 | 0.115 |
| F-train (adversarial) | 0.575 | 0.654 | 0.233 |
| F-rand (random rank 9) | 0.388 | 0.390 | 0.222 |

**F-LEACE criteria.**
- Passed: c ≤ 20% ✅; c ≤ matched-wrong + 10 ✅; linear c-probe ≤ 20% ✅; a-margin ≥ 30 ✅.
- Failed: a retained ≥ 85% (58%) ❌; b retained ≥ 85% (48%) ❌; b-margin ≥ 30 ❌; random-control c-drop < 10 ❌.

**Diagnosis.** Erasing a 10-class concept needs rank 9, and that removes 9 of only 16 dimensions of C. A *random* rank-9 projection damages a and b just as much (0.39 / 0.39). So the failure is a capacity effect of the 16-dimensional C, not a property of LEACE or of entangled registers. Supporting evidence:
- The adversarial filter F-train retains a at 87% and b at 93%, and pushes c to 0.233, within 3 points of matched wrong.
- The secondary target a shows the same pattern.

**Decision.** No criterion change. S4-confirm runs as frozen on the PCS3c bridge, which W1 sets to C = 64. There, a rank-9 erasure removes 14% of the dimensions instead of 56%. This is a prediction recorded **before** S4-confirm runs: F-LEACE should then retain ≥ 85% of a and b.
