# RQ6 bounded real-model smoke

**Modal call:** `fc-01M44R5VA6B1CC6ZBHTDM8F6B9`  
**Profile / GPU:** `modal-account-B` / L4, 24 GiB  
**Launcher SHA-256:** `a85ddb38264bc9cedaf8c873a0e152ca284758c59306bc51d5e918de8a212877`  
**Output:** `pcs-core-artifacts:rq6-real-model-smoke-a85ddb38264b/`  
**Duration:** 87.22 seconds; exit code 0 under the 600-second cap.

This smoke loaded the pinned Qwen3-4B and Qwen3-1.7B revisions locally from cache, loaded the pinned GSM8K `main` dataset revision, and exercised the core 6A capture and 6B prompt paths. It is explicitly smoke-only and did not run qualification gates.

## Observed checks

- 6A source generated and parsed: **yes**.
- 6A W/U capture positions located: **yes / yes**.
- 6A hidden capture finite: **yes**.
- B oracle arm generated output: **yes**, but its continuation did **not** parse as the required three `STATE` lines plus `FINAL_SUMMARY`.
- GSM8K checkpoint construction: **yes**; selected 3,000 train and 500 test rows.
- GSM8K source answer parsed under the frozen `Answer: <number>` rule: **no** for this one smoke example.
- Dataset manifest SHA-256: `f158f9727acfd9361c2240abcdc2c367f76201609b1e9ed2dee1cd68fd1fc1d9`.

The launcher returned success because this is a plumbing smoke, but the two failed format checks are material. Treat RQ6 as **smoke-executed with output-format issues requiring review**, not as format-qualified or ready for a full run. The smoke has n=1 per path and measures no accuracy. Full RQ6 remains unlaunched.

The first attempted call, `fc-01M44R3KP2D99YYJNB85SRP0QC`, failed before model inference because the launcher resolved its runner outside `/root/scripts/`. The launcher path resolution was fixed and covered by `tests/test_modal_rq6_launcher.py`; the successful call above ran with the corrected path.
