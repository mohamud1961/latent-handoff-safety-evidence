# 03: S4 selective cognitive filter: FREEZE

**Question.** Can one specific piece of transferred cognition be removed at the handoff while the rest survives and stays usable by the receiver? This is the C_full → filter → C_allowed security primitive.

**Object.** The PCS3 bridge's compact latent **C** (C_dim, between encoder and decoder). The filter acts on C, and the decoder then writes the filtered C into B's prefix. Both LLMs and the bridge stay frozen.

## Stages
1. **S4-dev:** on the PCS3b neural bridge (`evidence/pcs3b_ep40_2026-10-04/`; bridge on the volume). Use the PCS3b data. It is fitted on train, tuned on val, and reported on the PCS3b test pool. It is labelled **development**, because that test pool has been evaluated before.
2. **S4-confirm:** on the PCS3c bridge with PCS3c data. It runs once, only if PCS3c is POSITIVE or NEAR_MISS.

## Target and filters
The target is to **remove register c**. The symmetric run removing register a is reported as a secondary result.

| Filter | Method | Role |
|---|---|---|
| F-LEACE (primary) | closed-form linear concept erasure of c from C (LEACE), fit on train C with A's c-belief as the concept | primary |
| F-train | small MLP g(C)→C′ trained on train: keep B's a/b-selector fidelity (cross-entropy to A-belief) **and** an adversarial c-probe on C′ at chance (gradient reversal) | secondary |
| F-rand | remove a random subspace of the same rank as F-LEACE | control |
| none | unfiltered C | reference |

## Metrics (test)
- **B fidelity per selector** under each filter: a, b and c.
- **Probe recoverability of c from C′:**
  - a linear probe, fit on train C′ and scored on test;
  - an MLP probe.
- **Mistake fidelity on a and b** after filtering, wherever A-wrong records exist.

## Positive criteria (F-LEACE; the same for S4-confirm)
1. **c removed from behaviour:** B's c-selector fidelity ≤ 20%. Chance for a digit is 10%. It must also be **≤ mean matched-wrong-state fidelity + 10 pts**.
2. **c removed from the state:** the linear c-probe on C′ scores ≤ 20%. The MLP probe is reported, not gated.
3. **a and b preserved:** B's fidelity on a and b selectors is **≥ 85% of their unfiltered fidelity** (a relative threshold). The state-specific margin on a and b over matched wrong states stays ≥ 30 pts.
4. **Specificity control:** F-rand reduces c-selector fidelity by < 10 pts.

**Claim if positive.** "A specified component of a transferred cognitive state can be selectively removed at the handoff (it becomes behaviourally and linearly unrecoverable) while the remaining components keep working in the receiver."
