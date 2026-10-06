# PCS4v2b (40 epochs, EXPLORATORY) result: NULL; objective diagnosis

Modal `modal-account-B`, call `fc-01M42W5NPWRV0MA19GDCGSGRE9`.

| Category | Arm F neural (label-free trace regen) | Matched wrong | Zero | Text oracle | Private trace text |
|---|---|---|---|---|---|
| Derived (n=768) | 13.2% | 13.1% (Δ +0.0 [−2.2, +2.2]) | 9.1% | 100% | 80.7% |
| Source mistakes (n=98) | 23.5% | 18.0% (Δ +5.4 [−2.5, +14.1]) | 4.1% | 100% | 87.8% |
| Equality (n=256) | 59.8% | 59.9% | 74.6% | 69.9% | 74.6% |
| Shift+1 (n=256) | 14.8% | 13.7% | 18.0% | 93.0% | 41.8% |

The token-identity Arm F, which has perfect input, is also null or below the wrong-state control.

**Diagnosis.**
- Arm F's training and validation loss converge quickly, to about 0.14 per token.
- The trace-regeneration loss is dominated by format tokens that B can already predict. The few state-bearing digit tokens contribute little.
- So the bridge learns to help with boilerplate, not content.
- The token-identity arm failing too confirms that **the objective is the bottleneck**, not the source features.

**Next (pre-register separately).** Use a label-free **information-weighted** objective: weight each trace token's language-modelling loss by its surprisal under B *without* PCS state, i.e. B restart given the public input. This concentrates learning on information that B lacks. No hand-selected variables are involved.
