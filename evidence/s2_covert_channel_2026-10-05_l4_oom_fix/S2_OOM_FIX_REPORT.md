# S2 L4 OOM Fix Report

**Date:** 2026-10-05  
**Purpose:** bounded real-model smoke after the full-scale L4 out-of-memory failure. This is pipeline evidence only, not a scientific result or approval for a full rerun.

## Diagnosis and mitigation

The recorded full-scale run `s2-covert-channel-f9cfa01df2a0` failed while fitting capacity 1. The preserved [`run.log`](prior_failure/s2-covert-channel-f9cfa01df2a0/run.log) reports a failed 1.79 GiB allocation with 973.94 MiB free on the 22.03 GiB GPU; PyTorch held 18.79 GiB allocated and 2.05 GiB reserved but unallocated.

The preferred source-model mitigation was already satisfied: S2 loads sealed PCS2b source features from cache and does not instantiate or keep source model A resident on the GPU. The receiver model B is the only large model resident for S2's receiver queries. The code and protocol record `source_model_gpu_resident: false`.

I reduced the configured attack-training batch from 32 to 8, detector batch from 64 to 16, and receiver evaluation batch from 8 to 4. Model revisions, cached feature and bridge hashes, data and split sizes, payload schedule, seeds, capacities, objectives, epochs, and sealed evaluation are unchanged. L40S was not needed.

## Bounded L4 smoke

- Modal call: `fc-01M44QZ16GY18M2JHCH3REN4ZS`
- Profile: `modal-account-B`
- Runner SHA-256: `c1fa937bd8157ee6d9d0860f40a748c09d7293713e1e7ef32ad9afeb37b29dfb`
- Output: `pcs-core-artifacts:s2-covert-channel-c1fa937bd815-gpu-smoke/`
- Result: exit code 0, `S2_GPU_SMOKE_OK`; completed under the 600-second function timeout. Exact records are in [`gpu_smoke/`](gpu_smoke/s2-covert-channel-c1fa937bd815-gpu-smoke/).
- The real-model smoke exercised the full configured training batch of 8 at capacity 1, one attack backward step, and three receiver calls including an evaluation query of shape `[4, 10]`.
- Recorded peak GPU allocation: 8,131,063,296 bytes (7.57 GiB); peak reserved: 8,992,587,776 bytes (8.37 GiB).
- The smoke confirms the reduced full batch fits and the frozen B receiver can be queried. It does not establish that the complete training and evaluation workload will finish without OOM.

## Unit checks

`tests/test_s2_covert_channel.py`: 17 passed.  
The updated synthetic CPU smoke printed `S2_SMOKE_OK`; its outputs are in [`cpu_smoke/`](cpu_smoke/).  
Python compilation of the S2 runner and Modal launcher passed; `git diff --check` passed.

No full S2 run was started.
