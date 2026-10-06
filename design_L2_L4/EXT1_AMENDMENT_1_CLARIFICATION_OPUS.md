# EXT1 Amendment 1, clarification of the prerequisite stop clause (Claude, designer), 2026-10-06

Amendment 1 says "Criteria 1–2 (inheritance, swap) become a prerequisite gate" and then gives the stop rule explicitly: **"If criterion 1 fails (CORRECT − MISMATCHED < 20 pts), stop."** The implementation gated the authority test on *all* inheritance criteria, including criterion 2 (swap ≥ 25%). That is stricter than the written stop clause.

**What happened.** Run `fc-01M47F8NBMV4MRJFEJMJ0VVXZE`'s test-inheritance stage (direct readout, 700 episodes) produced:

| Arm | B follows A |
|---|---|
| CORRECT | 90.6% |
| MISMATCHED | 8.8% |
| NONE | 10.9% |
| TEXT | 90.1% |

- CORRECT − MISMATCHED = **+81.8 [79.4, 84.2]**, McNemar 601 vs 1. **Criterion 1 passes.**
- Swap (B follows the partner's value) = **18.4% < 25%**. **Criterion 2 fails.**

The code therefore skipped the authority test. The run was cancelled during the descriptive thinking cross-check, **before any authority-condition data existed**. Its inheritance and validation outputs are preserved.

**Resolution.**
- The gate follows the written stop clause: the authority test runs iff criterion 1 passes, meaning CORRECT − MISMATCHED ≥ 20 with CI > 0, and CORRECT − NONE ≥ 20.
- **Criterion 2 is reported as FAILED** in every summary and claim.
- Nothing else changes. The full run restarts deterministically from scratch on the same seeds.

**Interpretation of the swap failure.** With a wrong sender's cache, B mostly answers with neither value (only 18% the partner's, 9% A's). So the inherited content does not cleanly *replace* B's answer with the partner's. Inheritance (+82) is strong, but substitution is partial.
