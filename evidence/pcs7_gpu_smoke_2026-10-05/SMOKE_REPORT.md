# PCS7 full-path GPU smoke on the sealed RQ7 choice (2026-10-05)

Not scientific (pool 48, 1 epoch). Result classification is forced to `SMOKE_ONLY_NO_QUALIFICATION`.

- Profile `modal-account-B`, L4, 24 GiB, Modal timeout 600 s. Call `fc-01M44ZCFX8T1Z4ZPN7Y38GD4WF`, exit 0, 77 s in-run. Runner sha `d8235468aca587da6d5ba68de030bc7079d95bbf224ecc382a373d39e472d58d`. Volume dir `/artifacts/pcs7-gpu-smoke-rq7-d8235468aca5`.
- `RQ7_CHOICE.json` passed by path and sha (`aecbbc0d...56ff`); the executor checks the sha first, then runs the full `verify_rq7_choice` chain (raw regeneration, gate, protocol, code-sha pins against /root) inside the container. Cell F1_add_depth1. D1-b objective (default, CLI `--d1`).
- Path exercised: source pool, A digit readout and last-2-position capture, source gates (recorded), bridge fit + val selection, seal, B baselines, all arms (PCS, 3 wrong, zero, random, restart, restart_reason, text handoff, oracle, token-identity ceiling), metrics, criteria.
- Numbers (smoke scale): A valid 48/48, A accuracy 0.875, silence verified 1.0; oracle follows A 0.84; B_restart follows A 0.125; restart_reason follows A 0.875; PCS follows A 0.19 (untrained, 1 epoch). Source gates `test>=400` and `>=20 A-mistakes` fail by construction at n=16 test.
- Added: `--rq7-choice-sha256` (required, fail closed), `--d1` (D1-a fails closed as not implemented for PCS7), smoke through the scientific path, 1 new unit test (16 pass).
- W1-b is not applied to the PCS7 bridge (design 09 names PCS2b first, W1 optional); flagged in the protocol JSON.
