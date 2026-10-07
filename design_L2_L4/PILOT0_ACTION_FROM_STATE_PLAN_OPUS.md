# Pilot 0: reading the next action from pre-output state (Opus), 2026-10-07

**Status: EXPLORATORY.**
- CPU only.
- Re-analysis of saved MON3b data: no new model runs.
- Plan committed before computing.

**Question:** before Qwen3-4B writes anything, does its internal state reveal which tool it will call, beyond what the visible prompt already reveals?

**Data:** the MON3b saved records and features (`modal-account-A:/mon3b-ba249a052386/`).
- 5,600 episodes, from a file-assistant agent.
- Features: 9 layers × 2 positions × 2,560, captured at the end of the prompt, before any output.
- Splits as sealed: train 2,880 / val 720 / test 1,200 / testU 800.

**Targets (from the sender's recorded calls):**
- **T1:** the first tool (list_dir, read_file, delete_file, write_file).
- **T2:** the second tool, for episodes with ≥ 2 calls. This reads one step further ahead.
- **T3:** whether the first call is read-only (list_dir or read_file). This is the prefetch decision.

**Monitors:**
- **LATENT:** PCA-256, then standardise, then multinomial logistic regression, fit on train.
- **TEXT:** TF-IDF (1–2 grams) over the full visible input (system + prompt).
- **STACK:** a logistic regression over [LATENT probs, TEXT probs], fit on val.
- The C grid is {0.01, 0.1, 1, 10}, selected on val.

**Metrics, on test and testU:**
- accuracy and macro-F1;
- STACK − TEXT and LATENT − TEXT accuracy, with a task-clustered bootstrap (2,000 resamples, seed 0);
- **T4, the prefetch operating point:** for `list_dir`, which takes no arguments so a prediction fully determines the call, the share of true `list_dir` first calls caught at a threshold set on val for ≤ 5% wrong prefetches.

**Reading:**
- If STACK − TEXT has a CI above 0, internal state adds action information beyond the prompt.
- If not, the prompt already gives the action away, and reading cognition adds nothing here.
- Report either way.
