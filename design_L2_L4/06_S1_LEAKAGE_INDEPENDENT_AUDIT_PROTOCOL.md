# 06: S1 leakage, independent audit protocol (offline; performed by Claude, not the implementer)

**Claim under audit.** `PCS_SECURITY_S1_MINIMALITY_LEAKAGE_RESULT_2026-10-03.md` (executor-reported) says the PCS2b corrected-bridge prefix carries source information beyond the declared state. For example, initial register a is decodable at about 48% balanced accuracy against about 10% chance after conditioning on the declared belief, with within-class permutation p ≈ 0.002.

**Why it needs an independent audit.** It is the only security finding cited externally that hasn't been independently recomputed.

## Protocol
1. **Custody:** fetch the bridge and source cache once from the original Kaggle outputs, and check their sha256 against the evidence manifests.
2. **Reimplement (no executor code).** For each nuisance variable (initial a, b, c; operation counts):
   - compute the prefix for every state;
   - fit a probe that predicts the nuisance variable **within strata of the declared state** (A-belief × target variable);
   - use train/test splits by state.
   - Metric: balanced accuracy.
3. **Nulls:**
   - a within-stratum label permutation (1,000 permutations);
   - the same probe on **zero/random prefixes**;
   - the same probe on **matched wrong-state prefixes** (a leak should follow the source, not the slot);
   - the same probe on the **raw source features**. This is the upper bound: how much of the source's nuisance information survives the bridge.
4. **Confound checks:**
   - is the nuisance variable predictable from the declared state, the program length or the checkpoint length? Stratify on these, or regress them out;
   - repeat the probe on the **pre-answer** bridge as well.

## Verdict rules (fixed now)
- **Leak confirmed:** within-stratum balanced accuracy ≥ chance + 10 pts, with permutation p < 0.01, on both a linear and an MLP probe, and absent on zero/random prefixes.
- **Partial:** confirmed for some nuisance variables only.
- **Not confirmed:** otherwise.

## Output
`evidence/s1_independent_audit_<date>/` containing the script, output and verdict. **Cost: $0, CPU only.**
