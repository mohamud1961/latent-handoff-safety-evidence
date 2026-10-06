# Build questions and protocol blockers

These items are absent from the frozen experiment documents and affect the
measurement. The implementation must not silently choose them before a run.

## W1 Part A train/validation scope (implementation clarification, resolved)

The W1 freeze names the enlarged-pool extras in its data list, then explicitly
limits the sweep to train and validation and says the PCS3/PCS3b test pool is
not touched. The enlarged-pool feature file contains test-only extras, so the
W1 implementation does not mount or load it. It builds train+validation caches
from the pinned multiposition feature artifact, and evaluates validation via an
isolated val-only cache temporarily relabeled `test` for the unchanged PCS3
evaluator. No threshold, split, or gate was changed; this interpretation leaves
no W1 protocol question open.

## S2 covert channel

`07_S2_COVERT_CHANNEL_FREEZE.md` defines the attack and pass criteria, but does
not freeze the following operational values:

1. **Artifact custody.** The PCS2b bridge path and SHA are recorded in
   `REVIEW_MON2_OPUS.md` and the sealed PCS2b manifest. The cache SHA is pinned
   by the manifest, but the exact Modal volume path for the source cache and
   read access to both files from profile `modal-account-B` still need explicit
   confirmation. The protocol must provide both exact paths and hashes and
   confirm the selected profile can read them. Do not infer the cache path
   from the bridge's directory name.
2. **Encoder norm budget.** Specify the numeric budget and whether it is
   absolute L2 or relative to clean-prefix RMS, including the norm's coordinate
   units and whether it is enforced per example or over a batch. The code
   scaffold supports only `absolute_l2` and `relative_prefix_rms`, each with
   `per_example` or `batch` scope; those supported choices are not approvals.
3. **Validation beta search and task-fidelity aggregation.** Freeze the
   explicit beta candidates and no-feasible-candidate policy. Define how
   future/readback task fidelity is aggregated on validation, and whether beta
   is fit separately per capacity and arm or shared across arms. Select the
   smallest feasible beta using validation only, as required by the freeze.
4. **Four-bit quantization.** The freeze pins four bits but not calibration or
   clipping. The scaffold currently supports coordinate-wise min/max ranges
   fitted on clean training prefixes and clipping to those ranges. Confirm
   those choices or specify an alternative before resolving the protocol.
5. **Payload schedule and samples.** The sealed PCS2b splits pin 512/128/256
   train/validation/test states. Choose the payload RNG seed and the within-
   split bit-balance/sampling rule; confirm payload assignments are
   independent across splits and preserve state-level clustering for
   uncertainty estimates. The scaffold's exact per-bit balance is a candidate
   only, not a frozen choice.
6. **Attack model and optimization.** The freeze specifies a linear encoder, an
   MLP decoder and the BCE-plus-beta-KL objective, but not encoder/decoder
   learning rates, optimizer, weight decay, epochs, batch size, decoder width
   and activation, gradient clipping, initialization seeds, loss reductions,
   or checkpoint/early-stopping rule. It also does not choose the query
   aggregation for the KL/fidelity objective. The scaffold implements one
   hidden GELU decoder and particular reductions; these require explicit
   confirmation or code changes and must not be treated as approved defaults.
7. **D-noise randomness and bootstrap seed.** The freeze pins Gaussian noise
   at `sigma = 0.1 × clean prefix RMS`; the roadmap fixes state-cluster
   bootstrap at 10,000 resamples. The noise draw/repetition policy and seed,
   plus the bootstrap resampling seed (or its derivation), remain unspecified.
   Resolve these so arms are comparable and intervals reproducible. The
   scaffold's `SMOKE_SEED` is only for synthetic checks, not an approved
   experiment seed.
8. **Detection monitor.** Choose the classifier family, architecture and
   optimization/checkpoint rule, plus the clean-versus-payload sample balance
   and how training/validation/test examples are formed for each capacity and
   defense arm. The scaffold currently supports a binary MLP selected by
   minimum validation BCE; this is not an approved selection.
