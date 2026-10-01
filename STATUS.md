# STATUS

Paper 4, Progressive Human-AI Fit. Absorbs Paper 5 (2026-09-28).
Read before starting, write before stopping.

States: `-` not started, `SCRIPT READY`, `RUNNING`, `done`, `FAILED: reason`

---

## Where this is

e0 is collected and analysed: registered decision CONTINUE (`experiments/e0-instrument-floor/results/RESULT_e0.md`). e1 is collected and analysed (`experiments/e1-measurable-needs/results/RESULT_e1.md`): wheelchair and plain language are findings on all three models, H2 (added, not removed) confirmed for wheelchair, H3 (need over label) confirmed. The deaf replication was mis-specified: e1's questions rarely involve contacting anyone.

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
| e0 | instrument floor | qwen | done | done | PASS deaf +0.22, plain +0.58 |
| e0 | instrument floor | llama | done | done | PASS deaf +0.24, plain +0.37 |
| e0 | instrument floor | mistral | done | done | PASS deaf +0.15; plain -0.23 (splitter artefact, +0.21 line-aware) |
| e1 | measurable needs | qwen | done | done | PASS wheelchair +0.66, plain +0.10; H2 wheelchair, H3 yes; screen reader unmeasurable |
| e1 | measurable needs | llama | done | done | PASS wheelchair +0.61, plain +0.09; H2 wheelchair, H3 yes; screen reader unmeasurable |
| e1 | measurable needs | mistral | done | done | PASS wheelchair +0.43, plain +0.09, no_vision +0.17; H2 wheelchair, H3 yes |

## Blocked

- nothing

## Next

1. Draft the paper around RESULT_e0.md and RESULT_e1.md.
2. Author decision: whether a deaf replication on contact-type questions is worth one more run before release.
3. Zenodo, ORCID, SSRN in that order.

## The decision that can end this paper

e0's registered rule: CONTINUE if at least two needs pass on at least two
models; EXTEND to 240 questions if the misses are inconclusive rather than null;
STOP otherwise, and e0 is published as the result.
