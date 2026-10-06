# PCS roadmap L0–L7 and design package to L4 (Claude/Opus, 2026-10-04)

**Goal: portable cognition.** PCS is not a bridge. It is a model's in-progress cognition becoming a state that another model inherits, continues, evolves and passes on. Bridges are the instrument.

| Level | Proves | Defining experiment | Status |
|---|---|---|---|
| L0 Measurement | real transfer vs generic nudge | C2C audit + wrong-state controls | ✅ `evidence/c2c_pcs1_2026-10/` |
| L1 Fact transfer | a computed value moves A→B, with mistakes | PCS2b pre-answer (+85 pts) | ✅ audited |
| L2 Multi-fact | several values move together | PCS3b (67.5%, near-miss) → **PCS3c** | ⚠️ → design 01 |
| L3 Label-free | the bridge learns what to keep from A, not from our labels | PCS4v3 (running) → **PCS4v4** if null | 🔄 → design 02 |
| **L4 Reasoning continuation** | B **continues A's in-progress reasoning** (trajectory and mistakes), generating its own steps | **PCS6** | ⬜ → design 04 |
| L5 Persistence | state evolves in B and moves on (A→B→A, chains) | PCS5 | later |
| L6 Portability | cross-family, shared state format | cross-family qualification and bridges | later |
| L7 Strong→cheap | big-model cognition keeps a small model useful over many steps | 8–30B → small, τ_uplift | later |

The security layer runs in parallel. **S4 selective filter** is design 03.

## Package (all frozen before build; build by Luna Max; review by Claude; launch by Codex)
| File | Experiment | Depends on | Unlocks |
|---|---|---|---|
| `01_W1_PCS3C_FREEZE.md` | Writer sweep W1, then PCS3c confirmatory 3-value transfer | — (W1 then PCS3c, mechanical rule) | L2 |
| `02_PCS4V4_CONTINGENCY_FREEZE.md` | Contrastive label-free objective | runs **only if** PCS4v3 fails its pre-stated read | L3 |
| `03_S4_SELECTIVE_FILTER_FREEZE.md` | Erase one register from the portable state and keep the others | PCS3b bridge (exists); confirm on PCS3c | security |
| `04_PCS6_REASONING_CONTINUATION_FREEZE.md` | RQ6 qualification, then PCS6-A controlled continuation, then PCS6-B natural reasoning (exploratory) | RQ6 now; bridge objective chosen by L3 outcome rule | **L4** |
| `06_S1_LEAKAGE_INDEPENDENT_AUDIT_PROTOCOL.md` | Independent audit of the leakage claim (Claude does this offline; not built by the implementer) | — | security |
| `07_S2_COVERT_CHANNEL_FREEZE.md` | Hidden payload in the portable state: attack, defence (canonical projection), adaptive attacker | PCS2b bridge (exists) | security |
| `08_MON2_COMPROMISED_STATE_MONITOR_FREEZE.md` | Detect compromised cognition (an injected false premise) from the portable state at the handoff, plus a calibrated firewall | PCS2b bridge (exists) | security / monitoring |
| `09_PCS7_SILENT_COGNITION_FREEZE.md` | Silent (unwritten) cognition: A answers with no written reasoning, and B uses A's state on a new step, including A's silent mistakes | RQ7 qualification (now); D1 rule | **unwritten cognition** |
| `10_CAP1_CAPACITY_LADDER_FREEZE.md` | Portable-state size ladder C16 → C2048 → no bottleneck → full per-token sequence: fidelity, leakage and monitorability against bits | after the PCS3c confirmatory evaluation | capacity / security trade-off |
| `05_BUILD_SPEC_FOR_IMPLEMENTER.md` | Engineering contract for the builder | — | — |

## Order
- **Parallel now:** W1, RQ6 qualification, S4 dev run on PCS3b, S2 covert channel, MON2 monitor and firewall, RQ7 qualification, S1 audit (Claude, offline).
- **Then:** PCS7 main (after RQ7), CAP1 (after the PCS3c evaluation), PCS3c (after W1), PCS6-A (after RQ6 and the L3 outcome), S4 confirmatory (after PCS3c).
- **Conditional:** PCS4v4 (only if PCS4v3 fails).

## Global rules (apply to every design)
- Both LLMs stay frozen. Only bridges, filters and monitors train.
- Selection uses train/val only. The test set is evaluated once. No retries except for documented infrastructure failures.
- **Standard controls:**
  - correct state;
  - ≥3 matched wrong states;
  - zero and norm-matched random;
  - receiver restart;
  - explicit-state text oracle;
  - fair-format text handoff;
  - token-identity bridge (the writer ceiling);
  - source-mistake fidelity.
- **Statistics:** state-cluster bootstrap with 10,000 resamples, plus exact McNemar for the correct-vs-each-wrong comparisons.
- **Seal:** hash the bridges and commit the probe seed before test probes are instantiated. Write raw per-record outputs. Store everything under `evidence/<exp>_<date>/`.
- **Claim discipline:** say "values / states A formed in its private working", unless the unwritten-checkpoint variant passes.

## Status update 2026-10-04 (Claude)
PCS4v3 finished. The token-identity arm shows a weak pass (+3.9 [+0.7, +7.2]) and the neural arm is null; see `evidence/pcs4v3_2026-10-04/RESULT.md`.

**Consequences (mechanical):**
- **PCS4v4 is triggered, neural arm only.** Build and launch it.
- **PCS6 defaults to D1-b** unless PCS4v4 reaches L3.
