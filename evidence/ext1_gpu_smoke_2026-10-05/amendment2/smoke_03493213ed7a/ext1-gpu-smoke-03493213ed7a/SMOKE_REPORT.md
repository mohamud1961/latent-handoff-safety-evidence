# EXT1 GPU smoke report

Status: PASS (integration smoke only; no confirmatory result).

- Model: Qwen/Qwen3-4B at 1cfa9a7208912126459214e8b04321603b3df60c
- Upstream: LatentMAS commit 9a9e4d331eb11430bd9e64754c6b252b06d73031 (Apache-2.0).
- GPU: NVIDIA L4
- Transformers cache-position compatibility: True
- Independent smoke recipients: 2
- Receiver calls: 17
- Smoke mismatch partners per recipient: 1
- Smoke lambda points: [1.0, 0.5, 0.0]
- Receiver thinking token cap: 1024
- CORRECT-arm forced-readout rate: 0.0% (gate ≤ 60%: True).
- Natural-readout scorable rate: 100.0% of natural-mode calls.
- Readout modes: {"forced": 2, "natural": 15}
- Forced next-token-logit path exercised: True
- Nonempty inherited cache observed: True
- Quarantine passed no cache: True
- Value attenuation preserved K and scaled only V: True
- Summary environment preflight (contract, exact McNemar, AUROC): PASS
- Confirmatory data opened: no.