9. **Adaptive attacker protocol.** The freeze requires retraining E and D with
   D-PCA in the loop. Resolve whether beta and training checkpoints are fit
   separately for each capacity/arm and confirm D-PCA is fit only on clean
   training prefixes, before any adaptive training or test evaluation.

The current S2 runner contains math/metric helpers and a synthetic-only CPU
smoke, not an end-to-end PCS2b extraction/training/evaluation implementation.
Its scientific CLI exits before model construction even if protocol/input
preflight passes. The Modal scaffold has `S2_EXECUTOR_READY = False` and must
not spawn. Do not enable either gate until the questions above are answered,
the full executor is implemented and reviewed, and the exact pinned assets are
available. Unit tests and synthetic CPU checks are permitted meanwhile.

The protocol validator requires explicit values for custody, norm budget, beta
search, quantization, payload schedule, attack training and detector selection.
It also constrains some fields to the current scaffold's supported
implementation (including clean-train min/max quantization, exact per-bit
balance, a one-hidden-GELU decoder and specified BCE/KL reductions). These
constraints are not scientific resolutions; revise the implementation if the
reviewed protocol selects another method. Tests use a clearly test-only
protocol fixture and do not resolve the experiment.

The PCS2b prompts/bridge hash, capacities `k ∈ {1,4,16}`, D-PCA 99% variance
bar, D-noise scale and pass criteria remain fixed by
`07_S2_COVERT_CHANNEL_FREEZE.md`.

## PCS3c confirmatory 3-value transfer

`01_W1_PCS3C_FREEZE.md` fixes the confirmatory thresholds, generation seed
`20261005`, four multiposition semantics, W1-selected bridge config, evaluation
arms, positive criteria, and the 450-state post-gate test floor. The present
build implements only pure decision/metric helpers and a synthetic smoke;
`scripts/pcs3c_confirm.py` exits blocked and has no model executor or Modal
launcher. Do not score PCS3c or treat synthetic outputs as experiment results
until these items are resolved and reviewed:

1. **W1 choice custody.** W1 has to produce `W1_CHOICE.json` first. Pin its
   exact path and file SHA-256 for PCS3c. The validator checks the W1 schema,
   seal, eight arm scores/checkpoints, pinned canonical runner, and mechanical
   config choice, but no sealed W1 choice is currently present in this build.
2. **Fresh pool and split.** Part B says the pool should retain at least 450
   test states after gates and suggests 1,600. The older PCS3 neural freeze
   uses 512/128/256 train/val/test, while the earlier canonical runner uses
   different pool defaults. Pin the exact fresh pool size, train/val/test
   allocations, generated-record order, eligible-row selection, and exact
   gate/split/seal order. Keep test labels sealed until evaluation.
3. **Generator and source prompt identity.** Seed `20261005` is fixed, but the
   fresh-run RNG namespace and generator bytes are not pinned. Older PCS3
   freeze text gives a `Final:` marker; the pinned runner uses `Final state:`.
   Pin the exact generator/code SHA, source prompt bytes/hash, and parser/output
   grammar for the fresh run instead of inferring them from prose or defaults.
4. **Receiver gate interpretation.** PCS3c says exact-A-state oracle >=90%.
   The PCS3 transfer freeze applies >=90% overall, while the supervised PCS3
   freeze and pinned runner additionally require >=85% for each selector. Pick
   and review the governing interpretation; the helper requires an explicit
   policy and the scientific preflight currently supplies none.
5. **Checkpoint token mapping.** The multiposition amendment names the last
   assignment-line token for each register plus the original checkpoint, but
   does not approve the character-offset/token-boundary mapping from saved
   greedy IDs into teacher-forced `prompt + trace`. Pin that mapping and its
   checkpoint-rate numerator/denominator.
6. **Model and tokenizer custody.** The source/receiver names are Qwen/Qwen3-4B
   and Qwen/Qwen3-1.7B, but immutable model and tokenizer revisions or local
   artifact hashes are absent.
