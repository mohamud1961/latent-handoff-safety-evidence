# RQ6 Amendment 3: one final rung R4, fixing a designer prompt error (Claude, designer), 2026-10-05

**Trigger.** The Amendment 2 ladder failed for a reason traceable to **my R1 design**, not to B (`AMENDMENT2_LADDER_REPORT.md`). Copying A's source template verbatim kept its instruction "Write exactly N blocks, one per state … K=0..D-1". B obeyed that, restarted from s0, and hit the token cap before update 9. That is a prompt contradiction, the same class of error as RQ7's amendments 1 and 1b. One corrected rung is justified; **there will be no further rungs after it.**

## R4 (D = 10, i.e. the pre-registered M = 2 retry; `enable_thinking=False`; cap 300 tokens)
- **Worked example rewritten as a continuation.** It shows a different program, then "State after step 7: a=… b=… c=…", then **only** the lines for updates 8–9: a calculation line plus a STATE line for each, then FINAL_SUMMARY.
- **Instruction:** "You are given the state after update 8. Write ONLY the lines for updates 9 and 10, in the same style as the example: one calculation line, then one STATE line each. Do not write any earlier states. Then FINAL_SUMMARY:".
- Numbered program as currently pinned. Identical across all receiver arms.

## Probe and decision
- Probe: the same 32 episodes, oracle_state + restart, ≤ 10 min.
- **Oracle ≥ 70%:** pin R4 and run full RQ6.
- **Oracle < 70%:** final STOP_RECEIVER_INCAPABLE. PCS6-A moves to the post-grant larger-receiver phase.
