# PCS4v4 bounded GPU smoke

- Modal call: `fc-01M44MV7KYP23Q5SM2CD1PCZ0Z`
- Modal app: `ap-kmxVJl1HDL8g8t1ML3LiT8`
- Output: `/artifacts/pcs4v4-gpu-smoke-fab7f74fd9d6-8d1ef0a9-d9495ea849`
- Profile / GPU: `modal-account-B` / L4, 24 GiB
- Modal timeout: 600 seconds; helper budget: 540 seconds
- Result: exit code 0; runtime 32.74 seconds; `SMOKE_ONLY_NOT_SCIENTIFIC_RESULT`
- Stage B: one contrastive update over four train examples, with three train-only negatives per query; validation loss 11.6051.
- Readback: copied checkpoint loaded successfully; one validation prediction completed; no test item selected or read.
- The earlier attempt under `pcs4v4-gpu-smoke-fab7f74fd9d6-6be68c98-1a6e19c33c` failed at readback because fp16 cached features were passed to the float32 bridge. The fix explicitly casts readback features to float32; this run passed that path.

The JSON summary, code SHA manifest, and exit code are stored alongside this record. The validation checkpoint remains on the Modal artifacts volume and has a local ignored copy for review.
