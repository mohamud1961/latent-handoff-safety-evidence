# 12: SCALE1, larger and cross-family pilot of the PCS2b result: FREEZE

**Claude (Opus), designer, 2026-10-05.** This is a funding-critical pilot.

## Purpose
Show that the PCS2b result (A's private scalar belief, mistakes included, transfers through a learned latent bridge to a frozen B) is not specific to Qwen3-4B → Qwen3-1.7B. The pilot covers:
- **a larger source**;
- **a receiver from a different model family**.

It also measures the real cost of the scaled step, for the grant budget.

## Arms (each a full PCS2b replication)
| Arm | A (source) | B (receiver) | GPU |
|---|---|---|---|
| **S-UP** | Qwen/Qwen3-8B | Qwen/Qwen3-4B | L40S 48 GB (A100-40GB fallback) |
| **X-FAM** | Qwen/Qwen3-4B | microsoft/Phi-4-mini-instruct (ungated, MIT) | L4, 24 GiB, raised to 32 if needed |

Revisions are pinned at build time (HF `main` sha recorded in CODE_SHAS.json before any run). B's chat template is its own.

## Protocol
**Exactly the PCS2b pre-answer protocol and runner:**
- task generator, depth-8 mod-10 chain, prompts, checkpoint immediately before the answer token;
- 4 prefix slots, bridge architecture, objective (future loss plus readback λ = 0.25), epochs, splits, controls (≥ 3 matched wrong, zero, random, restart, text oracle, fair text handoff, token-identity ceiling) and statistics.

Only the model ids and the capture layer list change:
- Capture layers: every 4th layer starting at layer 4, through the last layer.
- Bridge in/out dims follow the models' hidden sizes.

Fresh data, seed 20261013.

## Gates (per arm; as PCS2b)
- A competence and parse rate.
- Receiver explicit-state usability (oracle).
- Source decodability.

If a gate fails, that arm stops and the failure is reported. A Phi receiver-format failure is a finding about cross-family receivers, not a reason to change prompts after the fact. **One pre-registered prompt variant is allowed for X-FAM only:** use Phi's own system-message convention for the instruction. The choice is made on the receiver gate (val only) before any bridge training.

## Criteria (per arm; PCS2b's frozen criteria verbatim)
- **Fidelity** to A's belief.
- **Δ_specific** = correct − mean matched wrong, with state-cluster bootstrap CI > 0 and exact McNemar.
- **Source-mistake fidelity:** follows A's mistakes above wrong states.
- **Beats** restart and the fair text handoff.

**Claims:**
- S-UP passes: "the effect holds with a 2× larger source and receiver".
- X-FAM passes: "cognitive state transfers across model families".

## Cost reporting (required)
GPU-hours and $ per stage (generation, capture, training, eval) per arm. These feed the grant's compute budget directly.

## Compute
About 2–3 h L40S plus about 2 h L4 ≈ $8–12. Profile: whichever has more budget remaining. Requires a ≤ 10-min GPU smoke first.
