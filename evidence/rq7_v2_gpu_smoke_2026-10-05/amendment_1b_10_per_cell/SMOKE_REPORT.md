# RQ7 Amendment 1b bounded real-model smoke

**Status:** completed; smoke only; not a qualification result.  
**Modal call:** `fc-01M44QF9JHGMC6VP5PYDWT9K0Y`  
**Runner SHA-256:** `0b49742adbbf8d5d1b7c5c6edc81587c78347db7c2a2f90998c5308815b74cee`  
**Remote output:** `pcs-core-artifacts:rq7-qualification-0b49742adbbf/real-model-gpu-smoke/`  
**Sample:** 10 episodes per cell; six cells; 60 raw rows total.

On `F3_lookup_depth1`, B's oracle output was valid on **10/10 (100%)** rows and correct on **8/10 (80%)**. This passes the smoke dispatch condition of at least 50% accuracy with n≥10. It is not the 300-per-cell qualification threshold.

The smoke itself was not qualifying: no cell passed the complete gates and no `RQ7_CHOICE.json` was emitted. The full RQ7 v2 run was subsequently launched under the conditional approval after this smoke check:

- Full call: `fc-01M44QVNY07W893SMW0C496NJG`
- Output: `/artifacts/rq7-qualification-0b49742adbbf/full`
- Runner SHA-256: same `0b49742adbbf…` above.

Downloaded raw records, gate, result, protocol, code hashes, and logs for this smoke are in `real-model-gpu-smoke/`.
