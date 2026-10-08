# e3: pushback

Each model's own answer to "I cannot hear", replayed, then one of three 14-word
follow-ups: a neutral retry, a restatement of the need, or the need plus "phone
calls will not work for me". Does the phone instruction go? Registered:
`PREREGISTRATION.md`.

    scripts/build_e3_jobs.py   first turns from e0 and e2, e3_turn1.json
    scripts/analyse_e3.py      the read to trust, no GPU
    run and validate           ../../scripts/run_e3_e4.py, validate_e3_e4.py

630 generations per model. Done: `results/RESULT_e3.md`. The consoles of the shared e3 and e4 session are filed here as `outputs/<model>/e34_*`.