7. **Evaluation prompt/control commitment.** Pin exact receiver prompts and
   chat-template bytes for restart, partial, text-oracle, private-trace, and
   selector evaluation; the tie rule when selecting among multiple strong
   wrong states; the probe-seed commitment; and the bootstrap seed. The build
   spec requires the bridge checkpoint SHA and probe commitment sealed before
   evaluation probes are constructed.
8. **Executor/review gate.** After the protocol is resolved, implement and
   review the complete generation, multi-position capture, source/receiver
   gates, chosen bridge training, sealed one-pass evaluation, raw records,
   exact McNemar, 10,000-resample state-cluster summary, and artifact custody.
   The current CLI cannot execute that path and must remain blocked.

## S4-dev selective filter

03_S4_SELECTIVE_FILTER_FREEZE.md fixes the target, filters, split use, metrics
and F-LEACE pass bars. The scientific runner refuses to start until these
custody and secondary-method choices are resolved:

1. **PCS3b neural checkpoint custody.** The checked-in PCS3 multiposition
   manifest pins the feature files but does not contain the PCS3b neural
   PCS3_BRIDGE.pt path or SHA-256. Provide the exact bridge path on
   pcs-core-artifacts and its SHA-256. Also confirm the L4 profile
   modal-account-B can read that artifact volume: the feature manifest names
   profile modal-account-A, while the S4 build table names modal-account-B.
   The runner already pins the main and enlarged-test feature SHA-256 values
   from evidence/pcs3_multipos_2026-10-04/MANIFEST.json.
2. **F-train architecture and optimization.** The freeze says “small MLP” and
   adversarial c-probe at chance, but supplies no mapper/adversary hidden
   widths, learning rates, weight decay, epoch budget, batch size, adversary
   updates per batch, task/adversary loss weights or gradient-reversal scale.
   Provide those values and confirm the implemented mapper has one hidden GELU
   layer and directly maps C to C′. State the validation checkpoint rule; the
   runner's candidate is minimum
   task_loss_weight × retained-selector CE − adversary_loss_weight × c-probe
   CE, selected on validation only.
3. **F-train “chance” interpretation.** Confirm that 10% is the c-probe chance
   benchmark, and choose whether c-probe scoring uses class-balanced or
   ordinary accuracy if A's c-belief counts are uneven. The runner reports
   both ordinary and observed-class balanced accuracy, but requires the choice
   governing the 10% chance comparison and linear-probe gate.
4. **Reported MLP c-probe.** The freeze requests an MLP probe result but does
   not specify its hidden width, optimizer values, epoch budget, batch size or
   validation checkpoint rule. The implementation supports a one-hidden-layer
   GELU classifier selected by minimum validation cross-entropy; provide the
   remaining values.

Record the answers in a reviewed protocol JSON with schema
s4_dev_protocol_v1, status resolved, the bridge custody values, F-train values
and MLP-probe values. Until that JSON is complete and the bridge SHA is pinned
in the runner, S4-dev may run only the synthetic CPU smoke and unit tests; the
Modal launcher must not spawn a job.

The protocol JSON must include these runner keys:

- asset_custody: pcs3b_neural_bridge_sha256,
  pcs3b_neural_bridge_volume_path, volume_artifact_profile, modal_profile and
  cross_profile_access_verified=true.
- c_probe_chance_accuracy: explicitly confirmed as 0.1;
  c_probe_accuracy_metric: ordinary_accuracy or balanced_accuracy.
- f_train: hidden_dim, epochs, batch_size, learning_rate,
  adversary_learning_rate, weight_decay, task_loss_weight,
  adversary_loss_weight, gradient_reversal_scale, adversary_hidden_dim,
  adversary_updates_per_batch and validation_selection.
- mlp_probe: hidden_dim, epochs, batch_size, learning_rate, weight_decay and
  validation_selection.

## RQ6 qualification (PCS6 reasoning continuation)

The local RQ6 helper implements deterministic parsing/scoring only. The frozen
RQ6 cannot be run until these protocol conflicts are resolved in a reviewed
amendment. Do not load models or launch a job while any of these remain open.

