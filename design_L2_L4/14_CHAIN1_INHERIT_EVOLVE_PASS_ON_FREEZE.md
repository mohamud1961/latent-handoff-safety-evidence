# 14: CHAIN1, inherit → evolve → pass on (A → B → C): FREEZE

**Claude (Opus), designer, 2026-10-05.**

## Claim tested
A's cognitive state is inherited by B. B **evolves** it with a new step, and B's own resulting state is **passed on** to a third model C, which uses it. **A's specific content, mistakes included, survives two neural hops plus an evolution step**, with no text carrying it.

## Base
The PCS2b pre-answer regime: a depth-8 mod-10 chain, and A's private scalar belief v at the checkpoint.
- **Hop 1 (A → B):** the sealed PCS2b bridge, frozen, from Qwen3-4B to Qwen3-1.7B (`pcs2b_bridge.pt`, sha `87de8fb8…a771`).
- **Evolution at B:** B receives P + prefix₁ + update U₁: `v1 = (v + m1) % 10`, with m1 ∈ {1–4} on train and {5–9} held out. B does **not** answer.
- **Hop 2 (B → C):** capture B's hidden states at B's last 2 prompt positions after U₁ (layers 4, 8, …, 28). A new bridge₂ maps these into prefix₂ (4 slots) for **C = Qwen3-4B, a fresh instance with no access to A's context**, so this is also a reverse-direction hop, 1.7B → 4B.
- **C's step:** C receives P + prefix₂ + U₂: `v2 = (v1 + m2) % 10`, then answers greedily with a digit readout.
- Every model sees only the public problem P and the updates. No model downstream of A sees A's text.

## Data
1,600 fresh PCS2b-generator episodes, seed 20261015. Split train 900 / val 200 / test ≥ 450.

## Training
- Only bridge₂ is trained, D1-b style: C's future loss on the A-derived target `((v_A + m1) + m2) % 10`, plus a readback auxiliary ("What is v after the first update?" → `(v_A + m1) % 10`) at λ = 0.25.
- The target uses **A's belief** v_A, not ground truth, so the chain must carry A's cognition, including A's errors.
- 40 epochs, selected by val loss. Seal the bridge and probe-seed commitment `sha256(bridge2_sha ‖ "CHAIN1")` before test.

## Arms (test)
- **CHAIN:** A's real state at hop 1, and B's real state at hop 2.
- **WRONG-1:** a matched wrong A state at hop 1 (3 partners with different v_A, nearest prompt length), followed by the real hop 2. This is the key control: does *A-specific* content survive?
- **WRONG-2:** the real hop 1, but a matched wrong B state at hop 2.
- **Zero** and **random** prefixes at each hop.
- **C_restart:** P + U₁ + U₂ only.
- **Text chain:** A's written text, which is just the answer-free prompt in this regime, so it equals restart; assert this.
- **Oracle chain:** an explicit "v = <v_A>" line given to B, then an explicit "v1 = <B's readback>" line given to C.
- **Token-identity ceiling** for hop 2.

## Positive criteria (test; state-cluster bootstrap 10k, seed 0)
1. **End-to-end fidelity** to `((v_A + m1) + m2) % 10`: ≥ 60% on train-m and ≥ 50% on held-out m.
2. **A-specificity survives two hops:** CHAIN − mean WRONG-1 ≥ 30 pts, with CI > 0 and exact McNemar.
3. **Hop-2 specificity:** CHAIN − mean WRONG-2 ≥ 20 pts, with CI > 0.
4. **A's mistakes pass on:** on test episodes where v_A is wrong (≥ 30), C follows the A-derived wrong target at ≥ mean WRONG-1 follow rate + 20 pts.
5. **Beats restart:** CHAIN − C_restart ≥ 25 pts.

**Claim if 1–5 pass:** "A frozen model's private cognitive state can be inherited, evolved and passed on through a chain of different frozen models via neural state alone, carrying the source's specific content and its mistakes."

## Compute
- B and C forward passes, about 1,600 B captures.
- Bridge₂ training at 40 epochs.
- About 1.5–2 h on L4, about $2, profile modal-account-B (where the PCS2b assets live).
- Requires a ≤ 10-min GPU smoke first.

## Addendum 1 (2026-10-05, before any CHAIN1 build or run): provenance probe, secondary analysis, no extra run
Can traces of **A's original state** still be read after B has evolved it and passed it on?
- Fit an L2-logistic probe (PCA 64 on train; C chosen on val) on **prefix₂** (B → C) to predict **v_A**, A's original belief, 10-way. Also probe for **v1_A** = (v_A + m1) % 10.
- Report test balanced accuracy for each, with bootstrap CIs.
- **Key descriptive:** v_A decodability from prefix₂ *conditional on* v1_A. This is a stratified probe within each v1_A value (a within-stratum probe like S1), and m1 is held fixed by construction within each stratum. Above-chance means prefix₂ carries **lineage**: information about A beyond what B's evolved state needs.
- No pass/fail. It feeds the provenance and lineage research question.
