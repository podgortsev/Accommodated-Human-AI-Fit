# STATUS

Paper 4, Progressive Human-AI Fit. Absorbs Paper 5 (2026-09-28).
Read before starting, write before stopping.

States: `-` not started, `SCRIPT READY`, `RUNNING`, `done`, `FAILED: reason`

---

## Where this is

e0, the instrument floor, is ready to run. It decides whether Paper 4 exists.
Nothing collected yet.

| step | state | note |
|---|---|---|
| prior art | done | `docs/related-work-paper-4.md` in the research repo, three rounds, 55 quotes verified |
| Paper 5 merged in | done | recorded in `docs/research-program.md` |
| delivery instrument | done | `scripts/p4_checks.py`, five needs |
| instrument validated offline | done | `scripts/validate_p4_checks.py`, 29 checks, 0 failures |
| design | drafted | `DESIGN.md` |
| e0 preregistration | done | `experiments/e0-instrument-floor/PREREGISTRATION.md`, committed before any run |
| e0 stimuli | done | 120 questions x 17 cells, word counts checked mechanically |
| e0 scripts | done | validated offline, 46 checks, 0 failures |

## Experiments

| id | what | model | collected | analysed | result |
|----|------|-------|-----------|----------|--------|
| e0 | instrument floor | qwen | SCRIPT READY | - | - |
| e0 | instrument floor | llama | SCRIPT READY | - | - |
| e0 | instrument floor | mistral | SCRIPT READY | - | - |

## Blocked

- nothing

## Next

1. Run e0 on all three models: `colab/run_p4_e0_<model>.ipynb`, bundle `colab/p4_e0.zip`.
2. `analyse_e0.py` on the three CSVs together gives CONTINUE, EXTEND or STOP.
3. On CONTINUE: rank Paper 4, then the full menu (penalty on the same response, turns with the CONCAT control, "declines to say").

## The decision that can end this paper

e0's registered rule: CONTINUE if at least two needs pass on at least two
models; EXTEND to 240 questions if the misses are inconclusive rather than null;
STOP otherwise, and e0 is published as the result.
