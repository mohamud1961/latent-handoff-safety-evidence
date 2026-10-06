# GEN1 GPU smoke (2026-10-05)

Not scientific. Profile `modal-new-account`, L4, 600 s cap, exit 0, **55 s wall**, peak GPU 7.9 GiB. Call `fc-01M46BQPJ3MXM4MNXCT1YTT63F`, runner sha `292560eaf4197ababf4c99570f6eb8609f4d6191cc817947974e2c11feb5f7e2` (code commit 895b0dc). An earlier smoke with the staged two-step prompt (`w = ...`, then `e = (w + m2)`) was superseded: B's oracle accuracy on it was 0%, so the prompt was changed to the design's literal `e = (v + m1 + m2) % 10` (oracle 37.5% on the smoke). The first smoke's call id was not captured.

Path exercised end to end on a 48-episode pool (24 / 8 / 16), 3 epochs per arm: P1 generation (seed 20261021) -> A (Qwen3-4B) capture and silent readout -> source gate -> REP bridge -> seal -> evaluation -> COMP bridge -> seal -> evaluation, raw records, statistics.

| item | value |
|---|---|
| A silent accuracy / format valid / silence | 100% / 100% / verified (matches the PCS7b P1 level) |
| source gate | all checks pass except test parsed >= 400 (smoke pool has 16; not enforced in smoke) |
| B sees g | never (asserted on 50 episodes; map absent from every B prompt) |
| queries per arm | 96 (16 test states x 2 primary + 2 seen + 2 two-step) |
| oracle follows A (single / two-step) | 75-78% / 37.5% (B can use an explicit v; two-step is harder for B itself) |
| B_restart follows A | 12-28% (B cannot recompute) |
| PCS (3 epochs, 24 train states) | 3-16%, equal to the matched-wrong rate: meaningless, the bridge is untrained |
| val loss REP / COMP | 3.07 -> 2.47 / 2.74 -> 2.77 (3 epochs) |

Plumbing verified: held-out combination rule (20 distinct combinations, COMP never trains them, REP trains only m 1-4), seals written and verified before any control is built, raw JSONL written before statistics, batched soft-state logits equal one-at-a-time logits (padding invariance, CPU test), overflow-safe Fraction McNemar from `mon2_contract`, state-cluster bootstrap. No design-level problem seen. Files here: result JSONs, per-arm raw records, protocol, code shas, log.

Estimated full run: about 2 h on L4 (about $2).
