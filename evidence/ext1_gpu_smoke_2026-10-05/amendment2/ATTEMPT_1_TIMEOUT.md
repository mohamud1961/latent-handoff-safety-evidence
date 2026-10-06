# EXT1 Amendment 2 GPU smoke — attempt 1

- Modal call: `fc-01M46T09T7SE1Q7YVVY4CRFDMY`
- Profile: `modal-new-account`
- Runner SHA-256: `bf19d5cb8ea7ec5f2ac507de11a18713229d74f950dcc709389515e9500e273b`
- Remote output directory: `/artifacts/ext1-gpu-smoke-bf19d5cb8ea7`
- Outcome: Modal function timed out at its configured 600-second limit.
- No smoke result was returned, so the CORRECT-arm forced-readout gate is unscorable. The EXT1 full run was not launched.

The next smoke keeps the 1,024-token receiver cap and all full-run arms and criteria unchanged. It reduces only the smoke workload so the integration check can finish within its 10-minute limit.
