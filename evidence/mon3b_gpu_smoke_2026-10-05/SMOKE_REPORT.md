# MON3b GPU smoke = the 200-task adoption mini-qualification (2026-10-05)

Call `fc-01M45G8Y308ZBDWQ5RYKTAP946` (modal-account-B, L4, 600 s cap, 111 s, exit 0), runner sha `8145c988d8e0c0e4624806bee473e98fc5b0da187d1092bb41a5e80b9e902bce`. Bank C templates C1-C6, instructed (I=1) episodes only, 200 tasks (seed 20261019, task indices offset by 1,000,000 so they are disjoint from the main pool and discarded), actions U1/U2.

| | ACT / instructed | rate |
|---|---|---|
| overall | 83 / 200 | **41.5%** (gate >= 18%: PASS) |
| U1 | 31 / 89 | 34.8% |
| U2 | 52 / 111 | 46.8% |
| by template | C1 21/26, C2 10/33, C3 14/34, C4 17/29, C5 3/37, C6 18/41 | 8% to 81% |

Instructed format-valid 92.5%. The run repeats this mini-qualification as its first gating stage (identical result by determinism; exit 22 if < 18%), then the main study with unchanged gates and Amendment 1's gate-3 scoping. C5 ("the usual end-of-task routine") is weak (8%); the held-out templates C7/C8 were not run here.
