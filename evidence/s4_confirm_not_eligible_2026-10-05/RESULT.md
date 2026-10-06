# S4-confirm: NOT RUN, per pre-registration (Claude), 2026-10-05

Design 03 says S4-confirm "runs once, only if PCS3c is POSITIVE or NEAR_MISS". PCS3c was classified **PCS3C_NULL** (`evidence/pcs3c_confirm_2026-10-05/`: specificity +52 confirmed, but fidelity 58% < 70%).

The launch `fc-01M4613B9ASQXJCJ4BTNAAEPXK` (modal-account-A) correctly refused at input admission with `S4C_PCS3C_CLASSIFICATION_NOT_ELIGIBLE 'PCS3C_NULL'`. No data was opened, and no filter or probe was fitted.

**Status:** selective inheritance (S4) is untested at C = 64. Evidence so far: S4-dev at C = 16 found that the adversarial filter (F-train) nearly meets the retention criteria, while LEACE rank-9 destroys the other registers. S4-confirm moves to the funded phase with a bridge that meets PCS3c's bar.
