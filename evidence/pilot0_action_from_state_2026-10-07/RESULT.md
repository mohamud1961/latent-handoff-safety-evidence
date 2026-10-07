# Pilot 0: next action from pre-output state. EXPLORATORY (Opus), 2026-10-07

- Plan: `design_L2_L4/PILOT0_ACTION_FROM_STATE_PLAN_OPUS.md`, commit 55eee64, committed before computing.
- CPU only. Uses saved MON3b records and Qwen3-4B internal state captured at the end of the prompt, before any output.
- Script: `scripts/pilot0_action_from_state.py`.
- Baselines:
  - **TEXT:** TF-IDF over the full visible input (system + prompt).
  - **STACK:** handoff state + text, fit on val.
- CIs: task-clustered bootstrap, 2,000 resamples.

| Target | Split | Majority | TEXT | LATENT | STACK | LATENT − TEXT | STACK − TEXT |
|---|---|---|---|---|---|---|---|
| T1 first tool (4 classes) | test | 46.2% | 91.2% | **96.2%** | 96.4% | **+4.9 [3.5, 6.4]** | +5.2 [3.8, 6.6] |
| T1 first tool | testU (held-out actions) | 50.7% | 85.3% | **90.2%** | 92.6% | **+5.0 [2.6, 7.6]** | +7.4 [5.4, 9.6] |
| T2 second tool (6 classes) | test | 48.4% | 94.1% | 94.7% | 95.9% | +0.6 [−0.8, 1.9] | +1.8 [0.8, 2.9] |
| T2 second tool | testU | 50.7% | **72.3%** | 65.1% | 75.3% | **−7.1 [−9.8, −4.4]** | +3.0 [1.1, 4.9] |
| T3 first call read-only? | test | 66.2% | 95.1% | **97.5%** | 97.7% | +2.4 [0.9, 3.8] | +2.6 [1.3, 3.9] |
| T3 first call read-only? | testU | 74.9% | 88.1% | **91.4%** | 93.4% | +3.2 [1.1, 5.5] | +5.2 [3.2, 7.4] |

**T4, `list_dir` prefetch (STACK), threshold set on val for ≤ 5% wrong prefetches:**
- test: caught **100%** of the 554 true `list_dir` first calls, at a **7.8%** wrong-prefetch rate;
- testU: 100% caught at **17.6%**.

The threshold doesn't hold its false-alarm target out of distribution.

## Reading (exploratory)
1. **The next action is readable before the model writes anything, and the state adds to the prompt.** First tool: 96% from internal state vs 91% from the full visible input, +4.9 points with a CI above 0. That holds on held-out action types too (+5.0).
2. **Reading one step further ahead works in distribution, but not beyond it.** For the second tool, the state alone equals text on test, and is *worse* than text on held-out action types (−7.1). The combined monitor still helps (+1.8 / +3.0).
3. **The prefetch decision is easy:** read-only or not is 97.5% from state.
4. **Calibration is the weak point.** A threshold set for 5% wrong prefetches gave 7.8% in distribution and 17.6% out of distribution. That's harmless for read-only prefetch with commit-on-real-call, but it is the reason writes must never run on prediction.

**Limits:**
- one model (Qwen3-4B), one read point (end of prompt), one task family;
- some prompts carry injected instructions (MON3b design);
- the text baseline is bag-of-words, and a stronger text model might close part of the gap;
- post-hoc re-analysis.
