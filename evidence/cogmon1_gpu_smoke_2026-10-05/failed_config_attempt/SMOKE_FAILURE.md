# COGMON1 GPU smoke attempt 1

Status: **FAILED before receiver inference**.

- Modal app: `ap-pdRsEAcYslQdhquKnTEfdl`
- Call: `fc-01M46NF9STM5V4M9897YBYW3JP`
- Output directory: `/artifacts/cogmon1-gpu-smoke-4ac30b322cff`
- The pinned Qwen3-1.7B receiver loaded. Bridge setup then failed because the sealed W1-b checkpoint config includes `c_dropout=0.0`, while the canonical PCS3 `Config` does not accept that W1 wrapper metadata field.
- No receiver forward pass, GPU smoke result, held-out access, or confirmatory result was produced.
- Full execution was not launched.

The runner now checks and records the zero-dropout reconciliation before loading the receiver, and the Modal launcher reads the committed log from its final path. A new content-derived output directory will be used for the retry.

Raw launcher output is preserved in [COGMON1_GPU_SMOKE.log](COGMON1_GPU_SMOKE.log).
