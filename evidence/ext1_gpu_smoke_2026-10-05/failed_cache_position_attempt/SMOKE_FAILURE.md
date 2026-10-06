# EXT1 GPU smoke attempt 1

Status: **FAILED on the first cached receiver call**.

- Modal app: `ap-sZS7T0aQf4oUYf3Or6ORwr`
- Call: `fc-01M46PAFXWB68JJX4J1SZJK32W`
- Runner SHA-256: `edc38cbf6c60a28611d32b4d7475d9b62616a15f3ab50f7a0655c97eb2361e61`
- Output directory: `/artifacts/ext1-gpu-smoke-edc38cbf6c60`
- The summary environment preflight completed and Qwen3-4B loaded. The first receiver generation then failed in Transformers 4.52.4 because its initial-cache-position helper evaluated LatentMAS's explicit multi-element `cache_position` tensor as a boolean.
- No receiver forward pass completed; no confirmatory data or full-run output was produced.

The retry uses a model-instance compatibility adapter that returns the explicit cache-position tensor unchanged, bypassing only that ambiguous truthiness check. The vendored LatentMAS methods remain unmodified.

Raw Modal output is preserved in [EXT1_GPU_SMOKE.log](EXT1_GPU_SMOKE.log).
