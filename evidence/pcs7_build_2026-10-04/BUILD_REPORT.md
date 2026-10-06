# PCS7 executor build report

Date: 2026-10-04

Status: executor implemented; synthetic CPU and bounded real-model GPU smokes completed. PCS7 scientific execution was not launched because the full RQ7 qualification selected no passing cell.

## Delivered

- `scripts/pcs7_silent.py`: PCS7 full executor with a sealed RQ7 input verifier, 1,600-source split and capture, PCS2b-shaped 4-slot bridge, frozen D1-b objective, validation selection, bridge/seed seal, matched wrong-state and other controls, raw outputs, cluster bootstrap, exact McNemar, mechanical criteria, `CODE_SHAS.json`, protocol, gate, result, log, and exit code.
- `scripts/modal_pcs7_silent.py`: Modal L4 launcher, 24 GiB memory. Full execution accepts an explicit RQ7 choice under the RQ7 `full/` output path. The real-model smoke is limited to 600 seconds and uses synthetic tasks; neither launcher mode starts unless invoked. The launcher resolves host paths and baked `/root/scripts` paths separately.
- `tests/test_pcs7_silent.py`: tests the frozen split, synthetic pipeline, fail-closed behavior, complete RQ7 bundle verification, tamper rejection, rejection of RQ7 smoke output, full-denominator treatment of malformed readouts, launcher path resolution, and explicit smoke-only label substitution.
- `cpu_smoke_final/` and `cpu_smoke_metrics_fix/`: synthetic-only smoke reports, raw rows, protocol, code hashes, trained toy bridge, bridge/seed seal, run log, and exit code. The first final bundle is retained as an initial run; the metrics-fix bundle reflects the final scoring code.
- `rq7_smoke_fail_closed/`: PCS7 stop-gate record from passing the available real-model RQ7 smoke directory as if it were the required full choice bundle.

The full runner rejects a missing, smoke, partial, hash-mismatched, edited, or non-passing RQ7 bundle before model construction. It recomputes RQ7 task generation, response parsing, cell scores, and the selected-cell rule. A qualifying artifact must be `RQ7_CHOICE.json` with the complete `RQ7_RESULT`, `RQ7_GATE`, `RQ7_PROTOCOL`, `RQ7_RAW`, and `CODE_SHAS` bundle. Unit coverage verifies the RQ7 bundle and rejects tampering and the smoke-only output. During PCS7, the bridge hash and probe-seed commitment are sealed and reverified before test queries, B baselines, matched controls, or evaluation probes are constructed.

PCS7 records D1-b because the PCS4v3 result says L3 was not reached and the available PCS4v4 reducer output is synthetic smoke rather than reviewed evidence. No sealed W1 choice was present in this checkout, so the runner uses the canonical PCS2b bridge dimensions. Both determinations and their source-file hashes are included in the run protocol/code hashes.

## Validation evidence

Commands run:

```sh
/tmp/pcs-l2l4-cpu-env/bin/python -m unittest tests.test_pcs7_silent -v
/tmp/pcs-l2l4-cpu-env/bin/python scripts/pcs7_silent.py --smoke-only --out-dir evidence/pcs7_build_2026-10-04/cpu_smoke_final
/tmp/pcs-l2l4-cpu-env/bin/python -m compileall -q scripts tests
git diff --check
```

Focused unit tests passed: 8 tests after review. The review caught a denominator asymmetry: malformed B readouts were excluded from baseline accuracy while malformed PCS readouts counted as failures. All arms now use the full test-query denominator, with malformed or truncated responses counted as incorrect; a focused regression test covers this rule. The real-model smoke uses programmatically known task labels as explicitly marked smoke-only bridge targets while retaining A's actual generated output; it therefore tests the real A-feature/B-soft-state path even if strict A formatting fails. The scientific path uses A's parsed answer and is unchanged. The final local CPU smoke trained the synthetic bridge for 2 epochs, evaluated 24 test queries across the PCS, three wrong-state, zero, random, restart, restart-reason, text-handoff, oracle, and token-identity arms, and returned exit code 0 with classification `SMOKE_ONLY_NO_QUALIFICATION`. The recorded smoke duration was 2.74 seconds. These measurements are pipeline checks only and are not qualification evidence.

