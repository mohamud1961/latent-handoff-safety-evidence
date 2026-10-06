# W1 resolved real-model GPU smoke

- Modal profile: `modal-account-A`
- Successful call: `fc-01M44FPWVPD10JX2QDEX7PX0Y9`
- Modal app: `ap-tvRkPzQYqkSSWDvLrjxR9o`
- Runner SHA-256: `f49f19039167f656c50da911c30972009c4bc0d9c19d7dabe2fee9d35a122ba3`
- Launcher SHA-256: `a97aab7bbdc0c5af052f7e0b520d0f5900db692a380b60aedfd54bc6df45c3c8`
- Output: `pcs-core-artifacts:w1-gpu-smoke-f49f19039167/`
- Resources: L4, 24 GiB, 600-second timeout
- Result: exit code 0; runner elapsed time 21.807 seconds; exact PCS3 feature SHA and canonical runner SHA verified.
- Work exercised: one pinned Qwen3-1.7B load; canonical neural `train_bridge` and `evaluate`; 8 sealed train rows and 8 sealed validation rows; 24 validation predictions.
- Isolation: no test rows or enlarged test-only features were scored; no official `W1_CHOICE.json` was written.

The first call, `fc-01M44FN5Y89J907KY4F367DM5G`, failed while importing the launcher because its resolutions-file path did not account for the Modal mount location. It ran no model code. The launcher path was fixed and the successful run used a new launcher hash. Both attempts are smoke engineering events, not W1 scientific results.
