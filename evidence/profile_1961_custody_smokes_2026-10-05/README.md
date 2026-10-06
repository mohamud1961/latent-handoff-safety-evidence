# Profile move to modal-account-A: custody smokes (2026-10-05)

PCS2b assets copied from modal-account-B to the modal-account-A `pcs-core-artifacts` volume at `/pcs2b-preanswer-state-realization/` and re-downloaded to verify: `pcs2b_bridge.pt` sha256 `87de8fb8a70d62aea0a2545faeb3c5b12890832dfd24d1b64e0b4a84cea8a771`, `pcs2b_source_cache.pt` sha256 `42f419d69f5ebda6270ecbd335b2e8de72123cf757d0ebc2327c1620bd8c048f` (both match). CHAIN1 and INTERFERE1 read nothing else (the PCS2b runner is baked into the image). Qwen3-4B and Qwen3-1.7B were already in the 1961 HF cache.

Launchers (`modal_s5_c2c_security.py`, `modal_chain1.py`, `modal_interfere1.py`) now accept `MODAL_PROFILE` of modal-account-A or modal-account-B. Smokes on 1961 (L4, 600 s cap), exit 0:
| launcher | call | note |
|---|---|---|
| INTERFERE1 | `fc-01M4549BYEB5XFNP2Q952YFYZN` | 104 s; in-container custody check passed (runner, bridge, cache shas above) |
| CHAIN1 | `fc-01M4549S05350KJWCM1M3B8WMK` | 192 s; custody passed; Addendum 1 lineage probe ran |
| S5 | `fc-01M454QKQQYE6B0K0G33GNT8MY` (final, after the stability fix) | 48 s; models, fuser and OpenBookQA downloaded to the 1961 cache; official and differentiable fusion agree exactly |

S5 stability: the earlier jump was the decoder's BCE, not KL (KL stayed about 0.001). One Adam step at lr 1e-3 over 57,344 decoder inputs moved hidden pre-activations by tens. Fix (G2, recorded in `S5_PROTOCOL.json`): D lr 1e-5, E lr 1e-4 with init x0.1, clip 1.0 over E and D, KL from fp32 log-softmax, decoder input centred with a relative std floor and clamp. Smoke losses 0.697 -> 0.643 over 2 epochs. Fuser revision: `f01fc325...` is the snapshot hash in every PCS1 audit log (PROVENANCE.md), so the pin matches the PCS1 weights; the 2026-08-14 repo modification date does not change that snapshot.

CHAIN1 Addendum 1 (resolved): primary lineage probe predicts A_wrong (v_A != ground truth) from prefix2 within (v1_A, m1) strata (within-stratum AUROC, state-cluster bootstrap CI), comparator = same probe on P-only TF-IDF features; v_A and v1_A decodability kept as descriptive. Smoke AUROCs are null (only 9 A-wrong test episodes); the statistics are exercised by the CPU synthetic test.
INTERFERE1: 256 test states recorded in the protocol values.
