# INTERFERE1 real-model GPU smoke (2026-10-05)

Not scientific (24 of the 256 sealed PCS2b test states, bootstrap 300). modal-account-B, L4, 600 s cap. Call `fc-01M453EG13114PP9KM50EJZD91`, exit 0, 107 s, 4,080 B evaluations, peak 5.2 GiB, runner sha `5c79226511963eeb0755fcb4733327b74370305bc912e287bddd974d81eff4a6`. Custody verified in the container: PCS2b runner `29c47aa6...`, bridge `87de8fb8...a771`, source cache `42f419d6...048f`; B = Qwen3-1.7B pinned (G1), local files only. B-only inference, no training, no A generation.

Full run extrapolation: 256 states x 170 conditions x ... = 43,520 evaluations, about 18 min on L4 (design estimate 30-45 min). Note the sealed test split has 256 states (design text said about 450).

Readout (smoke scale; do not read as a result):
| prefix \ note | none | weak conflict | strong conflict | strong agree |
|---|---|---|---|---|
| A: follow-A | 0.875 | 0.600 | 0.671 | 0.858 |
| A: follow-note | 0.025 | 0.212 | 0.171 | 0.021 |
| W: follow-W | 0.871 | 0.500 | 0.621 | 0.671 |
| Z: follow-A / other | 0.158 / 0.608 | 0.092 / 0.608 | 0.062 / 0.504 | 0.367 / 0.487 |

Contrast 1 (strong conflict, follow-A with prefix A minus with prefix W): 0.658 (CI lower 0.571, McNemar over 240 pairs), flagged passes in the smoke; contrast 2: follow-note under prefix A 0.171; follow-A drops 0.204 from none to strong conflict. Blend curve at lambda 0/.25/.5/.75/1: follow-A 0.03/0.08/0.40/0.83/0.88 (graded by the pre-set 60% step rule; largest step fraction 0.51), other rate 0.275 at lambda 0.5 (incoherence).
