# 04: PCS6 reasoning continuation (L4): FREEZE

**L4 claim.** B does not just receive a fact. It **continues A's in-progress reasoning**: it generates its own next steps from A's internal state, and ends where A would have ended, including when A's trajectory was wrong.

Models: A = Qwen3-4B, B = Qwen3-1.7B, both frozen. Greedy decoding throughout.

---
## Track 6A: controlled continuation (primary)

### Task
- **Program:** a three-register mod-10 program (a, b, c), the same generator family as PCS3/PCS4v2 (`+` and `*` operations, constants and register operands). It has total depth **D = 11** update lines in the public input P.
- **A's working:** A is prompted, using the fixed PCS4v2 compact prompt (amendment 1), to write one line per step, `s_k: a=_ b=_ c=_`, then `FINAL: a=_ b=_ c=_`.
- **Handoff point:** N = 8, so B must perform M = 3 further steps.

### Checkpoints (two variants, same episodes)
- **6A-W (written, primary):** immediately after A has written the complete `s_8` line (its newline token).
  - Capture positions: the end of the `s_7` line, the end of the `s_8` line, and the checkpoint. That gives 3 positions × 9 layers (4, 8, …, 36).
- **6A-U (unwritten, secondary):** immediately after A writes the `s_8:` prefix, **before any s_8 value token**. A's s_8 values are therefore computed internally but not yet in text.
  - Capture positions: the end of the `s_7` line and this checkpoint.

### B's input in every arm
`chat(P + "\n\n" + [ARM CONTENT] + "\n\nContinue the computation from step 9 to step 11 in the same line format, then write FINAL: a=_ b=_ c=_")`

B **generates**, greedy, max 120 tokens. Parse with the PCS4v2 parser (amendment 1).

- **Fidelity target:** A's own FINAL triple (A's greedy trace continues past the checkpoint).
- **Objective target:** symbolic truth.

### Arms
| Arm | ARM CONTENT |
|---|---|
| restart | (none) |
| partial-text handoff | A's private working up to the checkpoint, in a fair format validated on val |
| oracle-state | `State after step 8: a=<A's s8 a> b=… c=…` |
| **PCS (neural)** | 4 continuous prefix slots from the bridge, inserted at the arm position |
| token-identity PCS | Same bridge architecture; input = one-hot of A's written s7/s8 digits. 6A-W only; undefined for 6A-U because s8 is unwritten |
| 3× matched wrong PCS | Prefix from another test episode with a different A-s8 triple |
| zero, random | zero or norm-matched random prefix |

### RQ6 qualification (inference only; run first; Kaggle or Modal)
Pool of 1,600 episodes. Gates:
1. **A competence:**
   - A's final-triple accuracy ≥75%;
   - parse ≥95%;
   - checkpoint location ≥98% for both variants.
2. **A mistakes:** A's s8 triple differs from truth in ≥40 episodes, with ≥15 in what will be the test split.
3. **Receiver can continue:**
   - B oracle-state strict final-triple fidelity to A ≥70%;
   - B partial-text ≥70%.
4. **Inheritance matters:** B restart fidelity ≤ min(oracle-state, partial-text) − 30 pts.
5. **Source decodability** (linear probe; train/val; concatenated captured features):
   - 6A-W: each register of A's s8 ≥80%;
   - 6A-U: each ≥70%. If 6A-U fails, run 6A-W only and report the 6A-U decodability.

If gate 3 or 4 fails at M=3: rerun RQ6 once with **M=2**, as pre-registered, keeping D=10. If it still fails, stop. If a 6A gate fails, stop 6A and report.

### Splits
Train 900 / val 200 / test ≥400, after gates, seeded `20261006`.

### Bridge objective: decision rule D1 (mechanical, fixed now)
Training target: **A's own continuation tokens** after the checkpoint, i.e. the steps 9–11 lines and the FINAL line. Teacher-forced cross-entropy for B with the prefix, using the PCS4v3 **information-weighted** loss (weights from B-restart surprisal).
- **D1-a:** if L3 is reached by PCS4v3 or PCS4v4 (exploratory read), use exactly the L3-passing objective: info-weighted, plus the contrastive term if v4 was needed. The claim is **"label-free reasoning continuation"**.
- **D1-b:** otherwise, use the same objective **plus** a readback auxiliary: B answers "What were a, b, c after step 8?" against A's s8 triple, at λ = 0.25 as in PCS2b. The claim is **"state-supervised reasoning continuation"**.

Other settings:
- bridge = the W1-chosen writer config;
- 40 epochs;
- selection by val loss;
- the same objective for the token-identity arm.

### PCS6-A positive criteria (neural, 6A-W)
1. Strict final-triple fidelity to A ≥60%.
2. **State specificity:**
   - PCS minus mean matched-wrong ≥30 pts, with cluster CI > 0;
   - exact McNemar vs each wrong state;
   - under wrong states, B's final equals the **partner's** A-s8 propagated through *this* program's steps 9–11 in ≥40% of records. This is the swap test.
3. PCS minus restart ≥30 pts.
4. **Trajectory fidelity on A-wrong episodes** (n ≥ 15 test episodes): PCS follows A's (wrong) final ≥ mean wrong-state follow-rate + 25 pts.
5. Beats zero and random by ≥20 pts.

**Descriptive (no gate):**
- PCS vs partial-text and oracle-state;
- token-identity ceiling;
- held-out continuation lengths M=2 and M=4, on separate test episodes generated with D=10 and D=12 and the same N=8;
- prefix size in bits compared with text-handoff tokens.

**6A-U:** apply the same criteria and report them separately. A pass supports **"continuation from a step A computed but had not yet written"**.

**Classification.** `L4_POSITIVE_{LABELFREE|SUPERVISED}`, `L4_NEAR_MISS` (only criterion 1 fails, but ≥50%), or `L4_NULL`.

---
## Track 6B: natural reasoning (EXPLORATORY; runs after RQ6-B passes)

**Data.** GSM8K train (bridge training) and test (evaluation).

**A.** Qwen3-4B, non-thinking, greedy step-by-step solution ending `Answer: <number>`.
- **Checkpoint:** the end of the sentence in A's solution closest to 50% of its tokens. There must be at least 2 sentences before it and 1 after.
- **Capture:** the last token of each sentence before the checkpoint (at most 8, the most recent kept), plus the checkpoint position.

**B arms:**
- restart: the problem, solve;
- partial-text: the problem plus A's first half, continue;
- PCS: the problem plus prefix, continue;
- 3 matched wrong PCS: other problems' prefixes with a similar checkpoint fraction;
- zero.

**Fidelity target:** A's final answer. Objective target: the gold answer.

**RQ6-B gates:**
- A accuracy ≥75%;
- ≥60 A-wrong test problems;
- B partial-text agreement with A ≥ B restart agreement + 10 pts, both overall and on A-wrong problems.

**Bridge.** The D1 objective on A's continuation tokens, using the train split (A's solutions generated on about 3,000 train problems).

**Exploratory read (pre-stated):**
- PCS agreement with A minus mean wrong-state agreement, with cluster CI lower bound > 0;
- on A-wrong problems, PCS reproduces A's specific wrong answer more often than restart, by ≥10 pts.

Report everything else descriptively. No confirmatory claim is made from 6B.

---
## Order
1. **RQ6:** 6A and 6B qualification, one inference job.
2. **6A bridge:** once RQ6 passes, W1 is chosen and D1 is resolved.
3. **6B bridge:** if RQ6-B passes.

Seal, hash and audit as per the global rules in `00_ROADMAP_AND_PACKAGE_INDEX.md`.
