# Pilot 1, Amendment 1: file read by name, not list position (Opus), 2026-10-07

**Status:** post-hoc re-analysis. It was written **after** seeing the original file-index result (k0 17.5%, k2 26.8%), and is committed before computing the new numbers. The original result stays as sealed.

**Why:** the original label was the file's *index in a shuffled listing*. A linear probe on a state that encodes the file's identity can't map identity to a per-task position. File names come from a fixed pool of 27 (24 ordinary + 3 special), so the natural label is the **name**.

**Change, for file targets only:**
- **Label:** the `read_file` argument (file name). Turns where the name isn't in the listing are excluded, as before.
- **LATENT / TEXT / STACK:** as in the plan, but over name classes.
- **Prediction is masked to the files listed in that task.** Probabilities of unlisted names are set to 0, then renormalised. The mask uses only the visible listing, and applies identically to every monitor.
- **Secondary, descriptive:** also mask files already read earlier in the episode, which are visible in the context.
- **Read points:** k0 (before output) and k2 (after `read_file(`).
- **Prefetch tier 1:** rerun with the name-based file predictor. Same threshold rule: ≤ 5% wrong on val, reported on test.

Nothing else changes: same data, splits, C grid and bootstrap.
