# MON2 bounded real-model smoke

**Classification:** `SMOKE_ONLY_NOT_SCIENTIFIC_RESULT`  
**Modal profile:** `modal-account-B`  
**Call ID:** `fc-01M43VDBBS53H80J8S4Q4ZV92J`  
**Runner SHA-256:** `ff37b674ed97cc786e07ff33e39b69bb5a0c7a5694b12a30c6baa8f851eaf371`  
**Remote output:** `pcs-core-artifacts:mon2-gpu-smoke-ff37b674ed97/`

The L4 function used a 600-second timeout. It exited with code 0 after running
the real Qwen3-4B source path, the PCS2b bridge, and the Qwen3-1.7B receiver
path.

| Check | Observed |
|---|---:|
| Programs / paired episodes requested | 20 / 40 |
| Programs / episodes included | 20 / 40 |
| Source parse rate | 100% |
| Exact checkpoint rate among parseable answers | 100% |
| Pair exclusions | 0 |
| Source-gate enforcement | Disabled for this smoke, as specified |
| Receiver arms | 10, including PCS, restart, oracle, controls and three wrong states |
| Future-query offsets | 1–9 |
| Monitor fitting | Train split only (15 programs); no validation or test scoring |

The bridge SHA and byte count matched the frozen PCS2b manifest. The source
gate's study-scale checks are expected to be false on this tiny split; no
scientific pass/fail conclusion was computed. The 20-program smoke does not
authorize or replace the full MON2 run.

The first two detached invocations exited before model loading due to defects
in the input-gate constant and neutral-note formatting. Both were fixed and
covered by local regression tests. The successful run above used the resulting
`ff37b674ed97` runner hash.
