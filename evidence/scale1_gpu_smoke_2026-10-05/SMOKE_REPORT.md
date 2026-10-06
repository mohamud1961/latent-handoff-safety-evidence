# SCALE1 real-model GPU smokes (2026-10-05)

Not scientific: pool 48 (train 16 / val 8 / test 8 states), 1 epoch, gates recorded not enforced. modal-account-B, runner sha `4223501cc9a75469196ab04e6e977f50759d9ef90a3c8531298632e5a031de8d` (`scale1_pcs2b.py`, imports the unchanged PCS2b runner sha `29c47aa6...`, verified at load). Pinned revisions (HF main shas recorded 2026-10-05, in each `CODE_SHAS.json`): Qwen3-8B `b968826d9c46dd6066d109eabc6255188de91218`, Qwen3-4B `1cfa9a7208912126459214e8b04321603b3df60c`, Phi-4-mini-instruct `cfbefacb99257ffa30c83adab238a50856ac3083`. Models are loaded with `local_files_only=True` from the HF cache volume after a separate CPU `--prefetch` call.

| arm | GPU | call | exit | wall | A -> B | capture layers | A/B hidden | source gates (parse / objective / pre-digit agree) | receiver oracle | peak GPU mem |
|---|---|---|---|---|---|---|---|---|---|---|
| S-UP | L40S | `fc-01M4519AHXNWJDCKT7ZTBXE8TC` | 0 | 101.9 s | Qwen3-8B -> Qwen3-4B | 4,8,...,36 | 4096 / 2560 | 1.00 / 0.96 / 1.00 | 0.94 | 17.1 GiB |
| X-FAM | L4 | `fc-01M4519Q2ABTJNA7QQE63FJKCR` | 0 | 148.0 s | Qwen3-4B -> Phi-4-mini-instruct | 4,8,...,36 | 2560 / 3072 | 1.00 / 0.96 / 1.00 | 1.00 (default prompt; Phi system-message variant not needed) | 12.0 GiB |

Path exercised for both: pinned loaders, layer list from A's config, early receiver probe, 48-episode generation and pre-digit capture, source gates, bridge (PCS2b architecture; dims follow the models), future + readback loss, val-selected checkpoint, full evaluation (9 m values, 3 matched wrong, zero, random, restart, oracle, fair text handoff, readback), PCS2b criteria 1-10 plus text-handoff comparison, cost report. After one epoch on 16 states PCS fidelity is at chance (S-UP 11%, X-FAM 3%), as expected; no result is implied.

Stage seconds (smoke scale): S-UP generation 43, receiver preflight 17, training 8, eval 9; X-FAM generation 61, preflight 31, training 8, eval 25. Extrapolation to the PCS2b size (pool 1,024, 512/128/256, 10 epochs): about 1.2 h L40S (about $2.4 at the assumed $1.95/h) and about 1.4 h L4 (about $1.1 at $0.80/h); the full runs write measured per-stage GPU-hours and USD to `SCALE1_COST.json`.

Notes: the token-identity ceiling is not in the PCS2b runner, so the explicit-state oracle arm is the ceiling reported. Phi runs in bf16 (native dtype); Qwen arms in fp16 as in PCS2b.
