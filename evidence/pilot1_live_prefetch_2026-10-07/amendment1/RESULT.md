# Pilot 1, Amendment 1: file read by name. POST-HOC (Opus), 2026-10-07

Amendment: `design_L2_L4/PILOT1_AMENDMENT_1_FILE_NAME_READOUT_OPUS.md`, commit 13d6a50. It was written after seeing the index-label result and committed before computing these numbers. Script: `scripts/pilot1_analyse_names.py`.

| Which file `read_file` opens (611 test turns, 27 names; chance ≈ 10.7%) | TEXT | LATENT | LATENT − TEXT |
|---|---|---|---|
| k0, before any output | 32.7% | 34.9% | +2.1 [−1.9, 6.4] (n.s.) |
| k0, also masking files already read | 40.1% | 41.7% | +1.6 [−3.1, 6.2] (n.s.) |
| **k2, after `read_file(`** | 33.2% | **82.7%** | **+49.4 [45.4, 53.3]** |
| k2, also masking files already read | 40.1% | 82.5% | +42.4 [37.7, 46.7] |

**Tier-1 prefetch at k0** (name readout, threshold ≤ 5% wrong on val):
- on test, 25.1% of read-only calls prefetched exactly, at a **7.6%** wrong rate (above the 5% target);
- `list_dir` covered 97.5%; `read_file` covered 5.9%;
- 15 prefetches targeted special files and would be blocked by the permission check.

## Reading
1. **Fixing the label worked.** Once the model has committed to `read_file(`, its state names the file 83% of the time, against 33% from the visible conversation (+49). The index-label result (26.8%) was a probe-design artefact.
2. **Before any output, the file is not readable beyond text (35% vs 33%).** The tool is decided before the model writes (98%, original analysis), but the specific file is settled during writing, between k0 and k2. That's direct evidence that the decision forms in stages: *what* to do first, then *what to do it on*.
3. **Practical consequence:** reliable early prefetch works for argument-free actions (`list_dir`, 97.5%), not yet for argument choice. The k0 wrong-prefetch rate also exceeded its target on test (7.6% vs 5%).

**Limits:** post-hoc; one model and task family; same caveats as the main result.
