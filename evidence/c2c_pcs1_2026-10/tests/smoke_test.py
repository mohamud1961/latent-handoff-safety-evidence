#!/usr/bin/env python3
"""CPU smoke test of the *shipped* notebook: executes its code cells in order with tiny RANDOM models and random
projectors (PCS_SMOKE=1). Downloads only tokenizers, small JSON configs and the three small datasets; no weights.
It proves the code path runs end to end; the numbers it prints are meaningless.

  .venv-smoke/bin/python smoke_test.py [--dtype fp32|bf16|fp16] [--out DIR]

Needs torch==2.6.0, transformers==4.52.4, tokenizers==0.21.4, huggingface_hub==0.34.3, datasets, numpy, pandas, nbformat.
"""
import argparse, os, sys
from pathlib import Path
import nbformat

ap = argparse.ArgumentParser()
ap.add_argument("--dtype", default="fp32", help="fp32|bf16|fp16, or auto to exercise the fp16-vs-fp32 sanity gate")
ap.add_argument("--out", default=str(Path(__file__).parent / "smoke_out"))
ap.add_argument("--notebook", default=str(Path(__file__).parent / "c2c_fidelity.ipynb"))
a = ap.parse_args()
os.environ.update(PCS_SMOKE="1", PCS_DTYPE=a.dtype, PCS_OUT=a.out)
if a.dtype == "auto":
    os.environ["PCS_SMOKE_GATE"] = "1"
os.environ.setdefault("PCS_C2C_DIR", str(Path(__file__).parent / "C2C"))
Path(a.out).mkdir(parents=True, exist_ok=True)
nb = nbformat.read(a.notebook, as_version=4)
src = "\n\n".join(c.source for c in nb.cells if c.cell_type == "code")
exec(compile(src, a.notebook, "exec"), {"__name__": "__main__"})
