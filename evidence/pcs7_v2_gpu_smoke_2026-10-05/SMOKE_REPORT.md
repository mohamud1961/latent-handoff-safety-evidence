# PCS7 earlier Amendment 1 GPU smoke

Status: **superseded for current-runner validation by** [`amendment1b_current_runner/SMOKE_REPORT.md`](amendment1b_current_runner/SMOKE_REPORT.md). This earlier run used a different runner SHA; its record is retained below.

- Modal call: `fc-01M44NB50VEM213X5XJW0T4ZRP`
- Modal app: `ap-5SknKjDF0KBNlFeimZTw7h`
- Remote output: `pcs-core-artifacts:pcs7-gpu-smoke-1e255551f2f1/`
- Runner SHA-256: `1e255551f2f126b39dda9fff891972161defc90759769fc4411554d8864f9df6`
- Modal wrapper and runner exit codes: `0` / `0`
- Runner elapsed time: 30.99 seconds (function timeout: 600 seconds)
- Model pins: A `Qwen/Qwen3-4B` at `1cfa9a7208912126459214e8b04321603b3df60c`; B `Qwen/Qwen3-1.7B` at `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.

The run loaded both pinned models, read A's 12 synthetic F1/base-10 source tasks using the anchored digit-logit readout, fitted one bridge epoch using generator-known labels reserved for smoke, sealed the bridge, and exercised B's soft-state digit readout on two rows. A produced a valid digit on 12/12 tasks and the correct answer on 11/12 (91.7%). B's two PCS-arm outputs were valid digit readouts. This smoke used no RQ7 choice and wrote `SMOKE_ONLY_NO_QUALIFICATION`.

This small integration smoke does not exercise the base-100 two-digit readout, the other task families, PCS7's full matched controls, or any qualification criterion. The successful run establishes that the amended source and receiver readout paths execute on the pinned models; it does not establish answer transfer.

The local copies of `PCS7_GPU_SMOKE_REPORT.json`, `PCS7_GPU_SMOKE_SOURCE_RAW.jsonl`, `PCS7_GPU_SMOKE_EVAL_SEAL.json`, `PCS7_PROTOCOL.json`, `CODE_SHAS.json`, `EXIT_CODE.txt`, `MODAL_EXIT_CODE.txt`, `modal.log`, and `run.log` are in `artifacts/`. The bridge checkpoint remains available in the Modal artifact volume at the remote output path above.
