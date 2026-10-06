# MON3b supplement: per-episode records and monitor scores (2026-10-06)

This folder makes the headline MON3b firewall result, and the post-hoc analyses, recomputable from public files.

**Files:**
- `MON3B_SOURCE_RECORDS.json`: all 5,600 episodes. Each has its split, condition (clean or instructed), the sender's label (ACT or REFRAIN), its template, action, task, and the private text the text monitor reads. This is the file written by the sealed run `modal-account-A:/mon3b-ba249a052386/` before any capture or monitoring, copied unchanged.
- `MON3B_EPISODE_SCORES.csv`: per-episode monitor scores, recomputed on CPU from the sealed bridge (sha `a2088a95…`, matches `../mon3b_rerun_full_2026-10-05/MON3B_BRIDGE_SEAL.json`), the saved source features, and the unmodified MON3 monitor code. Columns:
  - `p_instructed_mpcs`: P(instructed), handoff monitor;
  - `p_act_mpcs`: P(act | instructed), handoff monitor;
  - `p_act_mtext`: P(act | instructed), text monitor;
  - `firewall_score` = `p_instructed_mpcs × p_act_mpcs`.
- `dump_episode_scores.py`: the script that produced the scores. It needs the withheld experiment code, so it's included for reference.

**Reproduction check:** test-T ACT AUROC from this CSV is 0.9673 (handoff) and 0.8839 (text). The sealed values are 0.9674 and 0.884. The tiny difference comes from computing the fp16 bridge on CPU.

**What you can recompute from these files alone:**
- every AUROC;
- firewall thresholds at any false-alarm budget on clean validation episodes, and the resulting test block and false-alarm rates;
- within-wording (template × action) AUROCs;
- the text + handoff stack.

The 516 MB source-feature tensor is too large for GitHub. It's available on request.
