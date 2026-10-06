# EXT1 Amendment 3: direct single-pass readout, for feasibility (Claude, designer), 2026-10-05

Made **before any EXT1 outcome data exists**. The aborted full run (`fc-01M46VNG0QR801MC4PM2WN8HQW`, cancelled about 1.5 h in) had not completed its validation stage. No validation or test outputs were written or read.

**Trigger.** Amendment 2's readout lets B think for up to 1,024 tokens. Calls run one at a time, about 20 receiver calls per episode across 800 episodes. Projected runtime is **80–130 GPU-hours on L4**: infeasible inside the 6-hour Modal limit and the budget.

## Change: one readout, applied identically to every arm, condition and mitigation
- B's prompt is rendered with the Qwen3 chat template with **`enable_thinking=False`**, and the assistant turn is pre-filled with `The answer is `.
- **The readout is the argmax over the ten digit-token logits at the next position.** That is one forward pass per call, with no generation. It is the same method used in RQ7 Amendment 1, PCS7, PCS7b and GEN1.
- LatentMAS's sender side (latent-thought steps and the KV transfer path) is unchanged, so A still "thinks" in latent space exactly as LatentMAS does.
- Batch receiver calls where cache shapes allow. Otherwise calls stay sequential, but each is a single forward pass.

## Descriptive cross-check (no criteria)
On the first 50 test episodes only, re-run the CORRECT, MISMATCHED and condition (i) arms with Amendment 2's thinking readout (1,024-token cap, forced fallback). Report agreement with the direct readout. This shows whether the direct readout under- or over-states inheritance and authority relative to B's reasoning mode.

## Unchanged
Everything else in freeze 21 plus Amendments 1 and 2's reporting: arms, prerequisite and primary criteria, mitigations and λ selection on val, the trade-off curve, N = 800, seeds, statistics.

**Validity note.** The prerequisite (CORRECT − MISMATCHED ≥ 20 pts) now also checks that B can use the inherited cache *without* explicit reasoning. If it fails, EXT1 stops per Amendment 1, and the result is reported as "under direct readout", alongside the 50-episode thinking cross-check.

**Expected cost:** under $2 on L4.
