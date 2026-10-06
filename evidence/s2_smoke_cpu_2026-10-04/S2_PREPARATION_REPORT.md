# S2 preparation report

Date: 2026-10-04

## Scope

This is an offline preparation build. It implements CPU-testable S2 transforms,
loss/metric helpers, and a synthetic smoke. It does not implement the end-to-end
PCS2b extraction, training, or evaluation pipeline. The scientific CLI is
fail-closed, and the Modal launcher is explicitly disabled. No model
checkpoint/source-cache files, Modal services, or GPU jobs were accessed; only
the local PCS2b runner and custody manifest were inspected.

Scientific choices still needing review are listed in
`design_L2_L4/BUILD_QUESTIONS.md` under **S2 covert channel**. In particular,
the test fixture's protocol values and smoke-only seed are not experiment
approvals.

## Local validation

Commands run from the repository root:

```sh
python3 -m py_compile scripts/s2_covert_channel.py scripts/modal_s2_covert_channel.py tests/test_s2_covert_channel.py
conda run -n base python -m pytest -q tests/test_s2_covert_channel.py
conda run -n base python scripts/s2_covert_channel.py --smoke --out-dir evidence/s2_smoke_cpu_2026-10-04
```

Results: syntax check passed; **13 tests passed**; synthetic CPU smoke returned
`S2_SMOKE_OK` and exit code `0`. The smoke checked balanced synthetic k=4 bits,
D-PCA (99% threshold), 4-bit coordinate quantization, D-noise at the frozen
0.1 RMS fraction, a synthetic norm bound, BCE+KL gradients with a frozen
synthetic receiver, validation-only beta selection helper, and AUROC helper.
The mechanical D-PCA criterion checks every k=4 bit is at or below 55%; a
unit case with a 52.5% aggregate but one bit at 60% fails as required by the
per-bit bar. Smoke reports `d_pca_rank=15`,
`norm_budget_max_relative_rms=0.1000000164`, and the synthetic receiver
remained frozen. Running the smoke twice produced identical summary JSON
(SHA-256 `5c3a703c7d9fc9ed812c9499defdde9504367bbe10081e9e04b16dddcc53366a`).
These are implementation checks, not PCS2b/model evidence.

The suite emitted only pytest's existing `pytest-asyncio` unset fixture-loop
scope deprecation warning.

## Scientific and Modal gates

Preflight command:

```sh
conda run -n base python scripts/s2_covert_channel.py --out-dir evidence/s2_preflight_blocked_2026-10-04
```

It exited `1` with:

```text
S2_ABORT ProtocolError: scientific S2 requires --protocol-json, --cache, --bridge
```

`S2_GATE.json` records `BLOCKED_BEFORE_MODELS`, `models_loaded=false`,
`training_started=false`, and `scientific_inputs_consumed=false`. The CLI would
also stop after custody preflight: the end-to-end executor is not implemented.

The Modal launcher has `S2_EXECUTOR_READY = False`; its unit test invokes the
local entrypoint with a stub Modal module and confirms it raises the
dispatch-disabled error before any `.spawn` call. No Modal CLI/API call was
made.

## Pinned local code inputs

- PCS2b canonical runner SHA-256:
  `29c47aa64ef482e0654052df223dc1b9596c0a23bfbb93ddb5d5959562b8949c`
- S2 runner SHA-256 at report time:
  `5444e6e615559285bfd1f0591331b658cdaf2b06563ce8387f7527b3e285eb4c`
- Modal launcher SHA-256 at report time:
  `1123d985a3fda77d15f2bcad730fa32c0d5aea6788bd5c2b3b612d2b283839a0`
- Focused tests SHA-256 at report time:
  `f1735df8a5f5bbb2a6e4b0c3631c6b83b58c317915575173f2b3337e42de9454`

The smoke artifacts (`S2_SMOKE_SUMMARY.json`, `CODE_SHAS.json`, `run.log`, and
`EXIT_CODE.txt`) and the blocked preflight artifacts are alongside this report.
