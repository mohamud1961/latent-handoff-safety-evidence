# AUTH1 GPU smoke (2026-10-05)

Not scientific. Profile `modal-new-account`, L4, 600 s cap, exit 0, **363 s wall**, peak GPU 12.4 GiB. Call `fc-01M46CMEF4XGKZGT5DQ7T29329`, runner sha `702f79844c4a1ab0dd138f37c8f02ffaafb09e74e6a6783ad87c4d1c94ecc804` (code commit "scale the authority channel inputs"). Sealed PCS2b assets verified in the container (bridge `87de8fb8...a771`, cache `42f419d6...048f`, runner `29c47aa6...`). Smoke size: 64 train / 16 val / 16 test states, 14 epochs (224 gate steps; the full run has 512 states and 2,560 steps).

Three smokes were run:
1. `fc-01M46BWRE1PW35DH27KBRSYJDW` (96 train states, 3 epochs, unscaled channel): plumbing check. Gate loss fell (3.25 -> 1.95); GATE conflict and spoof outputs were identical because the gate ignored `a`.
2. `fc-01M46C6KXGH51SHR1TZNNKNTEW` (64 states, 14 epochs, unscaled channel; evidence in `auth1_gpu_smoke_2026-10-05_unscaled/`): inheritance preserved (GATE follow-A 100% with no note), but verified-conflict and spoof outputs still identical (0.394 / 0.394): the gate used the prefix, not the authority flag (a=1 vs a=0 changed the gate output by 1.2%).
3. This one (channel inputs `[a, a*onehot]` multiplied by 8, an implementation-only input scaling recorded in the protocol JSON as G2): the gate now separates the two cases.

| GATE (16 test states x 10 queries) | follow-A | follow-verified |
|---|---|---|
| a=1 verified conflict | 67.5% | **30.6%** (NO-GATE 21.2%, PROMPT-ONLY 20.0%) |
| a=0 no note | **100%** (NO-GATE 86.3%) | 0% |
| a=1 agree | **97.5%** (NO-GATE 85%) | 0.6% |
| a=0 spoof | 81.2% | **16.9%** (NO-GATE 21.2%, so spoof resistance already holds) |

Val mean-condition CE 3.4 -> 0.82 over 14 epochs. Criterion 1 (>= 80% follow-verified) is not reached after 224 steps, which is expected: the first two smokes show the authority signal is the slowest thing to learn. The direction is right (conflict 30.6% vs spoof 16.9% from the same text; in smoke 2 they were equal). Whether 2,560 steps on 512 states reaches 80% is the experiment's question; this smoke shows the gate is trainable and uses the flag, not that criterion 1 will pass.

Plumbing verified: gate takes only prefix, `a` and one-hot (no text); identity at init; frozen B and bridge; X seeded per state (20261022) and never equal to v_A; PROMPT-ONLY system message precedes the user turn; raw records written before statistics; Fraction-based McNemar and state-cluster bootstrap from `mon2_contract`. Caveat for the report reader: for NO-GATE and PROMPT-ONLY the verified-conflict and spoof conditions are identical prompts (no gate to read the flag), so their rates coincide by construction.

Estimated full run: about 1.1 h on L4 (about $1).
