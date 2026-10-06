# PCS7 Amendment 1b current-runner GPU smoke

**Status:** completed; current runner smoke only; no qualification result.  
**Modal call:** `fc-01M44RHN0FN9TVQTGPXJD1BVE9`  
**Output:** `pcs-core-artifacts:pcs7-gpu-smoke-f2dbbf19f28a/`  
**Runner SHA-256:** `f2dbbf19f28ac3b3393faba6eea83e9e77e773f2b2d5de742c3c5b70e5a7c18d`  
**Exit codes:** Modal 0; runner 0.  
**Elapsed:** 29.03 seconds (600-second function cap).

The smoke loaded the pinned Qwen3-4B and Qwen3-1.7B snapshots, exercised the current Amendment 1b prompt/readout code, fitted one smoke bridge epoch, sealed it, and ran two B soft-state readouts. All **12/12** A digits were valid and **11/12 (91.7%)** were correct; both B soft-state readouts were valid. The output is labeled `SMOKE_ONLY_NO_QUALIFICATION` and the run used generator-known labels for smoke only.

This is pipeline evidence. It does not test the full base-100 readout, all task families and matched controls, or any qualification threshold. Artifacts are in `pcs7-gpu-smoke-f2dbbf19f28a/`.
