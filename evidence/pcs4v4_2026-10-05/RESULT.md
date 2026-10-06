# PCS4v4 contrastive label-free objective: sealed and audited (Claude), 2026-10-05

Run `fc-01M44PP4RF8F68K0Y5H584548Z`, profile modal-account-B, objective `restart_surprisal_weighted_contrastive` (λ=1.0, m=0.5 nats per design 02). Exit 0. Classification: **PCS4V4_L3_NULL**.

| Probe category | Neural (arm F) | Mean wrong | Δ | Cluster 95% CI | n probes |
|---|---|---|---|---|---|
| derived_random | 12.6% | 12.8% | −0.1 | [−1.0, +0.7] | 768 |
| source_mistake | 17.3% | 19.4% | −2.0 | [−5.5, +2.2] | 98 (≥ 25 ✅, ≥ 10 episodes ✅) |

The token-identity arms are also near chance on derived_random (TI-T +4.7 pts, CI [1.2, 8.2]). PCS4v3 showed a weak TI signal; even the writer ceiling is weak in this regime.

**Audit.** Both frozen L3 checks fail: neither CI has a lower bound above 0. This is the fourth label-free null in a row (PCS4v2, v2b, v3, v4). **L3 is not reached.**

**Interpretation (honest).** With these models, data sizes and objectives, a bridge trained only to make B predict A's own continuation does not learn to carry A's specific state. Supervision via readback is still required. This is reported as a negative result.
