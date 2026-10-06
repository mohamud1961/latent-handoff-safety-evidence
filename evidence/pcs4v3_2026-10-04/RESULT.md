# PCS4v3 (information-weighted label-free objective, EXPLORATORY): result

Modal `modal-account-B`, call `fc-01M43MT631KRK82VEN48GMXQKC`.

| Category | Neural Arm F | Token-identity Arm F | Matched wrong | Zero | Text oracle |
|---|---|---|---|---|---|
| Derived (n=768) | 6.9% (Δ −0.5 [−1.5, +0.4]) | 11.3% (**Δ +3.9 [+0.7, +7.2]**) | 7.4% | 7.8% | 100% |
| Source mistakes (n=98) | 2.0% (Δ 0.0) | 14.3% (Δ +12.2 [−1.3, +26.7]) | 2.0% | 4.1% | 100% |
| Equality (n=256) | 22.7% | 26.6% (Δ +3.9 [+1.2, +6.6]) | 22.7% | 77.3% | 72.3% |
| Shift+1 (n=256) | 19.1% | 19.1% | 19.1% | 19.1% | 94.9% |

## Pre-stated read (PCS4v3 freeze)
- **Token-identity Arm F:** it beats matched wrong states on derived beliefs, with the cluster-CI lower bound above 0. **PASS (weak, +3.9 pts)**: information weighting starts to force content into the prefix.
- **Neural Arm F: NULL.**

## Mechanical consequences
- **Design 02 trigger:** the token-identity arm passed and the neural arm did not, so **run PCS4v4 (contrastive) on the neural arm only**.
- **L3 status:** not reached.
- **Design 04 rule D1:** PCS6 uses **D1-b** (state-supervised continuation) unless PCS4v4's neural arm reaches the L3 read.
