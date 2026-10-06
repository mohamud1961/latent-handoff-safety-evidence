# PCS3c confirmatory three-value transfer (fresh data): sealed and audited (Claude), 2026-10-05

**Runs.**
- Training run `fc-01M44ZFJ4E48EKR167BG31BMQ1` (modal-account-A): fresh pool with seed 20261005, W1-b (K = 4, C = 64), 40 epochs, bridges sealed (`PCS3C_BRIDGE_SEAL.json`). It crashed in `summarize_pcs3c` on the exact-McNemar overflow.
- **Evaluation run `fc-01M45GVG8TN8CQQZBB8J9PZX3V`** (`--eval-only`): identical sealed bridges (neural `317b1ff3…`, TI verified), the same probe commitments and the deterministic evaluation, with the McNemar fixed in exact form (`69889f6`). Disclosed in the result.

Classification: **PCS3C_NULL**, per the pre-registered rule: overall fidelity and per-selector criteria failed.

Test set: 959 states, 2,877 records.

| Criterion (design 01) | Value | Pass |
|---|---|---|
| Overall neural fidelity ≥ 70% | **58.1%** | ❌ |
| Each selector ≥ 60% | a 51.3 / b 58.8 / c 64.2 | ❌ |
| Neural − strong wrong ≥ 30, CI > 0 | **+51.7, CI [49.7, 53.6]**; McNemar 1,521 vs 41 (and similar for the other partners) | ✅ |
| Neural − restart ≥ 30 | +43.3 (restart 14.8%) | ✅ |
| Beats zero and random | zero 5.4%, random 8.1% | ✅ |
| Source-mistake directional (≥ 10 states) | 37.2% follow A's wrong value vs 9.3% wrong-state (25 states, 44 records) | ✅ |

Ceilings: token-identity 99.6%, text oracle 100%, private-trace text 97.9%.

## Audit
1. **Specificity is strongly confirmed on fresh data.** When B answers from the latent state, it gives *A's* values for the selected register, not a neighbour's: +52 pts over strong wrong states. It also carries A's specific mistakes (37% vs 9%).
2. **Accuracy is short of the pre-registered bar.** 58% against 70%, below W1's val estimate of 71%. W1's val n was only 128, so a winner's-curse drop on fresh data is expected. Register a is weakest (51%).
3. **The writer is not the bottleneck** (token-identity 99.6%). The limit is how much of A's three-register state the neural bridge extracts.
4. The eval-only re-execution is legitimate: sealed bridges, deterministic decoding, statistics fixed only in an overflow-safe exact form.

## Allowed claim
"On fresh data, a latent bridge carries a source model's specific multi-register working state, including its mistakes, into a different frozen model with +52-point specificity. Absolute fidelity is 58% against a pre-registered 70% target."

**L2 status:** specificity confirmed; the pre-registered fidelity bar was not met. L2 is **not** claimed as fully confirmed.
