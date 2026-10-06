# RQ7 real-model GPU smoke report

- **Outcome:** completed successfully; smoke only, no qualification decision.
- **Modal profile:** `modal-account-B`; app `ap-0rm2eiboIDHFgzks2qcysB`; call `fc-01M44GVS148AX0GPHS73ARV8P6`.
- **Runner:** `scripts/rq7_qualification.py`, SHA-256 `502ffc8155f5a0ad00803a7aca974f9842ec55e99cd1ce1fc68d9c9ae746d570`.
- **Models:** Qwen3-4B revision `1cfa9a7208912126459214e8b04321603b3df60c`; Qwen3-1.7B revision `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- **Execution:** L4, 24 GiB, 600-second timeout; 2 episodes in each of six cells (12 total); elapsed 45.95 seconds; exit code 0.
- **Output:** Modal volume `pcs-core-artifacts`, `/artifacts/rq7-qualification-502ffc8155f5/real-model-gpu-smoke/`.

The smoke exercised A generation, B restart, B reasoned restart, and B oracle when A's strict format was valid. A emitted numeric-only text on 2/12 episodes, both in F3 lookup depth 1. Other A responses began with explanatory prose or an incomplete expression and therefore count as malformed under the frozen parser. The four-token B readouts were mostly incomplete; no cell can be scored from this smoke. This is diagnostic only: all cells have `n=2`, the qualification choice is disabled, and no gates were qualified.

No prompt, parser, gate, or threshold was changed in response. The preregistered full qualification remains the decision procedure. Raw outputs, protocol, gate, result, code hashes, logs, and exit code are preserved alongside this report.
