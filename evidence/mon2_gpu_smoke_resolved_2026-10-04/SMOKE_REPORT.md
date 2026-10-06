# MON2 resolved real-model GPU smoke

- Modal profile: `modal-account-B`
- Modal call: `fc-01M44FCX5TN736XVE3H1SKB1Y0`
- Modal app: `ap-diVl0s0vf7WYTSIojH9o8Y`
- Runner SHA-256: `dd1093e0e9e1738dd9bf7bafa877c8c3e282ae58f56ff276b521bc75649de9ba`
- Output: `pcs-core-artifacts:mon2-gpu-smoke-dd1093e0e9e1/`
- Resources: L4, 24 GiB, 600-second timeout
- Result: exit code 0; 20 programs / 40 paired episodes included; input and PCS2b bridge gates passed; source answer parse rate 100%; exact-checkpoint rate 100%.
- Models: Qwen3-4B `1cfa9a7208912126459214e8b04321603b3df60c`; Qwen3-1.7B `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.

This was a smoke-only run. It did not enforce study-scale balance gates or score a scientific test set. The smoke source-gate JSON therefore records expected small-sample gate failures; these do not indicate a full-run gate failure. The downloaded output files preserve the source records, receiver contract, features, protocol, code hashes, logs and exit code.