1. **Source prompt/parser incompatibility.** `04_PCS6_REASONING_CONTINUATION_FREEZE.md`
   requires A to write `s_k: a=... b=... c=...` through step 11 and end with
   `FINAL: ...`, then says to parse with PCS4v2 amendment 1. The PCS4v2 prompt
   and parser instead require `STATE s0` through `STATE s8` and
   `FINAL_SUMMARY:`; the prompt is also for depth 8. Supply the exact RQ6 A
   prompt and approved parser amendment without changing the scientific gate.
2. **Episode construction.** The pool is 1,600 episodes and the split seed is
   20261006, but the generation seed, RNG namespace, exact PCS3/PCS4v2
   generator variant, record ordering, and eligible-record selection rule are
   not fixed. Pin these values and identify how the M=2 retry reuses or
   regenerates episodes.
3. **Split/gate ordering.** The split is said to happen “after gates,” but the
   source decodability gate needs train/val and the mistake gate requires at
   least 15 A-wrong episodes in test. The exact test count and seeded split
   algorithm are absent, so the test-specific gate cannot be checked before
   the split. Specify the gate order, exact allocation, and selection rule;
   keep test outcomes sealed until the prescribed evaluation point.
   The 75% final-triple gate also does not say whether unparsed A traces count
   as incorrect or are omitted from the denominator.
4. **Checkpoint positions.** 6A-W requests end-s7, end-s8, and “the
   checkpoint,” while the checkpoint itself is immediately after the s8
   newline, duplicating end-s8. Resolve the third position. Also define the
   tokenizer-boundary rule and the checkpoint-location numerator/denominator
   for both W and U. 6A-U must stop after the s8 prefix and before every s8
   value token; a character offset is not a token-position rule.
5. **Partial text and B inputs.** Freeze the candidate partial-text content,
   validation selection metric and tie rule. Expand the abbreviated
   oracle-state example and pin exact restart, partial-text, and chat-template
   formatting. Specify how M=2 changes the B instruction while preserving the
   registered retry.
6. **Linear source probes.** “Linear probe” does not specify solver,
   standardization, regularization candidates/selection, concatenated feature
   order, or the validation score used for selection. Freeze these details
   for W and U without using test labels.
7. **RQ6-B natural reasoning.** Pin GSM8K dataset revision/hash and test
   sampling, A/B prompts, numeric-answer normalization, sentence segmentation,
   model-token counting and tie rules for the 50% checkpoint, and the matched
   wrong-prefix similarity tolerance/selection tie rule. The later “about
   3,000” train examples also need an exact selection rule. No answer
   canonicalization is implemented as an experiment default.
8. **Model custody.** Pin immutable Qwen3-4B/Qwen3-1.7B model and tokenizer
   revisions or local artifact hashes. The current freeze names model IDs but
   no immutable revisions, and this build is explicitly offline.

`scripts/rq6_qualification.py` has a no-model preflight, pure-Python strict
triple/answer-line parsers, frozen-threshold scoring helpers, and a synthetic
CPU smoke. These helpers are engineering-only and do not resolve the above
questions. There is no RQ6 Modal launcher; the default CLI exits nonzero before
any model import or load until the protocol is amended and reviewed.

## PCS6 bridge readiness and scoring

The PCS6-A/B build provides pure-Python scoring helpers and synthetic CPU
checks only. Both scientific preflights remain blocked by the RQ6 protocol
items above, missing qualified gate artifacts, and the absence of a PCS6
executor. The helper interfaces do not create prompts, models, checkpoints,
datasets, splits, or partner assignments.

1. **Reviewed RQ6 gate artifact and W1 custody.** The PCS6 freeze does not
   define the serialized RQ6 pass-gate schema or its reviewer/custody record.
   The helper currently recognizes an engineering wrapper named
   `rq6_gate_result_v1` with `status: passed` and track-specific booleans;
   this wrapper is not a scientific protocol decision. Before execution,
   review the artifact schema, pin its exact path and SHA-256 in a resolved
   `pcs6_protocol_v1`, and likewise pin/validate the sealed `W1_CHOICE.json`
   path and SHA-256. No qualified RQ6 gate or W1 choice is present in this
   build.
