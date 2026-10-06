# RQ7 Amendment 1 earlier real-model GPU smoke

Status: **superseded by the Amendment 1b 10-episodes-per-cell rerun** in [`amendment_1b_10_per_cell/SMOKE_REPORT.md`](amendment_1b_10_per_cell/SMOKE_REPORT.md). This file remains as the record of the initial 2-episodes-per-cell smoke below.

- Modal call: `fc-01M44N3PAX2XB124Q6S62BG7P6`
- Modal app: `ap-ZNAlUsJNdLZAxM2KELMPdP`
- Remote output: `/artifacts/rq7-qualification-f1b9f41250d9/real-model-gpu-smoke`
- Runner SHA-256: `f1b9f41250d991564d0977c4af3b4d08856aeeac91b6bc2c5a72d553e6344b73`
- Exit code: `0`; elapsed time: 44.69 seconds (600-second function limit)
- Protocol: `rq7_qualification_v2`; 12 episodes total, 2 per cell; no qualification choice was emitted.

## B-oracle readout

The restricted digit readout returned a valid-format result on **12/12 (100%)** B-oracle rows. It matched the true task answer on **2/12 (16.7%)**. Validity is guaranteed by the readout construction and is not evidence that B computed the answer.

| Cell | B-oracle valid | B-oracle correct |
| --- | ---: | ---: |
| F1 add, depth 1 | 2/2 | 1/2 (50%) |
| F1 add, depth 2 | 2/2 | 1/2 (50%) |
| F2 add mod 100 | 2/2 | 0/2 |
| F2 multiply mod 100 | 2/2 | 0/2 |
| F3 lookup, depth 1 | 2/2 | 0/2 |
| F3 lookup, depth 2 | 2/2 | 0/2 |

This is a very small smoke sample, not qualification evidence. The raw records show B's base-100 oracle and restart arms returning `07` on the four base-100 rows. A read-only prompt/scoring audit found no confirmed assembly or label bug. I also loaded both pinned tokenizers locally with `local_files_only=True`: their digit IDs are 15–24; the answer anchor ends with token 220, and both one-digit and all 100 two-digit strings tokenize as the expected anchor-plus-digit-ID sequence. That rules out the specific isolated-versus-context digit-token mismatch concern for these pinned revisions, but does not explain the model's low direct-readout accuracy.

The smoke evaluated 2 rows per cell against 300 required for qualification. All cells therefore remain non-qualifying and `RQ7_CHOICE.json` is absent. The local run artifacts (`RQ7_RESULT.json`, `RQ7_GATE.json`, `RQ7_PROTOCOL.json`, `RQ7_RAW.jsonl`, `CODE_SHAS.json`, `EXIT_CODE.txt`, `modal.log`, and `run.log`) are in this directory.
