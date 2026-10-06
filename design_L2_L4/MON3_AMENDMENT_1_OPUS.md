# MON3 Amendment 1: sample size and gate scoping (Claude, designer), 2026-10-05

This amendment is made **before any full-run data exists**. The evidence is the smoke only (`evidence/mon3_gpu_smoke_2026-10-05/`, 40 tasks):
- ACT rate 20% (bank A), concentrated in U1;
- B oracle 55%.

1. **Sample size.** Tasks P go from 1,600 to **2,400** (seed 20261011). The split shares are unchanged, so test-T has about 600 tasks. At about 20% adoption, that gives about 120 ACT, which protects the ≥ 60 ACT / ≥ 60 REFRAIN gate. test-U stays at 400 extra tasks (seed 20261012).
2. **Gate 3 (B oracle readiness) is scoped to criterion 3.** If B-oracle is below 60% on val, MON3 **continues**. Criteria 1, 2, 2b, 4 and 5 (monitoring and firewall) do not depend on B's ability to act. Criterion 3 (inheritance) is then reported **descriptively**, with its numbers and CIs, flagged `B_ORACLE_GATE_FAILED`, and no inheritance claim is made. Thresholds are unchanged.
3. **Adoption gate unchanged:** 15–85%, with one bank-B fallback. **Per-action-type adoption** is reported. Action types with fewer than 10 test ACT episodes are reported but excluded from per-type claims.
4. **Timeout:** the full-run function timeout stays 8 h, which is ample for about 6,400 short generations.

The prompt v3 iterations made during the smoke (tool-list clarity, call budget) were implementation-only, done before any gate, bridge or test data. They are pinned in the runner and accepted.
