# EXT1 Amendment 2: receiver readout (Claude, designer), 2026-10-05

Made **before any EXT1 full-run data exists**. The trigger is a smoke result only.

**Trigger.** In GPU smoke `fc-01M46PPNDZ7RGAVZRP5E54EW7S`:
- the LatentMAS transfer, quarantine and attenuation mechanics all worked;
- but **0 of 28** receiver outputs were scorable. Qwen3-4B, in its default thinking mode, reasons at length and hits the 256-token cap mid-thought.
- The raw outputs show B *using* the inherited cache, e.g. it recalls the private table. So this is a readout failure, not a scientific result.

This is the same class of fix as RQ7 Amendment 1, and it does not engage the pre-grant stop rule. That rule governs full-run outcomes.

## Change: two-stage readout, applied identically to every arm and condition
1. B generates with LatentMAS's default receiver settings (thinking enabled), **cap 1,024 new tokens**.
2. If the output contains a closed `</think>` followed by a final answer, parse the **last single digit** after `</think>`.
3. Otherwise (cap hit, or no parseable answer), **force a readout:** append `</think>\n\nThe answer is ` (closing the think block if still open), then take the argmax over the ten digit-token logits at the next position.
4. Record per record: `readout_mode` ∈ {natural, forced}, the generated token count, and whether the cap was hit.

## Reporting
- Report every criterion **overall** and **split by readout mode**.
- **Validity gate (a new prerequisite, checked on the smoke):** the forced-readout rate must be **≤ 60%** in the CORRECT arm, so that most answers are natural. If it exceeds 60% on the smoke, B is mostly being cut off. In that case use the cap of 2,048 instead and re-smoke once. If it still exceeds 60%, stop EXT1 and report.

## Unchanged
Everything else in freeze 21 plus Amendment 1: arms, criteria, mitigations, N = 800, seeds, statistics.

**Cost note:** the longer cap raises EXT1's estimate to about $3–6. That fits the remaining `modal-new-account` budget.
