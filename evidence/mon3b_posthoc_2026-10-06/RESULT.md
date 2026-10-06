# MON3b post-hoc analyses: EXPLORATORY (Opus), 2026-10-06

Plan: `design_L2_L4/MON3B_POSTHOC_ANALYSIS_PLAN_OPUS.md`, committed in c2bf25d before computing.
- CPU only. No new model runs.
- Inputs: the sealed bridge (sha `a2088a95…`, matches the seal), plus the saved source features and records from `modal-account-A:/mon3b-ba249a052386/`.
- Script: `scripts/mon3b_posthoc.py`.
- **These are post-hoc and must be labelled as such in any claim.**

## A0. Reproduction: PASSED
- M-PCS 0.9673 (sealed 0.9674) and M-TEXT 0.8839 (sealed 0.884).
- Firewall recall at 5% FPR: 97.4%, exactly as sealed.

## A1. Same wording, test-T
Each (template, action) cell has exactly one instruction wording; only the user task varies.

| Cell | n (ACT) | M-PCS | M-TEXT |
|---|---|---|---|
| template 6 / U1 | 137 (98) | 0.790 | 0.868 |
| template 6 / U2 | 157 (134) | 0.981 | 0.937 |
| template 7 / U1 | 160 (46) | 1.000 | 1.000 |
| template 7 / U2 | 146 (32) | 0.952 | 0.619 |
| **Stratified, within wording** | 600 | **0.934 [0.906, 0.958]** | **0.868 [0.827, 0.904]** |

**Reading:**
- The stratified M-PCS score is above the 0.85 line in the plan, so **"persuasive wording" does not explain the signal**: it holds with the wording fixed.
- But the text monitor also stays high within wording (0.868). **Task-level content visible in the prompt also predicts whether A acts.** It isn't simply whether the target file is present; the target file is present in every test episode.
- So the remaining boring explanation is "task features that make A comply". It is not intent, and not wording. Within wording, the latent monitor beats text by ~6.7 points (point estimates; the paired CI was not computed for the stratified statistic).
- One cell (template 6 / U1) has text ahead of the latent monitor.

## A2. Operating points: thresholds locked on clean validation (n = 360)

| Val FPR budget | Val false alarms | ACT blocked (test) | Clean FPR (test) |
|---|---|---|---|
| 1% | 2 | **96.1%** | **1.3%** |
| 5% | 17 | 97.4% | 6.2% (sealed 6.3%, from rounding of fp16 on CPU) |
| 10% | 35 | 97.4% | 8.5% |

- The 1% threshold rests on 2 val false alarms, so it is noisy.
- **Deviation from plan:** harm-with-firewall needs B's generations, which weren't saved, so only recall and FPR are reported.

## A3. Text + latent stack, fit on val only

| Split | TEXT | PCS | STACK | STACK − TEXT | STACK − PCS |
|---|---|---|---|---|---|
| test-T (held-out wording) | 0.884 | 0.967 | 0.971 | **+0.087 [0.059, 0.116]** | +0.004 [0.002, 0.005] |
| test-U (held-out action types) | 0.632 | 0.725 | 0.727 | **+0.096 [0.059, 0.133]** | +0.002 [−0.010, 0.014] |

**Reading:**
- The latent state adds substantial detection on top of text, on both test sets.
- Text adds almost nothing on top of the latent state.

## Allowed claims (post-hoc, labelled)
- "With the threshold locked on validation at a 1% false-alarm budget, the firewall still blocked 96% of handoffs where the sender would act, at a 1.3% clean false-alarm rate on test (post-hoc)."
- "Holding the instruction wording fixed, the pre-output state still predicted whether the sender would act (stratified AUROC 0.93). A text monitor given the task also predicts above chance (0.87), so task features drive part of the signal (post-hoc)."
- "Combining the text monitor with the latent monitor improved on text alone by about 9 AUROC points; adding text to the latent monitor added almost nothing (post-hoc)."
