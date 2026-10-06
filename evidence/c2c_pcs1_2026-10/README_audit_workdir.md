# PCS x C2C fidelity audit

A free-GPU experiment notebook that asks one question of the Cache-to-Cache (C2C) bridge: **does it transfer the sharer's beliefs, mistakes included, or does it just make the receiver generically better?** Every latent-communication paper reports task accuracy; this measures fidelity instead. Read `PREREG.md` first: hypotheses, sample sizes, metrics and decision thresholds are fixed there before any result exists.

**Status: written and validated locally with no weights; never yet run on a GPU.** See "Validation" and "What could still break".

## What it tests

Pair: receiver `Qwen/Qwen3-0.6B`, sharer `Qwen/Qwen2.5-0.5B-Instruct`, released fuser `nics-efc/C2C_Fuser`, folder `qwen3_0.6b+qwen2.5_0.5b_Fuser/final` (28 projectors, about 956 MB). C2C code is cloned at commit `3ca0e98` (does not `pip install -e .`, because that would re-pin torch).

| Part | Purpose | Items | T4 time |
|---|---|---|---|
| A | Plumbing: receiver / sharer / C2C on OpenBookQA, paper's generation protocol and a logit readout, against the paper's Table 4 (39.2 / 45.6 / 52.6) | 200 | 5-8 min |
| B | **The experiment.** On items where sharer-alone and receiver-alone disagree, inheritance = P(C2C answer == sharer's answer), split by sharer right / sharer wrong. Controls: mismatched-sharer null, text handoff, text handoff plus the sharer's rationale | 2000 | 25-40 min |
| C | Exploratory: false premise only the sharer sees (receiver gets masked padding of equal length) | 500 | 5-10 min |

Plus about 8-12 min of installs and downloads (about 3.2 GB: 0.5B + 0.6B models and the fuser). Total about 45-75 min on a T4; the notebook estimates runtime after loading models and shrinks Part B if it would exceed `TIME_BUDGET_MIN` (90), logging that as a deviation. Greedy, seed 0, batch size 1.

## Run on Kaggle

CLI (this folder has a `.venv` with the `kaggle` CLI; credentials are not configured):

```bash
cd <local>/Downloads/pcs-c2c-audit
# 1. put your Kaggle username in kernel-metadata.json ("id": "USERNAME/pcs-c2c-fidelity")
.venv/bin/kaggle auth login            # or follow the Kaggle CLI docs for an API token
.venv/bin/kaggle kernels push -p . --accelerator NvidiaTeslaT4
.venv/bin/kaggle kernels status YOURNAME/pcs-c2c-fidelity
.venv/bin/kaggle kernels output YOURNAME/pcs-c2c-fidelity -p ./kaggle_out    # results.json lands here
```
The kernel is private, GPU on, internet on (needed for GitHub and Hugging Face). If the push rejects `machine_shape`, delete that line and pick GPU T4 in the UI. Prefer a T4: on a P100 (compute capability 6.0) recent default torch wheels may lack kernels, so the notebook detects compute capability < 7 and installs torch 2.6.0+cu124 (what C2C pins); a T4 avoids that detour.

Web upload: Kaggle > Create > New Notebook > File > Import Notebook > `c2c_fidelity.ipynb`. In Settings set Accelerator **GPU T4**, Internet **On**, Persistence off. Run All (or "Save Version" > Save & Run All for an unattended run). `results.json` appears under `/kaggle/working` (the Output tab).

## Run on Colab

Upload `c2c_fidelity.ipynb`, Runtime > Change runtime type > **T4 GPU**, Run all. `results.json` is written to the working directory (`/content`); download it from the Files panel. The free tier can disconnect; `results_partial.json` is written every 100 items, but the notebook does not auto-resume across a lost runtime, so keep the tab open.

## Where results land

- `results.json`: config, environment (GPU, dtype, versions, C2C commit), `deviations`, Part A / B / C summaries with bootstrap CIs, **per-item predictions for every condition** (`records`: letter plus the four option probabilities), Part C per-item rows.
- `results_partial.json`: periodic checkpoint of per-item records.
- The printed tables at the end of each part are the summary; the **AUTO-READING** line applies the PREREG decision table mechanically.

Headline number: Part B table, row `B` (sharer wrong, receiver right), column `EXCESS E = C2C - null`. High and positive means the receiver abandons a correct answer for the sharer's wrong one beyond what a generic cache perturbation produces: belief transfer.

## Notes on design (what C2C actually allows)

- Sharer and receiver must be **position-aligned** (equal token length): the fuser is applied per position and `RosettaModel.forward` slices both models' inputs with the same indices. They can see *different tokens* if lengths match (C2C's own aligner pads template regions and masks them). That is what makes the mismatched-sharer control (a cache from a different same-length prompt) and the planted-premise variant possible.
- The released fuser was trained only on identical inputs (OpenHermes 500k), so mismatched/planted inputs are out of distribution. The mismatched-sharer null is an upper-ish bound on "generic perturbation" for that reason; read Part C as exploratory.
- Same-tokenizer pair: both models are fed the receiver's chat-template tokens (`is_do_alignment: false`). The sharer therefore sees the Qwen3 non-thinking template, not its own. "Sharer alone" in Part B uses those exact tokens (what the fuser transmits); the sharer's own template is kept as a sensitivity condition (`S_nat`).
- C2C's repo hard-codes bf16. A T4 has no native bf16, so the notebook tries fp16, checks it against fp32 on 24 probe items, and falls back to fp32 if it disagrees or produces non-finite values. Native-bf16 GPUs (A100/H100/L4) use bf16 like the repo.

## Local validation (done, no weights downloaded)

```bash
.venv/bin/python validate_notebook.py                 # static: nbformat, byte-compile, every C2C import/keyword exists in the cloned C2C, answer-key parity
.venv-smoke/bin/python test_analysis.py               # Part B analysis on synthetic scenarios with known truth (belief carrier / truth-biased helper / non-specific)
.venv-smoke/bin/python smoke_test.py --dtype fp32     # executes the shipped notebook end to end on CPU with tiny RANDOM models (also: bf16, fp16)
```
`.venv-smoke` (torch 2.6.0 CPU, transformers 4.52.4; about 700 MB, safe to delete) exists only for these checks. The smoke run downloads tokenizers, tiny JSON configs and the three small datasets, never weights. It proves the code path runs end to end under the pinned versions in each dtype (fusion gates are forced open so the cache-fusion path is exercised); it says nothing about accuracy. Logs are in `validation_logs/`.

## What could still break on the GPU

See the report in chat; short list: fp16 numerics of the real fuser (gated and logged), transformers/torch version drift on the platform image, Hugging Face / GitHub reachability from the sandbox, and the logit readout giving a smaller C2C gain than the paper's generation readout (Part A reports both so you can see it).

## Files

| File | What |
|---|---|
| `PREREG.md` | hypotheses, controls, sample sizes, decision table (fixed before results) |
| `c2c_fidelity.ipynb` | the experiment (self-contained) |
| `kernel-metadata.json` | `kaggle kernels push` metadata (private, GPU, internet; replace `USERNAME`) |
| `validate_notebook.py` | static checks against the cloned C2C |
| `test_analysis.py` | unit test of the Part B analysis on synthetic data |
| `smoke_test.py` | CPU smoke run of the notebook with tiny random models |
| `validation_logs/` | outputs of the checks and smoke runs |
| `C2C/` | shallow clone of thu-nics/C2C at the audited commit |
| `.venv/` | venv with the `kaggle` CLI (no credentials) |
| `.venv-smoke/` | CPU torch/transformers env for the smoke test only |
