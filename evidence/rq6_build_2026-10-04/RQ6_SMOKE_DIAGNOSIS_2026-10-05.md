# RQ6 smoke diagnosis — 2026-10-05

This is implementation evidence for review, not an RQ6 qualification result. Four pinned L4 real-model smokes ran, each with a 600-second Modal ceiling. No full RQ6 run was launched.

## Findings

| Modal call | Runtime | 6A B oracle continuation | GSM8K source A |
| --- | ---: | --- | --- |
| `fc-01M44VHMRR8HKAG7DD5AES2M4K` | 59.13 s | Used 120/120 tokens and stopped mid-equation. No `STATE` lines or `FINAL_SUMMARY`; parser reported missing steps 9–11. | Used 420/420 tokens and stopped mid-solution before an answer line. |
| `fc-01M44VTB0649ZZGS46S4W14NAV` | 85.43 s | Parsed in 63/120 tokens, but repeated the s8 state for s9–s11. | Completed in 518 tokens under the new 768-token cap, but emitted `**Answer: 180**`; the frozen literal-line parser correctly rejected Markdown. This attempt’s diagnostic mistakenly displayed the old 420-token cap; the reporting bug was fixed for later attempts. |
| `fc-01M44W3PP8H37ZMR8RJ6ZJWK18` | 52.63 s | Parsed, but still repeated the s8 state. | Plain-text prompt produced `Answer: 180`, parsed at 287/768 tokens. |
| `fc-01M44WCW71A05ZEYRE3ZGSTMP3` | 88.38 s | Parsed at 72/120 tokens, but still repeated `(6,2,2)` for s9–s11. The generated episode’s symbolic s9–s11 are `(6,2,3)`, `(5,2,3)`, `(5,6,3)`, so the B final state is wrong on this one smoke example. | Parsed `Answer: 180` at 287/768 tokens; did not hit the cap. |

The final attempt also confirmed that A’s 6A source trace parsed, both W/U checkpoint positions were located, and the captured hidden state was finite. Its B output is structurally valid but does not demonstrate continuation fidelity. This n=1 smoke is not an estimate of the registered 6A gate.

## Candidate changes for review

- Added bounded smoke diagnostics: output preview, generated token count, cap-hit flag, exact trace parse errors, parsed step indices, and answer-marker count. The preview is capped at 8,000 characters.
- Made each real-smoke output directory unique to the launcher and runner hashes, preserving earlier attempts.
- Separated GSM8K source A’s generation cap from the 420-token 6A source cap and 420-token GSM8K receiver cap. The candidate GSM8K source A cap is 768 because the original 420-token smoke ended before an answer.
- Added a plain-text instruction to GSM8K A while retaining the resolved literal `Answer: <number>` suffix. The smoke then produced a parseable literal line.
- Replaced the ambiguous 6A continuation instruction with an exact state-line template that pins update numbering and asks B to apply updates 9–11. This removed the earlier prompt contradiction and restored parseability, but did not fix B’s repeated-state answer.
- Pinned these candidate prompt and budget values in `RQ6_PROTOCOL.json`; they require Claude review before a full run.

## Validation and remaining hold

- Focused RQ6 and launcher suite: **17 passed** after the final code/protocol edits.
- Python compilation, protocol JSON validation, and `git diff --check`: passed.
- The final smoke’s exit code was 0. Its report, launcher manifest, code hashes, and exit record are preserved under `real_model_smoke_2026-10-05/diagnostic_attempts/fc-01M44WCW71A05ZEYRE3ZGSTMP3/`.
- Full RQ6 remains held for review. In particular, review the candidate GSM8K cap/prompt and the evidence that B can produce a parseable 6A continuation while still failing the one smoke example’s symbolic continuation.

The full-run command remains:

```bash
MODAL_PROFILE=modal-account-B modal run --detach scripts/modal_rq6_qualification.py --full-run
```
