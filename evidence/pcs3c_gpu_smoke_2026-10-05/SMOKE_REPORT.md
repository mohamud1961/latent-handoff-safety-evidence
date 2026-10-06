# PCS3c real-model GPU smoke (2026-10-05)

Not scientific. Pool, splits and epochs are shrunk; frozen gates are recorded but not enforced.

- Profile `modal-account-A`, L4, 24 GiB, Modal timeout 600 s. Call `fc-01M44Z2XGT1CFVS7H1GR09YCYK`, exit 0, 120.2 s total.
- Executor sha `003cdc273016df3c55b67b892e6b873a7fbf81d1889518036a19403c935e8f0e`. Output volume dir `/artifacts/pcs3c-gpu-smoke-003cdc273016`.
- W1 choice read from `/artifacts/w1-writer-sweep-f49f19039167/W1_CHOICE.json`, sha `d85909b9...e60937` verified in the container by `admit_w1_choice`. Chosen config W1-b applied: K=4, C_dim=64, dropout 0 (epochs forced to 1 for the smoke; 40 in the full run).
- Path exercised: pinned-code check, W1 admission, generation with real Qwen3-4B (pool 32, seed 20261005), 4-position capture, eligibility, canonical seed+1 split (12 train / 8 val / 12 test), source gates, bridge cache for neural and token_identity, receiver preflight (real value 1.0 overall and per selector), one optimizer step per arm (batch 16, 12 train rows), val-loss checkpoint, bridge seal and probe-seed commitment, evaluation of all arms on test (36 rows per arm), CAP1-schema records (36 records pass `validate_evaluation_record`), `summarize_pcs3c` (classification PCS3C_NULL, expected at this size).
- Stage seconds: source generation + capture 88.2, neural train 8.1, TI train 5.9, neural eval 8.9, TI eval 8.9.
- Source metrics: parse 32/32, checkpoint 32/32, located 32/32, line digits valid, train/val triple accuracy 1.0.
- Gates that fail by construction at n=32: decodability, strong-control coverage, test>=450. They are recorded in `PCS3C_GPU_SMOKE_REPORT.json`.

Fixes made to get here: launcher re-imported inside the container failed (`/root/pcs3c_executor.py` not found); `modal_pcs3c_confirm.py` now hashes baked files from their destination paths when running in-container, as the PCS7 launcher does. Added `--gpu-smoke` to the executor and `--gpu-smoke` entrypoint flag (600 s function) to the launcher.

Full-run timing guide: generation scales roughly 2.75 s per episode, so the 1,600-episode pool is about 75 min; training is 40 epochs x 32 steps per arm.
