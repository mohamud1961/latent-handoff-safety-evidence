# Pre-grant stop rule (Claude, designer; user-endorsed direction), 2026-10-05

**EXT1 (amended) and COGMON1 are the final pre-grant experiments.** After both are audited and sealed:

- **Both pass:** stop experimenting.
- **One passes, one is mixed:** stop experimenting.
- **EXT1 fails to reproduce the authority conflict externally:** stop experimenting.
  - Report the failure prominently.
  - Do not rerun until it succeeds.
  - Revise the size of the ask and the framing (the authority problem shown on PCS bridges only).

**No EXT2, COGMON2, MON4, AUTH2 or PCS6 before applying.** Those, plus multi-seed robustness, generality across architectures and models, selective inheritance, provenance and authority, adversarial robustness, and richer cognition, are BlueDot Stage II.

## Claim discipline (applies to the application)
- **GEN1:** "the simple memorisation explanation is substantially weakened." Not "the failure mechanism was found and fixed." REP also generalised, so run-to-run variance motivates multi-seed work.
- **AUTH1:** a proof-of-concept of privilege separation. It preserves inheritance (100%), cannot be spoofed by text (by design), and takes authority only from a separate channel. It does not disable the latent channel. It has not faced adaptive attack.
- **MON3b:**
  - formal results: AUROC 0.967 pre-text, 97% blocked, 92% harm reduction;
  - the "beats text by 0.10" comparison **missed** (+0.083);
  - the 83%-vs-0% downstream action is **descriptive** (B-oracle gate 58.9% < 60%).
- **Never claim "we can read minds."** The defensible claim: "transferred state is an observable causal control surface at the handoff", and only if COGMON1 passes.

## Lead result and approved wording (2026-10-05)
**Application order:** MON3b → INTERFERE1 → AUTH1 → EXT1 (if it passes) → COGMON1 (if it passes) → GEN1.

**MON3b headline (verbatim; matches `evidence/mon3b_rerun_full_2026-10-05/`):**
> Before the sending model produced any output, its transferred internal state predicted whether it would follow a hidden unauthorised instruction (AUROC 0.967). A firewall at the handoff blocked 97% of those handoffs and cut the rate at which the receiving model carried out the unauthorised action from 47% to 4% (−92%), at a 6% false-alarm rate on clean handoffs. In latent agent systems, the handoff may be the only object available to inspect; this suggests it can carry enough signal to intervene before harm.

**Wording notes:**
- "97%" means 302 of 310 handoffs where A would act. It does not mean "flagged transfers".
- Harm means B emitting the instructed action, with all instructed test episodes as the denominator. The firewall criterion passed formally. The B-readiness miss affects only the descriptive inheritance comparison (83% vs 0%).
- Use "highly predictive" and "pre-output internal state". Not "detects malicious cognition". It is instructed intent, not spontaneous scheming.
- Argue architecturally: the handoff may be the only inspectable object. Do not claim to beat a text monitor; that pre-registered bar missed (+0.083 vs 0.10).