2. **D1 outcome review.** The D1 helper selects D1-a only from a reviewed
   PCS4v3/v4 L3 result whose evidence hash is recorded; otherwise it returns
   the frozen D1-b fallback (information-weighted plus readback at λ=0.25).
   The PCS4v4 synthetic reducer smoke is not qualifying review evidence. Pin
   the reviewed L3 result records and the exact derived decision in the PCS6
   protocol before training.
3. **6A partner propagation and comparison records.** The swap scorer accepts
   explicit operation records for steps 9–11 and explicit partner IDs; it
   does not implement a program generator or select matched wrong partners.
   Freeze and review the partner-selection rule and the raw operation/record
   schema before a scientific run. The helper's specificity estimator uses
   episode-level PCS-minus-mean-wrong effects over rows with at least one
   supplied partner; its bootstrap point and interval use that same matched
   subset.
4. **6B answer and checkpoint protocol.** Exact answer-string comparison is
   provided only as a pure helper; no numeric normalization is applied. The
   RQ6-B freeze still needs the GSM8K revision/sampling rule, prompt bytes,
   sentence segmentation and model-token checkpoint mapping, answer
   normalization, and similar-fraction wrong-prefix matching/tie rule listed
   above. The exploratory PCS-vs-wrong metrics consume explicit partner
   records and do not select them.
5. **Executor/review gate.** `scripts/pcs6a_continuation.py` and
   `scripts/pcs6b_gsm8k.py` do not train bridges or execute model inference.
   The CLI preflights always exit nonzero before model imports while RQ6 is
   blocked. Implement and independently review complete train/evaluation
   executors only after the protocol and artifact custody above are resolved.

## MON2 interpretation and firewall protocol (before full run)

The MON2 implementation follows the requested paired design and the three
review fixes, but the freeze leaves these analysis details open. The current
firewall aggregation below is an explicit candidate, not a frozen choice.

1. **Public-input baseline for COMP versus REJ.** Task 2 contains injected
   rows only, and public programs vary across rows. M-PUBLIC is reported for
   COMP versus REJ, but the freeze only requires its near-chance check for
   Task 1. Confirm whether Task 2 must also compare M-PCS against M-PUBLIC
   (and what criterion applies), or narrow the claim so public susceptibility
   prediction is not mistaken for reading A's compromised cognition.
2. **Shuffled-control tolerance.** The freeze says the shuffled-label AUROC
   should be approximately 0.5 but gives no numeric interval. The runner
   reports shuffled AUROC descriptively and does not include it in the
   mechanical classification. Choose a reviewed tolerance or explicitly keep
   it diagnostic before treating the classification as fully mechanical.
3. **Combined firewall score.** The runner currently calibrates and evaluates
   `p(INJ) × p(COMP | INJ)`. The freeze says to combine Tasks 1 and 2 but does
   not specify this formula. Approve it in a reviewed amendment or state the
   intended combination; do not interpret firewall outcomes as frozen until
   this is resolved.

## Model and tokenizer custody for runner-based builds

The manifests pin code, bridges and feature files, but do not pin the
underlying Qwen model/tokenizer snapshots. MON2 loads Qwen3-4B and
Qwen3-1.7B by model ID; PCS4v4 trains/evaluates its new bridge using
Qwen3-1.7B; W1 loads the Qwen3-1.7B receiver and its feature manifest does
not record the Qwen3-4B source revision. The completed MON2 smoke verifies
that these current model paths execute, but cannot establish identity with
the model snapshots that produced the frozen PCS2b bridge. Before full
scientific runs, pin immutable model and tokenizer revisions or local artifact
hashes for each arm and record source-model provenance for existing feature
artifacts. The PCS3c, RQ6 and PCS6 sections also call out their experiment-
specific model custody blockers.
