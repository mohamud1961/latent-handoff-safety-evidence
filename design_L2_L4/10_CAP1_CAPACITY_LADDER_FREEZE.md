# 10: CAP1 capacity ladder, from compressed to uncompressed C: FREEZE (descriptive, with one primary contrast)

**Question.** How does the size of the portable state change:
- how much of A's cognition reaches B;
- what else it carries (leakage);
- how inspectable it stays (monitorability)?

At the top end, C is not compressed at all.

**Data.** The PCS3c fresh source data and sealed splits (design 01 Part B), using the same multi-position capture, extended as below. This is a secondary analysis of the PCS3c test set, and is labelled as such. **It runs after PCS3c's confirmatory evaluation is complete.**

## Arms (identical training budget: 40 epochs, val-loss selection, W1-chosen optimiser settings)
| Arm | Portable state | Approx. size |
|---|---|---|
| C16 | encoder → C (16) → decoder → K=4 slots | 16 numbers |
| C64 | C = 64, K = 4 | 64 |
| C256 | C = 256, K = 8 | 256 |
| C2048 | C = 2048, K = 16 | 2,048 |
| NOBOT | no bottleneck: encoder → K = 16 slots × 2,048 directly (PCS2b-style) | 32,768 |
| FULLSEQ | **uncompressed in sequence**: every token of A's private working up to the checkpoint (cap 256 tokens), layers 16 and 28 only. Mapped by a shared per-token MLP into B's embedding space, giving a prefix of length L (L = A's trace length) | L × 2,048 |
| TI-x | token-identity ceiling for each arm's architecture | — |

## Metrics per arm (PCS3c test; state-cluster bootstrap)
1. **Fidelity:** overall and per selector.
2. **Specificity:** Δ vs strong matched wrong; swap rate.
3. **Mistakes:** A-mistake follow-rate excess.
4. **Leakage:** S1-style within-stratum nuisance probe (initial registers; operation counts), as balanced accuracy on the portable state.
5. **Monitorability:** linear-probe accuracy for each register from the portable state (train/val fit, test score).
6. **Bits:** nominal state size × 16 bits.

## Primary pre-registered contrast
**FULLSEQ − C16 fidelity**, with cluster CI. Read it as follows:
- **lower CI > 0:** compression loses cognition that the uncompressed state keeps;
- **CI includes 0:** the compact state already carries what this task needs.

## Secondary, descriptive
- The **fidelity vs bits** curve.
- The **leakage vs bits** curve. Expectation (not a criterion): leakage rises with capacity.
- The **monitorability vs bits** curve.

These three curves form the trade-off figure for the security story: how much state crosses, how faithful it is, and how inspectable it stays.
