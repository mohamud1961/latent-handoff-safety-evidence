# RQ6 6A receiver probe with numbered update lines (2026-10-05)

Inference-only, not a qualification result. Modal call `fc-01M44ZKPSS1CB47YTZ1CVSG9TS` (modal-account-B, L4, 24 GiB, 600 s cap, exit 0, 169 s). Launcher sha `c17143f16d85...`, volume dir `/artifacts/rq6-receiver-probe-c17143f16d85-46a360f4`. 32 generated D=11 episodes (seed 20261006, indices 0-31), oracle_state and restart arms only. Fix tested: B's program copy numbers update lines `Update K: <line>`; initial assignments and A's source prompt unchanged (pinned in `RQ6_PROTOCOL.json` as `six_a.receiver.program_rendering`).

| metric | value |
|---|---|
| A parse rate | 30/32 = 0.9375 (A final == symbolic truth on 22 of the 30 parsed) |
| **oracle_state fidelity to A-s11** (of parsed A) | **0.167** (5/30); 0.156 over all 32 with unparsed counted as failures |
| restart fidelity to A-s11 | 0.000 |
| oracle_state B parse rate | 0.933 |
| restart B parse rate | 0.033 (B restates s0..s7 and runs out of the 120 tokens) |
| oracle accuracy vs truth s11 | 0.200 |
| oracle outputs with s9 and s10 equal to A-s8 | 24 of the parsed rows |

Result: oracle fidelity is far below the 70% gate. Numbering the updates did not fix the failure mode: B still copies the supplied s8 state into s9, s10 and s11 ("The state remains the same after all updates") while parsing correctly. Per instructions, iteration on RQ6 stops here. RQ6 6A is BLOCKED; PCS6-A/B and CAP1-style L4 claims that depend on its gate cannot launch.

Unit tests: 34 pass (RQ6, RQ6 launcher, PCS6-A/B, PCS6 launchers). New: `number_program_updates` tests and the `--receiver-probe` mode in `rq6_qualification.py` / `modal_rq6_qualification.py`.
