# Shared

Code and data used by more than one experiment.

    scripts/p4_checks.py           the delivery instrument: for each of five needs,
                                   properties an answer has or lacks, decided with no
                                   model in the loop. Version 1 (e0) and version 2
                                   (line-aware plain language, 250-word window; e1 on)
    scripts/validate_p4_checks.py  36 offline checks of the instrument
    scripts/p4_stats.py            the claim rule: signed-rank and sign-flip both
                                   required, Benjamini-Hochberg, Holm for floors
    scripts/p4_gen.py              generation for any number of turns, and the
                                   resumable job collector used by e3 to e5
    tasks/tasks.json               verified arithmetic tasks; e4 uses the first 330
                                   with numeric answers. Copied from the author's
                                   Paper 3 task set (commit bd37f7f of that repository)

## Where files were before 2026-10-08

The repository was reorganised on 2026-10-08 to match Paper 2's layout. The
preregistrations name files at the paths they had when registered:

    scripts/p4_checks.py, p4_stats.py, p4_gen.py, validate_p4_checks.py
        -> experiments/shared/scripts/
    scripts/run_e3_e4.py, validate_e3_e4.py  -> experiments/e3-pushback/scripts/
    scripts/run_e5.py, validate_e5.py        -> experiments/e5-wrappers/scripts/
    scripts/analyse_refusals.py              -> experiments/exploratory-refusals/scripts/
    shared/tasks/tasks_p3.json               -> experiments/shared/tasks/tasks.json
    paper/paper.tex, paper.pdf               -> accommodated-human-ai-fit.tex, .pdf

Every analysis was re-run from the new locations and reproduces its committed
output byte for byte; every validator passes.
