# EXT1 GPU smoke report

Status: PASS (integration smoke only; no confirmatory result).

- Model: Qwen/Qwen3-4B at 1cfa9a7208912126459214e8b04321603b3df60c
- Upstream: LatentMAS commit 9a9e4d331eb11430bd9e64754c6b252b06d73031 (Apache-2.0).
- GPU: NVIDIA L4
- Transformers cache-position compatibility: True
- Independent smoke recipients: 2
- Receiver calls: 28
- Nonempty inherited cache observed: True
- Quarantine passed no cache: True
- Value attenuation preserved K and scaled only V: True
- Summary environment preflight (contract, exact McNemar, AUROC): PASS
- Confirmatory data opened: no.
