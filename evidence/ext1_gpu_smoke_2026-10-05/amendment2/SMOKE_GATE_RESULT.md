# EXT1 Amendment 2 smoke gate

Status: **PASS**. The EXT1 full run is authorized by the predeclared smoke gate.

- Modal call: `fc-01M46V0JB0MW6ARRQDDVF7NJV2`
- Modal profile: `modal-new-account`
- Runner SHA-256: `03493213ed7aa9f72fbc004ae9a01b48fa6b1b12fad88f9231147c2ccde64934`
- Modal output directory: `/artifacts/ext1-gpu-smoke-03493213ed7a`
- Model: `Qwen/Qwen3-4B`, revision `1cfa9a7208912126459214e8b04321603b3df60c`
- GPU: NVIDIA L4
- CORRECT-arm forced-readout gate: **0/2 (0%)**, threshold `<= 60%`; passed.
- Natural-readout scorable rate: **100%** among the 15 natural-mode calls.
- Smoke readout modes: 15 natural, 2 forced. Both forced reads were in `inherit_none`; the forced next-token-logit path was exercised. The validation-only forced read on a natural CORRECT call did not change that call's natural classification or score.
- Mechanics: passed; nonempty inherited cache observed, quarantine dropped the cache, and attenuation preserved K while scaling V.
- Confirmatory data / held-out test: none used; this is an integration smoke only.

Downloaded artifacts are in `smoke_03493213ed7a/ext1-gpu-smoke-03493213ed7a/`.

Attempt 1 timed out at the configured 600-second limit and returned no scorable gate result; see `ATTEMPT_1_TIMEOUT.md`. The compact smoke passed without changing the receiver cap or any full-run design choices.
