# e5: wrappers

The deafness headline of e2 re-tested under two further wrappers: a neutral
opening sentence before the lead-in, and the lead-in placed after the question.
Required by the methodology checklist (several wrappers, position).
Registered: `PREREGISTRATION.md`.

    scripts/build_e5_jobs.py   e2's 90 questions x 2 wrappers x 4 cells
    scripts/analyse_e5.py      the read to trust, no GPU; the original wrapper
                               is read from e2's committed answers
    scripts/run_e5.py          collect, then analyse
    scripts/validate_e5.py     offline check, 9 passes, validate_e5_output.txt

720 generations per model. Done: the headline holds under all three wrappers on
all three models, `results/RESULT_e5.md`.
