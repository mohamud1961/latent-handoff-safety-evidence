# RQ6 Amendment 2 receiver ladder (2026-10-05): STOP_RECEIVER_INCAPABLE

Inference-only probes on 32 generated episodes (seed 20261006, indices 0-31), oracle_state and restart arms, modal-account-B L4, each <=600 s Modal cap. Gate: oracle fidelity to A's final state >= 70%. Stop at the first rung that passes; none did.

| rung | D | A parsed | oracle fidelity | restart fidelity | oracle parse | restart parse | hit token cap | mean tokens | outputs with </think> |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 11 | 30/32 | 0.000 | 0.000 | 0.000 | 0.000 | 59/60 | 199 | 0 |
| R2 | 10 | 32/32 | 0.000 | 0.000 | 0.000 | 0.000 | 64/64 | 200 | 0 |
| R3 | 10 | 32/32 | 0.000 | 0.000 | 0.000 | 0.000 | 64/64 | 600 | 0 |

Calls: R1 `fc-01M451F3V2XFW0YCKZSJ8QVC7P` (187 s), R2 `fc-01M451P9XGGZWMFTAD0MYSV3GR` (174 s), R3 `fc-01M451WNN5RNQZTSZ0AGBE9G5T` (360 s). Raw rows and previews: `amendment2_R1/`, `amendment2_R2/`, `amendment2_R3/`.

## What happened
With A's own source prompt template in B's prompt (R1, R2), B now writes calculation lines and STATE lines in the right style (the earlier copy-the-state failure is gone), but it **restarts from the initial assignments**: it writes `STATE s0`, `s1`, ... and is cut off by the token cap (200) around s6-s7, before any update-9 line, so nothing parses. In R3 (thinking, 600 tokens) B spends the whole budget thinking from the start of the problem (it says it will track a, b, c "through each update" from the initial values) and never reaches `</think>`; again 0 parseable outputs. In every rung B ignores the supplied "State after step 8" line.

## Diagnosis for the designer (not iterated, per the pre-registered ladder)
The R1 prompt contains A's source template verbatim, which says "Write exactly N blocks, one per state ... K=0..D-1 ... nothing else before them". The appended "Continue from update 9" instruction conflicts with it, and B follows the earlier, longer instruction. Parity with A's prompt may therefore have been the cause of the failure rather than a capability limit. Caps are also too small for a from-scratch trace (about 300 tokens needed for D=10-11). A rung that keeps the worked example but rewrites the block-count instruction as "write only the lines for updates 9..D" is not in the ladder and was not run.

## Outcome
RQ6 6A = STOP_RECEIVER_INCAPABLE under Amendment 2 as written. Pinned in `RQ6_PROTOCOL.json` (`six_a.receiver.amendment_2_ladder`, `pinned_rung: null`). No full RQ6 run. PCS6-A stays blocked; PCS6-B (GSM8K) is independent and unaffected here.
