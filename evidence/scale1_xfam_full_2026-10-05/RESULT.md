# SCALE1 X-FAM (Qwen3-4B → Phi-4-mini-instruct): sealed and audited (Claude), 2026-10-05

Run `fc-01M452TE6Z0CYDRQ6YG3AD09XQ`, modal-account-B, L4, runner sha `4223501c…`. PCS2b protocol (10 epochs, PCS2b default), seed 20261013. Phi revision `cfbefacb…`. Exit 0. Classification: **SCALE1_XFAM_NOT_POSITIVE**.

Gates pass:
- source parse 100%, objective 95%;
- receiver oracle 100%;
- readback 98%.

| | PCS | mean wrong | restart | zero/random | text handoff | oracle |
|---|---|---|---|---|---|---|
| all m | 19.0% | 8.9% | 10.9% | 9% | 98.4% | 100% |
| **train m** | **42.4%** | 6.5% | 12.2% | 10% | 99.4% | 100% |
| held-out m | 0.3% | 10.8% | 9.8% | 8% | 97.6% | 99.9% |

- State-specific fidelity, overall: **+10.1 pts, CI [8.5, 11.8]**; McNemar p < 1e-30 against each partner.
- Readback (B states A's value) is 98%. The cross-family receiver *does* receive A's specific value.
- Source-mistake excess: +4.3 (13 states, small).

**Criteria failed:**
- PCS future fidelity ≥ 50;
- beats restart by 20;
- held-out-m specificity;
- zero/random don't explain;
- beats fair text handoff.

## Audit
1. **The cross-family hop carries A's specific state.** Readback is 98%, and on trained update values PCS beats wrong states by +36 pts.
2. **What fails is use of the state on new updates.** On held-out m, fidelity collapses to 0.3%, below chance: the bridge learned m-specific shortcuts instead of a reusable value.
3. Training looks **under-converged at 10 epochs**: val loss was still about 1.0 and noisy. PCS3b needed 40 epochs.
4. **Cost:** measured 0.93 L4 GPU-hours, about $0.74 at an assumed $0.80/h (generation 43%, training 29%, eval 24%).

## Allowed claim
"A source model's private value can be read back by a receiver from a different model family (98%), and used on trained update values (+36 pts over wrong states). Generalisation to new updates fails at the PCS2b training budget."

The full cross-family PCS claim is **not** made.

**Exploratory follow-up (proposed, not pre-registered):** a 40-epoch rerun, labelled a training-budget deviation as with PCS3b.