The Modal launcher also uses explicit host/container layouts and hashes baked files from `/root/scripts`; a test covers both paths. This avoids import-time failures when Modal imports the launcher from `/root` while the sources live under `/root/scripts`.

The bounded real-model Modal smoke completed with exit code 0 in 35.70 seconds (call `fc-01M44HQ7E5880T3230ZTAY0WG0`, app `ap-8uHQCl8FATJkKKVkupU24x`, output `pcs-core-artifacts:pcs7-gpu-smoke-05ee3789ef7b`). It loaded the pinned A and B revisions, generated 12 synthetic source tasks, trained the one-epoch smoke bridge, sealed it, and exercised the B soft-state readout. A's strict numeric format was valid on 0/12 source generations; both recorded B readouts were malformed/truncated. Thus the smoke validates execution through the model/bridge/readout path, but does not validate usable answer transfer. The synthetic smoke label substitution is explicitly marked in the artifacts. Full details are in [`gpu_smoke_modal/SMOKE_REPORT.md`](gpu_smoke_modal/SMOKE_REPORT.md).

The full RQ7 qualification completed separately with 1,800 episodes and stopped: no cell passed. The best A silent accuracy was 71.7% on F3 lookup depth 1, below the 80% bar, and its format-valid rate was 78%, below 95%. B-oracle accuracy was recorded as 0% for every cell. The sealed RQ7 result is at [`../rq7_full_2026-10-04/RQ7_RESULT.json`](../rq7_full_2026-10-04/RQ7_RESULT.json), with stop reason and run details in [`../rq7_full_2026-10-04/RQ7_RUN_REPORT.md`](../rq7_full_2026-10-04/RQ7_RUN_REPORT.md). PCS7's scientific gate correctly remains closed; the RQ7 stop should be interpreted only after auditing the zero B-oracle scores and prompt/readout path.

The full CLI was pointed at the available real-model RQ7 smoke output as its `--rq7-choice`. It exited 20 with `STOP_GATE_FAILED` at `rq7_choice_verification` and the recorded reason `missing RQ7_CHOICE.json`; no model was loaded. The check is reproducible with:

```sh
/tmp/pcs-l2l4-cpu-env/bin/python scripts/pcs7_silent.py --out-dir evidence/pcs7_build_2026-10-04/rq7_smoke_fail_closed --rq7-choice evidence/rq7_gpu_smoke_2026-10-04/real-model-gpu-smoke
```

## Launch commands prepared; not run

Local synthetic CPU check:

```sh
/tmp/pcs-l2l4-cpu-env/bin/python scripts/pcs7_silent.py --smoke-only --out-dir /tmp/pcs7-cpu-smoke
```

Optional real-model PCS7 smoke, synthetic tasks, 600-second cap:

```sh
PATH="/tmp/pcs-l2l4-cpu-env/bin:$PATH" MODAL_PROFILE=modal-account-B modal run --detach scripts/modal_pcs7_silent.py --mode gpu-smoke
```

Scientific run after a passing full RQ7 choice is available and review allows launch:

```sh
MODAL_PROFILE=modal-account-B modal run --detach scripts/modal_pcs7_silent.py --mode full --rq7-choice /artifacts/rq7-qualification-<sha12>/full/RQ7_CHOICE.json
```

## Open gate

The current RQ7 output is a completed full qualification with `STOP_NO_CELL_PASSES`; it is not a passing choice bundle. PCS7 scientific execution remains blocked at its required input gate. The bounded PCS7 smoke is integration evidence only, and no PCS7 full scientific job was launched.
