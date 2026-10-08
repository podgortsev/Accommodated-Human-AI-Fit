# Accommodated Human-AI Fit

What a language model changes when a person says what they need, measured
against a socially neutral personal detail of the same length, on three open
models (Qwen2.5-7B, Llama-3.1-8B, Mistral-7B), in six preregistered experiments
and 27,990 generated answers.

The paper: `accommodated-human-ai-fit.pdf` (source `accommodated-human-ai-fit.tex`).
In plain language: `explainer.md`. Across experiments: `RESULTS.md`. What it
cannot claim: `limitations.md`.

## Findings in brief

- Stating a need buys accommodation a neutral detail does not, for deafness,
  wheelchair use and reading difficulty, on all three models.
- For deafness the accommodation is added, not substituted: a text route appears
  while 56 to 82 percent of instructions to phone remain. Holds under three
  wrappers (e5).
- Saying "I cannot hear" again helps on two models; "phone calls will not work
  for me" removes the instruction on all three (e3).
- The label matters by need. After "I have a learning disability" answers are
  less plain than after a neutral detail, and Llama refuses ordinary banking and
  administrative help in 19 to 33 percent of cases (exploratory).
- Stating a need does not consistently cost accuracy on a keyed task in the same
  answer (e4).
- Screen-reader accommodations could not be measured: these models' defaults
  already contain none of the formatting the check scores.

## Layout

    accommodated-human-ai-fit.tex, .pdf   the paper
    RESULTS.md, explainer.md, limitations.md
    verify_paper_numbers.py               checks every table value and abstract
                                          figure against the committed data
    figures/                              the two figures and make_figures.py,
                                          which computes them from the CSVs
    experiments/
        shared/                           the instrument, statistics, generation
                                          code and the e4 tasks (README inside)
        e0-instrument-floor/              each experiment: README.md,
        e1-measurable-needs/              PREREGISTRATION.md, scripts/,
        e2-deaf-contact/                  outputs/<model>/ (raw answers and
        e3-pushback/                      consoles), results/RESULT_*.md
        e4-cost/
        e5-wrappers/
        exploratory-refusals/             refusals counted after the fact
    CHECKLIST.md                          the methodology checklist, item by item
    DESIGN.md, STATUS.md                  the design and the state of the work

The repository was reorganised on 2026-10-08 to match Paper 2's layout; the old
paths, which the preregistrations name, are listed in `experiments/shared/README.md`.

## Reproduce

No GPU is needed to reproduce any number. With `pip install -r requirements.txt`:

    python verify_paper_numbers.py

re-runs every analysis from the committed answers and checks the paper against
it. Each experiment's analysis also runs on its own, for example

    python experiments/e2-deaf-contact/scripts/analyse_e2.py \
        experiments/e2-deaf-contact/outputs/*/e2_*.csv

Every experiment has an offline validator that injects known effects into a
stubbed model and checks that the analysis recovers them (160 checks in all):
`experiments/shared/scripts/validate_p4_checks.py`,
`experiments/e0-instrument-floor/scripts/validate_e0.py`,
`experiments/e1-measurable-needs/scripts/validate_e1.py`,
`experiments/e2-deaf-contact/scripts/validate_e2.py`,
`experiments/e3-pushback/scripts/validate_e3_e4.py`,
`experiments/e5-wrappers/scripts/validate_e5.py`.

Collecting the answers needs a GPU; each `run_*.py` takes a model key (`qwen`,
`llama`, `mistral`) and resumes from its CSV.

## Related

- Paper 2, Single Human-AI Fit, concept DOI 10.5281/zenodo.22364497.

Code under MIT. The paper and its Zenodo record under CC BY 4.0.
