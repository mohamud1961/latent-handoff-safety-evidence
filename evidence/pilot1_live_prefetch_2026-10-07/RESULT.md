# Pilot 1: live read-only prefetch from internal state. EXPLORATORY (Opus), 2026-10-07

- Plan: `design_L2_L4/PILOT1_LIVE_PREFETCH_PLAN_OPUS.md`, commit 447ee85, committed before any data.
- Run `fc-01M4BG7T52CBXHH8FRG848KB0W` on modal-account-C, L4, 23.6 minutes, runner sha `309bbb4d…`.
- Analysis: `scripts/pilot1_analyse.py`.

**Run:** Qwen3-4B in a live, multi-turn file-assistant loop with a simulated filesystem; 1,200 clean tasks and 4,097 turns.
- **Invalid lines:** 422 turns (10%). The model invented tools, most often `rename_file` (197), and those episodes ended there. These turns are excluded from the analysis, leaving 3,675 valid turns.
- **Test turns (994):** read_file 611, list_dir 162, finish 151, write_file 35, delete_file 35.

## Results (test; task-clustered bootstrap CIs)

| Target | Read point | Majority | TEXT (full visible context) | LATENT | LATENT − TEXT |
|---|---|---|---|---|---|
| **Next tool** | k0, before any output | 61.5% | 85.5% | **98.2%** | **+12.7 [10.1, 15.1]** |
| Next tool | k1, after `CALL ` | 61.5% | 85.1% | **100%** | +14.9 [12.2, 17.5] |
| File for `read_file` (index in listing) | k0 | 11.3% | 12.1% | 17.5% | +5.4 [1.5, 8.9] |
| File for `read_file` | k2, after `read_file(` | 11.3% | 12.3% | 26.8% | +14.6 [11.2, 17.8] |

**Tier-1 prefetch at k0 (STACK).** The threshold was set on val for ≤ 5% wrong prefetches; val gave 4.6%.
- On test, **21.2% of the 773 read-only calls had their exact result ready before the model wrote anything**, at a 5.7% wrong-prefetch rate.
- 0 special-file prefetches.

## Reading (exploratory)
1. **The next action is almost fully readable before output, in a live loop: 98% from internal state vs 85.5% from the whole visible conversation (+12.7).** That's stronger than Pilot 0's first-step result (+4.9). As the conversation grows, the state keeps track of where the model is in its plan better than the text does. After `CALL ` it's 100%.
2. **Which file it will read is barely readable with this probe, even after `read_file(` (26.8%).** This is mostly a probe-design limit, not evidence that the file is undecided. The label is the file's *position in a shuffled listing*, which a linear probe can't map from a state that most likely encodes the file's *name*. A candidate-scoring readout would be the right design: score each listed name against the state, or read the model's own next-token preference at k2.
3. **Prefetch works but coverage is limited by the file problem.** Only 21% of read-only calls were prefetched within the 5% error budget. The error budget roughly held (5.7% vs 5%).
4. **Safety reading:** internal state reveals the specific next action (98%) better than the visible conversation does. In a harness, that means earlier and more specific pre-action monitoring.

**Limits:** one model, one synthetic task family; 10% invalid turns excluded; the file label design is weak (see 2); no real latency measured; tier 2 untested; post-hoc analysis choices were fixed in the plan.

**Raw data:**
- `PILOT1_TURNS.jsonl` (in this folder), sha256 `d07b923a…5f093d32`;
- `PILOT1_FEATURES.pt` (252 MB, kept off-repo), sha256 `11f6bba1…9cd715`, on modal-account-C at `/pilot1-309bbb4db533/`.
