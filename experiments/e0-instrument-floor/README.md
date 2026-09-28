# e0: the instrument floor

Does a model deliver an accommodation because a person stated the need, or
because a person said anything about themselves? The gate for Paper 4.
Registered expectations and the decision rule: `PREREGISTRATION.md`.

## Files

    scripts/build_e0_stimuli.py   120 questions, 17 cells, word counts checked
    scripts/e0_stimuli.json       what the runner reads
    scripts/run_e0.py             collect (resumable) then analyse; --smoke first
    scripts/analyse_e0.py         the read to trust, no GPU
    scripts/validate_e0.py        offline check, 46 passes, output saved in
                                  validate_e0_output.txt
    outputs/<model>/              e0_<model>.csv and the console text

Instrument and statistics: `../../scripts/p4_checks.py`, `../../scripts/p4_stats.py`.

## Cost

2,040 generations per model, 400 new tokens, batch 16 on a T4 at 4-bit. Expect
two to three hours per model, Mistral longer; resumable across sessions.

## Status

SCRIPT READY. Nothing collected.
