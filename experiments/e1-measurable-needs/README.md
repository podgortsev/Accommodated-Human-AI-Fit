# e1: the needs e0 could not measure

Three new pools of 60 questions, one each for screen_reader, no_vision and
wheelchair, in e0's 17 cells; deaf and plain_language replicated on all 180.
Instrument version 2, 250-word window. Registered: `PREREGISTRATION.md`.

## Files

    scripts/build_e1_stimuli.py   180 questions in three pools; lead-ins from e0
    scripts/e1_stimuli.json       what the runner reads
    scripts/run_e1.py             phase 1 none cells and the pool gate, phase 2
                                  the rest; resumable; --smoke first
    scripts/analyse_e1.py         the read to trust, no GPU
    scripts/validate_e1.py        offline check, 26 passes, output in
                                  validate_e1_output.txt
    outputs/<model>/              e1_<model>.csv, e1_<model>_gate.json, consoles

## Cost

Up to 3,060 generations per model, about four hours on a T4, resumable.

## Status

Done. Result: `results/RESULT_e1.md`.
