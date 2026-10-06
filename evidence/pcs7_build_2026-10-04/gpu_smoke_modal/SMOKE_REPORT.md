# PCS7 real-model GPU smoke

Status: completed as a pipeline smoke only; no scientific qualification claim.

## Run

- Modal call: `fc-01M44HQ7E5880T3230ZTAY0WG0`
- Modal app: `ap-8uHQCl8FATJkKKVkupU24x`
- Profile: `modal-account-B`
- Remote output: `pcs-core-artifacts:/artifacts/pcs7-gpu-smoke-05ee3789ef7b/`
- Bounded runtime: 35.70 seconds; Modal and runner exit codes were both 0.
- Runner SHA-256: `05ee3789ef7b5ad87077d219e7bea9a4e53a75e4fddcf610cc1f1248ddcb9496`
- A: `Qwen/Qwen3-4B` at `1cfa9a7208912126459214e8b04321603b3df60c`.
- B: `Qwen/Qwen3-1.7B` at `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.

## What executed

The job verified baked-file hashes, loaded both pinned models from the cache, generated 12 synthetic source tasks, trained the one-epoch smoke bridge, wrote and verified its bridge/seed seal, and exercised B's soft-state readout path. The smoke used generator-known answer labels only as explicitly marked bridge targets; A's raw generations remain preserved separately.

## Outcome and limit

- A strict numeric format: 0/12.
- Two recorded B soft-state readouts were malformed/truncated (`"1\n\n1\n\n"` and `"1\n\nThe final"`); neither parsed as an integer.
- Both exit codes were 0, so this confirms that the real model/bridge/readout pipeline completed. It does not validate answer transfer or qualification behavior.
- Classification: `SMOKE_ONLY_NO_QUALIFICATION`.

The raw smoke report, synthetic source records, bridge, protocol, code hashes, logs, and exit codes are retained in this directory.
