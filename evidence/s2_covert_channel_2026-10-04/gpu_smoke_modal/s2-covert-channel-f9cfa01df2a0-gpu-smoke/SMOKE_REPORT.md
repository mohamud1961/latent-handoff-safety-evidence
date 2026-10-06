# S2 real-model GPU smoke report

- Status: passed as an integration smoke; no scientific result or test-set evaluation.
- Modal profile: `modal-account-B`; app `ap-APw4rbqAH1qDU94bwETIhr`; call `fc-01M44HBTDDN3P5RC25J1EWQ1SC`.
- Output: `/artifacts/s2-covert-channel-f9cfa01df2a0-gpu-smoke/` in `pcs-core-artifacts`.
- Exit code: 0. The function was capped at 600 seconds on L4 / 24 GiB.
- Verified: pinned bridge and source-cache hashes, pinned model revisions, one real receiver query, one attack backward step, and frozen receiver weights.
- Runner SHA-256: `f9cfa01df2a084984d55f19008cc08c94a370cb1f7986f6c609c19b249911860`.

The first attempt failed before model loading because the Modal container resolves baked files under `/root/scripts/`. That launcher path was corrected and covered by a test before this successful retry. The failed call was `fc-01M44H9WX9XN2R03G161AZSDQF`.
