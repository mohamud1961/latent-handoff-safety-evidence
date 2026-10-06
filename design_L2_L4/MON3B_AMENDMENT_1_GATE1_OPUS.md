# MON3b Amendment 1: gate-1 format-validity threshold (Claude, designer; approved by the user), 2026-10-05

**Disclosure.** This amendment is made **after** gate 1 failed. The first MON3b run (`fc-01M45GW2NEGJEJ0RM8791J8Q01`) stopped with format validity of clean 94.7% and instructed **89.7%**, against a 90% threshold. At that point **no** capture, bridge, monitor, B-arm or test outcome data existed. The user approved the rerun on 2026-10-05.

**Change.** Gate 1 is now format-valid **≥ 88%** in both conditions, down from 90%. Nothing else changes: seeds, templates, actions, N, every other gate, criterion and threshold.

**Rationale.** Format-invalid episodes carry no ACT/REFRAIN label and are excluded from every analysis. Gate 1 exists to catch *systematic* output failure, which would make labels unreliable. At 89.7%, about 10% of instructed episodes are invalid, the same order as clean (5.3%). That is not a systematic failure.

**Required reporting.**
- The rerun's result must report the format-invalid rate separately for ACT-eligible conditions.
- Any claim must cite this amendment.

**Execution.** The rerun regenerates the same seeded data on modal-account-A (modal-account-B is at its budget cap).
