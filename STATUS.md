# STATUS

Paper 4, Progressive Human-AI Fit. Absorbs Paper 5 (2026-09-28).
Read before starting, write before stopping.

States: `-` not started, `SCRIPT READY`, `RUNNING`, `done`, `FAILED: reason`

---

## Where this is

Design stage. No data collected, no model run, no preregistration written yet.

| step | state | note |
|---|---|---|
| prior art | done | `docs/related-work-paper-4.md` in the research repo, 10 quotes verified |
| Paper 5 merged in | done | recorded in `docs/research-program.md` |
| delivery instrument | done | `scripts/p4_checks.py`, five needs |
| instrument validated offline | done | `scripts/validate_p4_checks.py`, 29 checks, 0 failures |
| design | drafted | `DESIGN.md`: four cells, the progressive arm, the two gates |
| task set | - | must carry all five needs per item; screening is mechanical |
| stimulus set | - | need form and label form per need, plus three neutral details |
| power calculation | - | Paper 3 needed 600 items after measuring 20 percent power at 200 |
| preregistration | - | written and dated before any model is run |
| collection | - | three models, as Papers 2 and 3 |

## Blocked

Nothing. The next step needs no compute.

## Next

1. Build the task set and screen it mechanically for headroom on all five needs.
2. Power calculation for a paired difference of proportions.
3. Preregistration, then collection.

## The decision that can end this paper

Gate 1 in `DESIGN.md`: if the neutral cell moves delivery as much as the matched
cell on every need and every model, the instrument counts personal context rather
than reading it, and there is no paper. That is checked before anything is
claimed, and a failure is published as a failure.
