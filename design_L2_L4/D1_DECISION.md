# D1 decision for PCS6 (and PCS7, MON3): Claude, 2026-10-05

**Decision: D1-b** (state-supervised).

**Evidence.**
- PCS4v3 L3 not reached: `evidence/pcs4v3_2026-10-04/RESULT.md`.
- PCS4v4 L3 null: `evidence/pcs4v4_2026-10-05/PCS4V4_L3_DECISION.json`, sha256 `74d7f55f70594a376cb5ef26cd90641e7b93ccd22dfc79c7982b1a50cd07609f`.

**Objective per design 04.** The PCS4v3 information-weighted continuation loss, plus a readback auxiliary at λ = 0.25: B answers "What were a, b, c after step 8?" against A's s8 triple.

**Claim wording.** "State-supervised reasoning continuation", not "label-free".
