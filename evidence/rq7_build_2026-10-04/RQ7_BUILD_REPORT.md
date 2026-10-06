# RQ7 qualification build report

## Build and validation

- Inference-only qualification executor: `scripts/rq7_qualification.py`.
- Modal launcher: `scripts/modal_rq7_qualification.py`.
- Unit tests: `tests/test_rq7_qualification.py`; 11 passed after the Modal output-path fix.
- CPU synthetic smoke: `evidence/rq7_build_2026-10-04/cpu_smoke_launcher_fix/`; exit code 0, 18 synthetic rows, explicitly classified as synthetic smoke with no qualification.
- Real-model smoke: `evidence/rq7_gpu_smoke_2026-10-04/real-model-gpu-smoke/`; exit code 0, 12 rows, no qualification decision. See `evidence/rq7_gpu_smoke_2026-10-04/SMOKE_REPORT.md`.

The Modal launcher now isolates smoke and full outputs beneath `/artifacts/rq7-qualification-<executor-sha12>/real-model-gpu-smoke/` and `/artifacts/rq7-qualification-<executor-sha12>/full/`. This prevents a prior smoke directory from making the full run fail the clean-output guard.

## Qualification command

```sh
MODAL_PROFILE=modal-account-B modal run --detach scripts/modal_rq7_qualification.py --mode full
```

The full result mechanically writes a sealed cell choice or stop result. PCS7 must verify and consume that full qualification bundle; smoke artifacts are rejected.
