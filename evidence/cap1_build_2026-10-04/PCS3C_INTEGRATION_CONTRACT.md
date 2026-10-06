# CAP1 / PCS3c handoff contract

CAP1 is a secondary analysis of the completed PCS3c run. It must not open
PCS3c data for a scientific analysis until the PCS3c confirmatory test is
complete and its final artifacts are hash-pinned. CAP1 never generates source
episodes or creates, shuffles, filters, reselects, or relabels a split.

## Required PCS3c artifacts

PCS3c must hand CAP1 four immutable artifacts through
`CAP1_PCS3C_HANDOFF.json`:

1. `source_bundle`: a `pcs3c_cap1_source_bundle_v1` Torch file with the final
   source `items` in sealed order, `features` with shape
   `[N, 4, 9, 2560]`, integer `line_digits` with shape `[N, 4]`, and each
   item's original generated `A_prefix_token_ids` up to the canonical final
   state marker.
2. `result`: a `pcs3c_confirmatory_result_v1` JSON file with the final PCS3c
   classification, `scientific_execution_complete: true`, `synthetic: false`,
   `test_episode_ids_sha256`, and all raw per-episode/per-selector records.
   Each row must pass `pcs3c_confirm.validate_evaluation_record`; its
   `A_state` and `truth_state` must exactly match the source bundle.
3. `result_seal`: a `pcs3c_result_seal_v1` JSON file with
   `status: complete`, `synthetic: false`, and SHA-256 links to the result,
   source bundle, and sealed W1 choice.
4. `w1_choice`: the original sealed W1 `W1_CHOICE.json`, validated by
   `pcs3c_confirm.validate_w1_choice` and bound to the frozen canonical PCS3
   runner hash.

The source bundle must carry this `provenance` object exactly:

```json
{
  "schema": "pcs3c_cap1_source_provenance_v1",
  "model_repo_id": "Qwen/Qwen3-4B",
  "model_revision": "1cfa9a7208912126459214e8b04321603b3df60c",
  "tokenizer_revision": "1cfa9a7208912126459214e8b04321603b3df60c",
  "canonical_runner_sha256": "20b0191e0d87bef269256aa5fb5cdb290d330d2d4c899dce9bccc193a3e8f49f",
  "multipos_capture_sha256": "7996da43f49d6053ec3317886bf2e72ecf0d95812d414d5521b627ac34ba4a22",
  "source_layers": [4, 8, 12, 16, 20, 24, 28, 32, 36],
  "position_names": ["last_assign_a", "last_assign_b", "last_assign_c", "checkpoint"]
}
```

## Split and episode identity

`CAP1_PCS3C_HANDOFF.json` must have schema `cap1_pcs3c_handoff_v1`,
`evidence_kind: pcs3c_confirmatory_science`, `synthetic: false`,
`status: complete`, and both completion flags set true:
`pcs3c_confirmatory_evaluation_complete` and
`sealed_test_evaluation_complete`.

Its `artifacts` object must contain `{path, sha256}` for all four files. The
top-level `source_bundle_sha256` must match the source artifact reference.
`split_manifest` must equal the manifest recomputed by
`cap1_capacity_ladder.split_episode_manifest(items)`: exact ordered episode
IDs, their canonical JSON SHA-256, and the train, val, and test ID lists and
hashes in source order. CAP1 requires every split to be nonempty and the sealed
test split to contain at least 450 episodes. The PCS3c result must contain
exactly one validated row for every sealed test episode and selector, and its
`test_episode_ids_sha256` must match the ordered test ID list.

CAP1 independently verifies that its raw rows contain exactly one record for
every sealed test episode and selector. For each selector row, every available
wrong partner must be a distinct sealed test episode, match the other two
registers exactly, and differ on the selected register. CAP1 retains all
sealed test rows. If a row has fewer than three matched controls, results and
gates report the exact full, partial, and zero-control counts; specificity
uses that row's available controls and the run status carries a control
coverage limitation. The fidelity and primary contrast still use every
sealed test row.

The completion JSON itself is passed with an expected SHA-256. CAP1 validates
that hash before opening any referenced data file or loading either model.
Every referenced artifact hash, the result-seal links, the W1 seal/choice rule,
local frozen code hashes, source model provenance, item ID order, and split
manifest are checked before a scientific run can continue.

## FULLSEQ capture after PCS3c

The current PCS3c multiposition artifact has no per-token activations and does
not preserve generated token IDs. PCS3c must retain each original generated
`ids[:marker_index]` vector as `A_prefix_token_ids` before its canonical runner
drops the temporary `_prefix_ids` field, then include that vector inside the
hash-pinned source bundle. After the completion certificate passes,
`cap1_fullseq_capture.py` uses only the cached, pinned Qwen3-4B tokenizer/model
to reconstruct the canonical user prompt, decode the saved original trace IDs,
verify `A_private_trace` by exact decode round trip, and require prompt-plus-
trace length to equal the sealed `checkpoint_tokens` value. Missing IDs, a
round-trip mismatch, or a token-count mismatch aborts capture. It performs no
text generation and does not touch split assignments.

The capture writes source token IDs and hidden states at indices 16 and 28 for
the suffix of private-work tokens nearest the checkpoint, capped at 256. Its
`cap1_fullseq_capture_v1` file repeats the completion/source-bundle hashes,
exact ordered IDs and split manifest, layer IDs, truncation rule, checkpoint
count hash, tensor hashes, and G1 source model/tokenizer revisions. CAP1 checks
all these fields against the completion handoff before the receiver model is
loaded. Its output file SHA-256, returned by the capture job, is also required
as an explicit input to the scientific runner and checked before the receiver
model is loaded.

## Remaining PCS3c integration

The current PCS3c work is preflight-blocked and has no confirmatory executor,
raw result seal, or completion handoff. Its future executor must preserve the
original per-episode prefix token IDs and export the four artifacts above after
its one confirmatory run. CAP1 then captures the token activations as a separate
post-completion job.
