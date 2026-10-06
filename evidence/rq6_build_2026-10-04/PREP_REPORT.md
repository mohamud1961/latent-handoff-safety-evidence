# RQ6 qualification build preparation

**Status:** local qualification utilities are implemented and tested; the
frozen experiment remains blocked before inference. No launcher was added.

## Implemented

- `scripts/rq6_qualification.py` contains pure-Python state/final parsers,
  character-offset-only step-prefix lookup, literal GSM8K `Answer:` extraction,
  strict triple scoring, source-episode summaries, 6A/6B frozen-threshold
  gate helpers, the registered M=3 to M=2 retry decision, and a fail-closed
  preflight. It imports no model runtime and performs no model load.
- `tests/test_rq6_qualification.py` covers parsing, duplicate/missing step
  handling, exact triple scoring, source summary denominators, qualification
  thresholds, retry behavior, and blocked preflight behavior.
- `design_L2_L4/BUILD_QUESTIONS.md` has an RQ6 section describing the protocol
  questions that must be resolved before inference.

## Local verification

- `python3 -m pytest -q tests/test_rq6_qualification.py`: **11 passed**.
- `python3 scripts/rq6_qualification.py --smoke --out-dir evidence/rq6_build_2026-10-04/cpu_smoke`:
  **passed**. The synthetic source and continuation traces parse, strict
  scoring runs, and the output records that no experiment/model/external
  service was used. This is engineering smoke evidence only.
- `python3 scripts/rq6_qualification.py --preflight --out-dir evidence/rq6_build_2026-10-04`:
  **exit 2 as designed**, status `blocked`, 15 unresolved protocol blockers.
  The preflight runs before any model import or load.

## Blocking protocol findings

The RQ6 freeze requires the PCS4v2 amendment-1 prompt/parser, which only handles
`STATE s0`–`STATE s8` and `FINAL_SUMMARY:`, while RQ6 requires states through
s11 and `FINAL:`. The split is also ordered “after gates” despite source-probe
gates needing train/validation and a mistake gate needing the test split. Other
unresolved items include the 6A-W duplicate checkpoint position, tokenizer
boundary and checkpoint-location rules, probe definition, partial-text
selection, M=2 retry sample relationship, exact model revisions, and GSM8K
prompt/answer/checkpoint/matching details. The machine-readable list is in
`RQ6_PREFLIGHT.json` and `scripts/rq6_qualification.py`.

No GPU, Modal, Kaggle, model download, or external service was accessed. The
frozen experimental thresholds and conditions were not changed. No files in
the W1 implementation scope and no `BUILD_REPORT.md` were edited.
