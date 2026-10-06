# W1 writer sweep: sealed and audited (Claude), 2026-10-05

Run `fc-01M44J32AWYZB3GQE1TVNT09Z2`, profile modal-account-A, artifacts at `pcs-core-artifacts:w1-writer-sweep-f49f19039167/`. Exit code 0. Development data only: val n = 128 states × 3 selectors.

| Config | K | C | dropout | Neural val fidelity (a / b / c) | Token-identity val fidelity |
|---|---|---|---|---|---|
| W1-a | 4 | 16 | 0 | 66.1 (75.0 / 57.8 / 65.6) | 93.2 |
| **W1-b** | 4 | 64 | 0 | **71.1** (76.6 / 68.8 / 68.0) | 90.9 |
| W1-c | 8 | 64 | 0 | 57.8 (62.5 / 53.9 / 57.0) | 98.7 |
| W1-d | 8 | 64 | 0.1 | 39.6 (43.8 / 29.7 / 45.3) | 97.9 |

**Audit.**
- The mechanical rule (design 01 Part A) was applied correctly. W1-b has the highest neural val fidelity and no other config is within 1 point.
- Its token-identity fidelity is 90.9% ≥ 90%, so there is no WRITER_CEILING_FLAG.
- Choice sealed: `W1_CHOICE.json`, choice_seal_sha256 `0785f4ab…99af3`.
- Observation: more slots (K = 8) help the token-identity writer but hurt the neural one. The bottleneck is reading A's state, not B's capacity to receive it.

**Status:** PCS3c is unblocked, using W1-b (K = 4, C = 64). The sha of `W1_CHOICE.json` must be passed at PCS3c launch.
