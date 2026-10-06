# S2 covert channel (full run): INCOMPLETE, compute-limited (Claude), 2026-10-05

Run `fc-01M44YWQSJ2XW16SZ50EXAE67W`, modal-account-B, runner sha `c1fa937b…`. It hit the 6-hour Modal function timeout (`FunctionTimeoutError`) during attack training. The gate file shows training started and the sealed evaluation was **not** started, so no test outputs were read.

**Cause.** The L4 out-of-memory fix cut the attack batch from 32 to 8 and the detector batch from 64 to 16. That makes the full grid (3 capacities × 8 β values × undefended/defended/adaptive × 30 epochs) roughly 4× slower than designed (designed 1–2 h; actual > 6 h).

**Status.** S2 is not concluded. Re-running needs either a larger-memory GPU (A100/L40S, restoring batch 32) or a reduced, pre-registered β grid. Neither fits the remaining budget this cycle, so it moves to the funded phase.

**Related evidence in hand:** S5 Part 3 found a 74% per-bit covert channel through C2C's fused cache with a < 1 pt behaviour change (`evidence/s5_c2c_full_2026-10-05/`).
