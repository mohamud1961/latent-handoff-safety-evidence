# Review of the MON2 build (Codex commits 1e38bad, 52ad668): Claude/Opus

**Verdict: NOT READY TO LAUNCH.** Three fixes are required, plus a real model-path smoke run.

## Verified by me
- `tests/test_mon2_contract.py`: **5/5 pass** (run locally).
- The `--smoke` contract path runs. It checks splits (720/180/300) and firewall calibration.
- **Design adherence:**
  - paired clean/injected rows per program;
  - templates T5–T6 used only in test;
  - neutral notes token-length matched to the injected notes;
  - injected digit false after assignment line 5;
  - COMP is "injected belief ≠ clean belief" and REJ is the complement;
  - the bridge is hash-checked before use.
- **Bridge checkpoint:** now uploaded to volume `pcs-core-artifacts` (profile modal-account-B) at `pcs2b-preanswer-state-realization/pcs2b_bridge.pt`. Its sha256 is `87de8fb8…`, which matches the PCS2b manifest.

## Required fixes
1. **The invented gate will almost certainly kill the run.**
   - `_gate_source` requires `all_2400_source_answers_parse_and_have_exact_preanswer_checkpoint`, i.e. 100% of 2,400 A answers. The freeze sets no such gate, and PCS2b itself only required parse ≥90% and exact checkpoint ≥98%.
   - **Fix:** require parse ≥95% and exact checkpoint ≥98%. **Exclude** any pair where either episode is invalid, and report the exclusions. Then compute the COMP/REJ gate on the remaining pairs.
2. **The B prompts don't match the bridge's training distribution.**
   - The receiver arms use a new readback wording (`_readback_query`). The frozen PCS2b bridge was trained on `pcs2b.readback_prompt` and `pcs2b.future_prompt`.
   - The behavioural and harm-to-B metrics would then be measured out of distribution.
   - **Fix:** use the PCS2b runner's own `readback_prompt` and `handoff_render`, exactly as in the PCS2b evaluation, for every B arm.
3. **The model path has never executed.**
   - Before the full launch, add `--gpu-smoke`: 20 programs, 40 episodes, with the real Qwen3-4B, Qwen3-1.7B and the bridge on Modal L4, for about 5–10 min.
   - It runs end to end through generation, capture, prefixes, monitors (on the train split only) and the receiver arms. Gates are reported but not enforced.
   - Codex launches it, and Claude checks its outputs before the full run.

## Process note for the remaining deliverables
The build spec asks for local smoke runs and unit tests. "Stop before anything runs" refers to **GPU and full runs only**. Please run the unit tests and the CPU smoke for every deliverable.

Not yet built: W1, PCS3c, S4-dev, S2, RQ6, PCS6-A, PCS6-B and PCS4v4 (conditional). Suggested order: S4-dev, S2, W1, RQ6, then the rest.
