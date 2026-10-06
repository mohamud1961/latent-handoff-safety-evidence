# PCS3b result (40 epochs; amendment `PCS3B_TRAINING_BUDGET_AMENDMENT_2026-10-04.md`)

Modal `modal-account-A`, call `fc-01M42T6KVRSBJXP215NYJS129Y`. Sealed test: 459 states × 3 selectors.

| | Neural (A hidden states, 4 positions) | Token-identity (A's written digits) |
|---|---|---|
| PCS fidelity to A | **67.5%** | 92.7% |
| Mean matched wrong state (shares the 2 unselected coordinates) | 4.3% | 1.2% |
| Δ_specific, state-cluster 95% CI | **+63.1 [+59.7, +65.3]** | +91.6 [+89.7, +93.0] |
| Per selector a / b / c | 65.8 / 70.6 / 66.0% | 95.9 / 87.8 / 94.6% |
| Follows A when A is wrong (13 states, 20 records) | 60% (wrong states 0%) | 95% (4.4%) |
| Classification (frozen) | **NO POSITIVE CLAIM**: fails only "overall ≥70%" (67.5%) | **POSITIVE** |

Baselines: restart 13.8%; partial state (2 of 3) 20.3%; exact-state text oracle 100%; private trace text 97.9%; zero 7.1%; random 8.8%.

**Neural arm checks.** Passed:
- source and receiver gates;
- strong-control coverage;
- each selector ≥60%;
- state-specific ≥30, with CI above 0;
- beats restart by ≥30;
- beats zero and random;
- source-wrong directional test.

Failed: **overall fidelity ≥70%** (67.5%).

Training notes:
- Neural validation loss reached its minimum near epoch 30, at 1.12, then rose (1.22 at epoch 40). The best checkpoint is chosen by validation loss.
- Token-identity validation loss reached 0.35.

**Reading.**
- A 3-coordinate source state from Qwen3-4B activations, captured along A's private working, is realised in frozen Qwen3-1.7B with very strong state specificity.
- Matched wrong states that share 2 of 3 coordinates drop fidelity to 4%.
- A's mistakes are inherited.
- Strictly, the frozen ≥70% fidelity criterion is missed by 2.5 points, so this is a **near-miss**, not a pass.
- The transferred content is A's state across its written private working; B never sees that text. Framing is per `PCS4V2_PCS3_MULTIPOSITION_CAPTURE_AMENDMENT_2026-10-04.md`.
