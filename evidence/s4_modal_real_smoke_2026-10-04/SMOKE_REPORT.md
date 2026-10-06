# S4 real-model Modal smoke

- Result: completed, exit code 0.
- Modal profile: `modal-account-A`.
- Modal app: `ap-w67joZ37lbCxSu16IDlgXp`.
- Function call: `fc-01M44GDGR7WHHFBY7N11E4MHZB`.
- Runner SHA-256: `64247e9d5350b38b61c3c4f7069aefd228ed221e57b30824dd19c2fb68e33845`.
- Runtime configuration: L4, 24 GiB, 600-second function timeout.
- Scope: pinned PCS3b bridge and source artifacts; deterministic 48-train / 16-validation / 8-test smoke subset; both c-removal and symmetric a-removal paths; 192 per-filter/selector/target records.
- Remote output: `/s4-real-smoke-64247e9d5350` on `pcs-core-artifacts`.
- Scientific classification: `SMOKE_ONLY_NO_SCIENTIFIC_CLAIM`. Small smoke metrics are diagnostic only; no S4 criterion is treated as passed or failed.

The remote run exercised model loading, bridge loading, filter training, test-time receiver evaluation, sealing, and raw-record/summary writes. The first launch attempts exposed local Modal-Python dependency and remote baked-path issues; both were fixed before this completed run. No full S4 development or confirmatory run was launched.

Files in this directory are the downloaded smoke artifacts: exit code, run logs, code hashes, gate, seal, protocol, raw records, and summary.
