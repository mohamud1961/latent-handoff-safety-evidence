# RQ6 implementation report

**Status:** executor and reviewable Modal launcher are implemented. Unit tests and local CPU synthetic smoke pass. No real-model inference, GPU call, Modal launch, or qualification run was performed.

## Implemented

- `scripts/rq6_qualification.py` implements the resolved 6A/6B inference gates, canonical PCS4v2 episode generator/chat/probe helpers, D=11 with only the registered D=10 retry, pinned model and GSM8K revisions, local-cache-only loads, deterministic splits, raw per-record prompts/outputs/token IDs, and sealed `rq6_gate_result_v1` output.
- The runner validates protocol choices before model loading and verifies hashes for the gate result, raw records, summary, code manifest, and resolved protocol copy. Qualified 6A-W and 6B results are checked through the PCS6 gate contract.
- `scripts/modal_rq6_qualification.py` provides separate explicit `--real-model-smoke` and `--full-run` entrypoints. Both require profile `modal-account-B`, L4, and 24 GiB. The smoke is capped at 600 seconds with a 570-second child budget; the full runner has a four-hour timeout. It uses the existing artifact and Hugging Face cache volumes and refuses to overwrite output directories.
- `RQ6_PROTOCOL.json` records the resolved protocol, executor settings, and custody. The local smoke and preflight outputs are under `cpu_smoke_final/` and `preflight_final/`.

## Validation

- `/tmp/pcs-l2l4-cpu-env/bin/python -m py_compile scripts/rq6_qualification.py scripts/modal_rq6_qualification.py` — passed.
- `/tmp/pcs-l2l4-cpu-env/bin/python -m pytest -q tests/test_rq6_qualification.py` — **12 passed**.
- `python scripts/rq6_qualification.py --smoke` — `RQ6_SYNTHETIC_CPU_SMOKE_OK`; outputs are labeled `synthetic_only` and are not accepted as qualification evidence.
- `python scripts/rq6_qualification.py --preflight` — resolved protocol accepted, with no model loading or external service access.
- `git diff --check` for the RQ6 runner and tests — passed.

The protocol SHA-256 in the final preflight is `9880291e2ed842882f50fa63ab8a1ff60509ccef85c153e4cb778228b9fb8704`.

## Remaining operational step

The separate real-model smoke has not been invoked. Root review is required before launching it; the full qualification remains unlaunched. Both paths use `local_files_only=True`, so the pinned model snapshots, tokenizers, and GSM8K revision must already be available in the profile's mounted Hugging Face cache.

No aggregate `BUILD_REPORT.md` was edited for this RQ6 work. No commit or push was made.
