# RQ7 full qualification run report

## Run identity

- Modal call: `fc-01M44H5YA7EA5Q6B17BYZ1NAM7`
- Modal app: `ap-u5nipPIVsUPrhSQAh5uw5c`
- Profile: `modal-account-B`
- Executor SHA-256: `502ffc8155f5a0ad00803a7aca974f9842ec55e99cd1ce1fc68d9c9ae746d570`
- Remote output: `pcs-core-artifacts:/artifacts/rq7-qualification-502ffc8155f5/full/`
- Six cells × 300 episodes; elapsed model-run time 586.55 seconds.
- The stop exit code was 21 (`STOP_NO_CELL_PASSES`). No `RQ7_CHOICE.json` was produced.
- Downloaded raw-record SHA-256 matches the result manifest: `43de3d8959d3768b488efeb044bda913b0597e6ec7d44fa4856afa834321d4fb`.

## Frozen qualification outcome

No cell passed all frozen gates. The highest source accuracy was F3 lookup depth 1: 215/300 correct (71.7%) and 234/300 strict answer-only outputs (78.0%). Both are below the frozen requirements of 80% accuracy and 95% format validity. Other cells had still lower strict source performance. B-oracle accuracy was 0/300 in every cell.

In the raw records, every valid A answer did receive a B-oracle request, but none of the oracle outputs parsed as an integer under the four-token readout. Examples begin with prose such as `"Let's go through"` or `"We are given the"`. Thus the B-oracle score is a recorded zero under the frozen parser/readout, not evidence that the transferred answer itself failed to help B once read. The protocol's stop remains binding for PCS7, but this output-format behavior limits the scientific interpretation: it does not by itself establish that the models' silent computation is too shallow.

## Cell summary

| Cell | A strict outputs | A correct | A accuracy | B-oracle accuracy | Pass |
|---|---:|---:|---:|---:|---|
| F1 add, depth 1 | 1/300 | 0/300 | 0.0% | 0.0% | No |
| F1 add, depth 2 | 0/300 | 0/300 | 0.0% | 0.0% | No |
| F2 add mod 100 | 84/300 | 46/300 | 15.3% | 0.0% | No |
| F2 multiply mod 100 | 0/300 | 0/300 | 0.0% | 0.0% | No |
| F3 lookup, depth 1 | 234/300 | 215/300 | 71.7% | 0.0% | No |
| F3 lookup, depth 2 | 0/300 | 0/300 | 0.0% | 0.0% | No |

## Retained artifacts

- `RQ7_RESULT.json`, `RQ7_GATE.json`, and `RQ7_STOP.json` contain the scored result and explicit stop.
- `RQ7_RAW.jsonl` contains all 1,800 per-episode outputs and prompts.
- `RQ7_PROTOCOL.json` and `CODE_SHAS.json` retain the frozen protocol and code/model pins.
- `EXIT_CODE.txt` records the runner's expected stop code.

PCS7 verifies a sealed, passing full RQ7 choice bundle before scientific execution. Since RQ7 stopped and produced no choice bundle, the PCS7 scientific run was not launched.
