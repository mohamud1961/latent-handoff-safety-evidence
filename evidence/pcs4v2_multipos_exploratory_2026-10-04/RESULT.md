# PCS4v2 exploratory result: NULL (bridge training failure)

Kernel: Modal `modal-account-B`, call `fc-01M42R7Z601T4PBTCHBP2V87V5`. Label: EXPLORATORY (see `PCS4V2_EXPLORATORY_DEVIATION_2026-10-04.md`). 1,378 sealed probes.

| Category | Arm F (neural, label-free) | Wrong states | Zero | Text oracle | Private trace text | Public only |
|---|---|---|---|---|---|---|
| Derived beliefs (n=768) | 7.7% | 7.7% | 7.2% | 100% | 82.3% | 19.1% |
| Source mistakes (n=98) | 2.0% | 2.0% | 4.1% | 100% | 87.8% | 16.3% |
| Post-freeze equality (n=256) | 31.2% | 29.8% | 76.6% | 70.7% | 73.4% | 61.3% |
| Post-freeze shift+1 (n=256) | 14.5% | 14.5% | 14.5% | 94.5% | 45.3% | 23.0% |

The token-identity Arm F is equally null. Arm T is not probed on its own target.

**Reading.** Arm F's outputs equal the zero-state outputs, so the trained prefix carries no usable state. Even the token-identity input, which is perfect information, fails. Stage B trained only 6 epochs for Arm F, with the best epoch 4.

This is a **writer/training failure**: label-free trace regeneration through K=4 slots did not learn. It is **not** evidence about source cognition. The source and receiver gates passed, and the private-trace text arm reaches 82–88%.

Consistent with PCS3 (`PCS3B_TRAINING_BUDGET_AMENDMENT_2026-10-04.md`): a multi-value prefix writer needs more training or capacity. PCS4v2 is held until PCS3b shows whether the training budget alone fixes the writer.
