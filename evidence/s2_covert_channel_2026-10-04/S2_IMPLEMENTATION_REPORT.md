# S2 Covert Channel Implementation Record

Date: 2026-10-04
Scope: implement the resolved S2 executor, its guarded Modal entrypoints, focused tests, and local CPU smoke evidence. This report supersedes the earlier S2 preparation-only note for this implementation pass.

## Implemented

- Resolved protocol validation against `design_L2_L4/RESOLUTIONS_1_OPUS.md#S2`, including the `modal-account-B` profile, pinned Qwen revisions, `local_files_only`, the per-example relative prefix RMS budget, and fixed bridge/cache custody hashes.
- Reuse of the hash-pinned `scripts/pcs2b_preanswer_bridge.py` bridge, `digit_ids`, future/readback prompts, handoff rendering, and receiver-logit path.
- Independent i.i.d. Bernoulli(0.5) payload schedules for train, validation, and test, with fresh training payloads per epoch and fixed validation/test payloads.
- Attack encoder/decoder training, validation-only beta selection, D-PCA/4-bit quantization/noise defenses, the adaptive D-PCA arm, per-arm detectors, clustered bootstrap summaries, and raw test records.
- A single sealed test pass: an exclusive evaluation-start marker is written before test outputs are read; existing seal artifacts block a repeat pass; records, summary, and seal include hashes and counts.
- A Modal L4 executor requesting 24,576 MiB for the research run and a separate 600-second L4 GPU smoke entrypoint with a 570-second subprocess timeout. Importing the module does not launch work.

## Input custody verified

Read-only Modal volume downloads under profile `modal-account-B` verified the following against the checked-in manifest and executor pins:

| Input | SHA-256 | Bytes | Verification |
| --- | --- | ---: | --- |
| `pcs2b_bridge.pt` | `87de8fb8a70d62aea0a2545faeb3c5b12890832dfd24d1b64e0b4a84cea8a771` | 30,083,799 | Strict canonical PCS2b bridge state-dict load; finite CPU output shape `(2, 4, 2048)` |
| `pcs2b_source_cache.pt` | `42f419d69f5ebda6270ecbd335b2e8de72123cf757d0ebc2327c1620bd8c048f` | 42,616,502 | Cache contract validated; feature shape `(896, 9, 2560)`, split counts 512/128/256 |
| `PCS2B_RUN_MANIFEST.json` | `adc79a4163fc56b12ce5d1a9cd25c2f4ed2be7adcb02b2000dd92dd6638276ae` | — | Matches checked-in pin |
| `pcs2b_preanswer_bridge.py` | `29c47aa64ef482e0654052df223dc1b9596c0a23bfbb93ddb5d5959562b8949c` | — | Matches the manifest's embedded runner SHA |

The machine-readable custody record is [S2_ASSET_CUSTODY_VERIFICATION.json](S2_ASSET_CUSTODY_VERIFICATION.json). The source cache's 2560-wide features are intentionally bridged into 2048-wide receiver prefixes.

## Local validation

Using `/tmp/pcs-l2l4-cpu-env`:

- `python -m py_compile scripts/s2_covert_channel.py scripts/modal_s2_covert_channel.py tests/test_s2_covert_channel.py` — passed.
- `python -m pytest -q tests/test_s2_covert_channel.py` — 16 passed.
- `python scripts/s2_covert_channel.py --smoke --out-dir evidence/s2_covert_channel_2026-10-04/cpu_smoke` — `S2_SMOKE_OK`; exercised synthetic payload, budget, attack-gradient/frozen-receiver, beta selection, all five arms, defense decoder, and detector paths.
- `git diff --check` — passed.

The CPU smoke is synthetic machinery validation only. It is not a PCS2b model run or an S2 result.

## Real-model GPU smoke

- First Modal attempt (`fc-01M44H9WX9XN2R03G161AZSDQF`) failed during container import before model loading: the launcher resolved baked scripts as `/root/<name>` although the image stored them under `/root/scripts/`.
- The host/container path resolution was corrected and covered by the launcher unit test. A bounded retry completed successfully: `fc-01M44HBTDDN3P5RC25J1EWQ1SC`, app `ap-APw4rbqAH1qDU94bwETIhr`, output `/artifacts/s2-covert-channel-f9cfa01df2a0-gpu-smoke/` in `pcs-core-artifacts`.
- The 600-second L4 smoke exited 0, loaded the pinned receiver revision, ran one real receiver query and one attack backward step, verified the bridge/cache hashes, and confirmed that receiver weights remained frozen. It is explicitly marked as an integration smoke, not an S2 scientific result.
- Downloaded evidence is in `gpu_smoke_modal/s2-covert-channel-f9cfa01df2a0-gpu-smoke/`.

## Execution boundary and outstanding evidence

No Modal app, container, research run, or GPU smoke was launched. Source and receiver models were not loaded; only the read-only input downloads and a CPU bridge forward were performed. The exact pinned model snapshots and tokenizers will be required from the local Hugging Face cache at executor runtime because model loading uses `local_files_only=True`.

Accordingly, there is no S2 scientific outcome or criterion decision in this record. The single sealed evaluation remains unexecuted. No aggregate `BUILD_REPORT` was edited.
