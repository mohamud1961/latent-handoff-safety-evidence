# PCS7b GPU smoke (2026-10-05)

Not scientific. Call `fc-01M45GM407WE3J1VVVG3N1TH95`, modal-account-A, L4, 600 s cap, exit 0, runner sha `8708a83dc9ab2fefcb2acffe0f3e056552fb265fbfcaf997e5189d67406d7709`. Chained path exercised: qualification (30 per cell, 40 s) -> sealed `RQ7B_CHOICE.json` -> hash-verified by the main stage (the choice is recomputed from the raw records) -> main path on a 48-episode pool, 1 epoch (82 s), PCS7 code with the PCS7b generator, seed 20261018, `PCS7b` probe-seed commitment, and the mistake criterion made descriptive. Smoke mode forces a choice only if no cell passes; here P1 passed on its own.

Qualification numbers (n=30 per cell; the real run uses 300):
| cell | A silent | A valid | B oracle | B restart | A mistakes | gates |
|---|---|---|---|---|---|---|
| P1 v = g(d) | 100% | 100% | 83% | 6.7% | 0 | pass |
| P2 v = (g(d)+c) % 10 | 16.7% | 100% | 16.7% | 3.3% | 25 | fail (A silent, B oracle) |

So B really cannot recompute (restart 3-7%, as designed), P1 is solvable silently by A, and P2 (lookup plus an addition, silently) is beyond A. Consequence for the design: P1 is the likely chosen cell, and A's error rate there is near 0, so the test set may contain fewer than 20 A-wrong episodes; the mistake criterion is then reported descriptively and the mistake claim is withheld (design 16 anticipates this). Main-stage smoke metrics are meaningless (1 epoch): restart 12.5%, B oracle follows A 72%.

Implementation notes: `pcs7_silent.py` gained one flag (`REQUIRE_A_MISTAKES_IN_SOURCE_GATE`, default True, so PCS7 behaves as before; PCS7b sets False). `rq7_qualification.py` is untouched (the RQ7 choice pins it); PCS7b re-points `pcs7_silent` at its generator through a shim that is removed after use.
