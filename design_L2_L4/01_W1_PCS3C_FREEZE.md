# 01: Writer sweep W1, then PCS3c confirmatory 3-value transfer (L2): FREEZE

## Part A: W1 writer sweep (development; existing PCS3 data only)
**Purpose.** Pick the bridge writer configuration on validation data before the confirmatory run.

**Data.** The existing PCS3 multi-position features and items:
- `pcs-core-artifacts:pcs3-multipos-2aedd7129e4e/PCS3_MULTIPOS_FEATURES.pt`, sha `ea514731…`;
- the enlarged-pool extras.

Use **train and val splits only**. The PCS3/PCS3b test pool is not touched.

**Configs.** The runner is `scripts/pcs3_multi_register_bridge.py`, unchanged except for these hyperparameters:

| id | K slots | C_dim | epochs | dropout on C |
|---|---|---|---|---|
| W1-a (PCS3b baseline) | 4 | 16 | 40 | 0 |
| W1-b | 4 | 64 | 40 | 0 |
| W1-c | 8 | 64 | 40 | 0 |
| W1-d | 8 | 64 | 40 | 0.1 |

Train the neural arm and the token-identity arm for each config.

**Metric.** Validation PCS fidelity (receiver answer equals A-belief for the selected register, all 3 selectors), computed with the PCS3 evaluation code on the val split.

**Decision rule (mechanical).**
1. **Chosen config:** the config with the highest *neural* val fidelity. Ties within 1 point go to the smaller config, in the order a < b < c < d.
2. **Writer-ceiling flag:** if the chosen config's token-identity val fidelity is below 90%, record a `WRITER_CEILING_FLAG`, but proceed anyway.
3. **Seal before PCS3c starts:** write `W1_CHOICE.json` containing the config, all val numbers and the hashes.

## Part B: PCS3c confirmatory (fresh data)
**Purpose.** A clean, pre-registered test of the L2 claim.

**Source.**
- **Episodes:** fresh, using the same generator and depth-6 RQ2c regime as PCS3, with **seed 20261005**. Pool size is large enough that the sealed test has ≥450 states after gates (suggested 1,600).
- **Generation:** Qwen3-4B greedy, prompt and checkpoint identical to PCS3.
- **Capture:** multi-position, with the same 4 frozen positions as `PCS4V2_PCS3_MULTIPOSITION_CAPTURE_AMENDMENT_2026-10-04.md`.

**Gates (unchanged from the PCS3 freeze).**
- parse ≥90%;
- checkpoint ≥98%;
- train/val triple accuracy ≥80%;
- per-register decodability ≥70% (val, concatenated features);
- strong-control coverage ≥90% (≥1 partner) and ≥70% (≥3 partners);
- receiver exact-A-state oracle ≥90%.

If a gate fails, stop and report. Do not tune.

**Bridge.** The W1-chosen config. Checkpoint selected by val loss.

**Arms.**
- neural (primary);
- token-identity;
- restart;
- partial (2 of 3);
- text oracle;
- private-trace text;
- zero;
- random;
- 3 strong matched wrong states (share the 2 unselected registers and differ in the selected one).

**Positive criteria (unchanged from PCS3; neural arm).**
1. Overall fidelity ≥70%.
2. Each selector ≥60%.
3. Correct minus mean strong-wrong ≥30 pts, with cluster CI > 0.
4. Beats restart by ≥30.
5. Beats zero and random.
6. If ≥10 A-wrong states exist, PCS follows A's wrong belief more often than the wrong states do.

Add exact McNemar for correct vs each wrong state.

**Classification.**
- `PCS3C_POSITIVE`: all criteria pass.
- `PCS3C_NEAR_MISS`: only criterion 1 fails, but fidelity is ≥65%.
- `PCS3C_NULL`: anything else.

**One run only.**

**Claim if positive.** "A three-value state formed in Qwen3-4B's private working transfers into frozen Qwen3-1.7B through its neural state, with strong state specificity and inheritance of source mistakes (confirmatory, fresh data)."
