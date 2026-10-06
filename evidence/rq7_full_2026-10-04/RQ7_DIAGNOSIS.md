# RQ7 full-run diagnosis (STOP_NO_CELL_PASSES)

Source: `RQ7_RAW.jsonl` (1,800 records), `scripts/rq7_qualification.py` at SHA `502ffc81...`, freeze `design_L2_L4/09_PCS7_SILENT_COGNITION_FREEZE.md`.
Models: A = Qwen3-4B, B = Qwen3-1.7B, both `enable_thinking=False`, greedy, fp16.

## Verdict

**There is no harness bug in the parser, the chat template, the think-block handling or the EOS/`<|im_end|>` handling.** The runner implements the freeze exactly (A: "Answer with only the number.", strict full-match parser, cap 8; B readout: greedy, at most 4 tokens, integer parse). The zero B-oracle accuracy and the low A format validity are genuine instruction-following behaviour of the two models under the frozen prompts. The one real defect is a **freeze design flaw** (the readout contract assumes the model emits a bare integer first), which cannot be fixed as a "bug fix" without amending the protocol. That is Opus's call.

## What B actually output

- B-oracle was issued only for A-valid episodes: 319 of 1,800. Every one of the 319 failed the parser (`not_integer_only`). **0/319 even begin with a digit.**
- Output is always the start of prose or chain-of-thought, cut by the 4-token cap:
  - F2 add (84 of 84): `'We are given:\n\n'` (tokens `[1654, 525, 2661, 1447]`)
  - F3 depth 1 (234): `'We are given the'` (the oracle `v` is ignored; e.g. A=`'6'`, `'7'`, `'1'`, `'2'` all give the same text)
  - F1 depth 1 (1): `"Let's go through"`
- B-restart (no oracle), all 1,800: `"Let's track the"` (600), `"We are given a"` (374), `"We are given:\n"` (305), `"Let's solve th"` (263), `"We are given t"` (226), `"First, compute"` (32). 0 valid.
- There is no empty or visible think block in any output. The only special-token check: no `<think>`, `</think>`, `<|im_end|>` or other special-token spelling appears in any text of any arm. `enable_thinking=False` appends the empty `<think>\n\n</think>\n\n` to the generation prompt, so the model starts directly in the answer channel. It then starts reasoning aloud in prose. No `<|im_end|>` is ever hit before the cap, because the first 4 tokens are prose.
- The oracle prompt gives `Intermediate result: v = 7` and still repeats the whole problem `P` plus `U`. Qwen3-1.7B treats that as a word problem to work through and ignores the final "Answer with only the number." This is the same behaviour as B-restart, so the oracle hint does not change the first tokens.

Conclusion: B was never given a chance to output the number inside the 4-token window. A larger cap (e.g. 128) would show whether the oracle helps, but that changes the freeze.

## What A output

Parse reasons across cells (A, strict): valid 1/300, 0/300, 84/300, 0/300, 234/300, 0/300 (F1d1, F1d2, F2add, F2mul, F3d1, F3d2).

- F1 add (both depths) and F3 depth 2: 100% prose openers, `'We are given the following sequence of operations'`, `'We are given:\n\n- \`a ='`, `'We are given a function \`g\`'`. Nothing numeric.
- F2 add: valid `'57'` (84); invalid are equation starts `'x = (52 + 5'` (cap hit at 8 tokens), `'First, compute the sum:  \n7'`, `'70 + 60 = '`, `'138 % 100'`, `'111'` (out of range).
- F2 multiply: all `'To compute $ x = (12'`.
- F3 depth 1: valid bare digit (234, 1 token each, so EOS is emitted correctly); the 66 invalid are `'The question asks for the value of $'` (62), `'The function g is defined as follows:\n\n'` (2), `'The digit map is given as:\n\n-'` (1), and `'6\n\nThe question asks for the value'` (1).
- Only 13 of 1,166 invalid A texts begin with a digit (12 in F2 add, 1 in F3). All 13 are number plus more text (`'70 + 60 = '`, `'6\n\nThe question asks...'`) and the freeze says any other token marks the episode invalid. A lenient "leading integer" parser would not rescue meaningful volume, and would be wrong under the freeze for e.g. `'70 + 60 = '`.
- Token-length histograms show a strict split: 1 to 3 tokens (clean number then EOS) or exactly 8 (cap). There are no near-misses from the cap (e.g. a 2-digit answer followed by a stray token).

The parser is correct and the A format failures are genuine model behaviour. A's numeric accuracy among valid answers is high where it complies: F3d1 215/234 valid are correct (91.9%); F2 add 46/84 (54.8%).

## Classification

| Item | Harness bug? | Notes |
|---|---|---|
| Strict parser rejects prose/equation prefixes | No | Matches freeze text "any other token before the number marks invalid". |
| Chat template / think block | No | `enable_thinking=False` used as frozen. Verified: no think/special tokens in outputs. |
| Readout length 4 (B) and 8 (A) | No | Frozen. Outputs start with prose, so no cap would rescue them. A clean 1 to 3 token number is accepted, so the cap is not truncating valid answers. |
| `<|im_end|>`/EOS trimming | No | Clean answers terminate in 1 to 3 tokens. |
| Instruction non-compliance by A (Qwen3-4B) | Genuine model behaviour | Sample size aside, only F3d1 and F2-add partially comply. |
| Instruction non-compliance by B (Qwen3-1.7B) | Genuine model behaviour | 0/319 oracle, 0/1800 restart start with a digit. |
| Freeze assumes B/A emit a bare integer first | Protocol design flaw | Needs an amendment, not a bug fix. |
| `B_restart_reason` arm (descriptive only) | Cap artefact | 128-token cap truncates 1,685 of 1,800 records, (F1 300/300, F2add 276, F2mul 209, F3 300/300 each). "Last integer in text" on truncated prose is meaningless, so the arm's 5% is not interpretable. It does not enter any gate. |
| Oracle only issued for valid A (319) | Per freeze ("invalid_A_oracle" rule) | Not a bug, but a 4-token B failure plus A-valid selection means the gate is effectively unobservable on 5 of 6 cells. |

## Minimal fix proposal (harness bugs only)

No harness bug qualifies, so no code was changed and no GPU smoke was run. Per the instructions, gates, thresholds and prompts are untouched.

If Opus decides to amend the freeze so RQ7 can actually measure what it intends (this is a protocol amendment, not a bug fix), the least invasive options in order of fidelity to the frozen prompts are:

1. **Digit-restricted first-token readout** for A and B: keep the frozen prompts, but score the argmax over digit tokens `0..9` (then continue greedy over digits only up to the base width) instead of free generation. This measures the silent answer without the model's chatty-prose habit. The A "silent format" gate then becomes a first-token-digit-mass gate, so the 95% format gate has to be redefined.
2. **Assistant-prefill** of an answer anchor (e.g. a short fixed prefix such as `The answer is `) for B readouts only. This keeps A's format gate meaningful (it still tests silence) and fixes B's readout.
3. **Raise B readout cap and last-integer parse** for the oracle and restart arms only (descriptive).

Option 2 is the smallest change that preserves the A-side silence test. Whichever is chosen, A-format failures on F1 and depth-2 cells (about 100% prose openers) are genuine, so those cells would still fail the A-silent gates. The realistic candidates for PCS7 are F3 depth 1 and F2 add.

I did not run any new GPU work and did not launch the full RQ7 rerun.
