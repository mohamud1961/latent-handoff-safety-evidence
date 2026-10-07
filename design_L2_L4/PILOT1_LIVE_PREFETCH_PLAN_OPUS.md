# Pilot 1: live speculative read-only prefetch from internal state (Opus), 2026-10-07

**Status: EXPLORATORY pilot.** The plan is committed before any data exists. It follows Pilot 0 (`evidence/pilot0_action_from_state_2026-10-07`).

**Question:** in a live, multi-turn agent loop, can the harness read the next tool call from the model's internal state *before the model writes it*, accurately enough to prefetch read-only results? And how early in the writing does the call become known?

## Setup
- **Model:** Qwen3-4B (rev `1cfa9a72…`), frozen, fp16, greedy, thinking off.
- **Tasks:** clean MON3 file-assistant tasks only (`gen_task`, new seed 20261107), with no injected instructions and system prompt `BASE_SYSTEM`. The prompt is the MON3 task text, except the model now gets **one call per turn and receives each result**.
- **Simulated filesystem:**
  - each file has deterministic synthetic contents (seeded);
  - for "find" tasks, exactly one ordinary file contains the target word;
  - `list_dir` returns the listing; `read_file` returns contents, or an error if missing;
  - `write_file` and `delete_file` change the simulated state;
  - `send_email` and `http_post` return "ok" and are logged;
  - at most 8 turns.
- **Size:** N = 1,200 tasks. Task-level split 60 / 15 / 25 (train / val / test), seed 20261107.

## Read points, per turn
- **k0:** the end of the context, before any output token of this turn. This is the prefetch point.
- **k1:** after the model writes `CALL `.
- **k2:** after `CALL <tool>(`. Only the argument remains.

State = the last-token hidden state at layers {12, 20, 28, 36}, captured with one teacher-forced forward pass over the turn's actual output.

## Targets and monitors
- **Tool** at k0 and k1 (7 classes).
- **File argument** of `read_file` at k0 and k2: the index of the file in the listing (≤ 11 classes).
- **LATENT:** standardise, then logistic regression; C from {0.01, 0.1, 1, 10}, chosen on val. Fit on train turns.
- **TEXT:** TF-IDF (1–2 grams) over the full visible context so far, including earlier results. Same C rule.
- **STACK:** a logistic regression over both, fit on val.
- CIs: task-clustered bootstrap, 2,000 resamples, seed 0.

## Prefetch simulation
**Tier 1:** prefetch, then serve the result only when the model actually makes the call. This leaves behaviour unchanged by construction.
- At k0, prefetch only if the predicted tool is `list_dir`, or `read_file` with a predicted file. The confidence threshold is set on val so that ≤ 5% of prefetches are wrong.
- **Primary metrics on test:**
  - coverage: the share of actual read-only calls whose exact result was prefetched before the model wrote anything;
  - the wrong-prefetch rate;
  - prefetches of a special file (`secrets.env`, `audit.log`, `monitor.cfg`). These are counted and reported; in a deployed harness they would be blocked by the permission check.

## Readings (exploratory, no pass/fail claim)
- If STACK − TEXT at k0 is above 0 (CI), the state adds information beyond the visible context in a live loop.
- Report coverage at ≤ 5% wrong on val, and the actual test wrong rate.
- Report the "how early" curve k0 → k1 → k2.

**Limits stated in advance:** a synthetic filesystem, one model, one task family; tier 2 (injecting results before the model asks) is not tested.

**Budget:** smoke ≤ 10 minutes, full run ≤ 1.5 h on L4. Account `modal-new-account`.
