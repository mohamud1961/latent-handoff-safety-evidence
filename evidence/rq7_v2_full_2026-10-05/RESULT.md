# RQ7 v2 qualification (amendments 1 and 1b): sealed and audited (Claude), 2026-10-05

Run `fc-01M44QVNY07W893SMW0C496NJG`, profile modal-account-B, runner sha `0b49742a…`. N = 300 per cell. Classification: **RQ7_QUALIFIED_CELL_SELECTED → F1_add_depth1**.

| Cell | A silent | B oracle | B restart | Oracle − restart | A mistakes (proj. 1,600) | Pass |
|---|---|---|---|---|---|---|
| **F1 add d1** | 90.0% | 81.7% | 10.7% | **+71.0** | 160 | ✅ |
| F1 add d2 | 20.0% | 18.0% | 9.0% | +9.0 | 1,280 | ❌ |
| F2 + mod 100 | 83.7% | 26.7% | 0.3% | +26.3 | 261 | ❌ (B oracle) |
| F2 × mod 100 | 10.0% | 2.3% | 0.7% | +1.7 | 1,440 | ❌ |
| F3 lookup d1 | 100% | 64.3% | 29.3% | +35.0 | 0 | ❌ (B oracle, mistakes) |
| F3 lookup d2 | 31.7% | 22.7% | 11.0% | +11.7 | 1,093 | ❌ |

**Audit.**
- Silence is verified in every cell, and A's answer format is valid in 100% of episodes.
- The choice rule was applied correctly: only one cell passes.
- B_restart_reason, where B may reason, scores about 100%. That is descriptive and expected: if B is allowed to write its own reasoning, it re-solves the problem. PCS7's "beats restart" comparison uses direct-answer restart, per freeze 09.
- F1 depth 1 has a true silent computation: A gets 90% with no written tokens, and B can use the result (oracle 82% vs restart 11%).

**Status:** PCS7 main is unblocked on cell F1_add_depth1.
