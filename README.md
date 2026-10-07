# Accommodated Human-AI Fit

What a language model changes when a person says what they need, measured
against a socially neutral personal detail of the same length, on three open
models (Qwen2.5-7B, Llama-3.1-8B, Mistral-7B), in six preregistered experiments
and 27,990 generated answers.

The paper: `paper/paper.pdf` (source `paper/paper.tex`).

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

    paper/                  the paper
    scripts/                p4_checks.py (the delivery instrument), p4_stats.py,
                            p4_gen.py, runners, validators, analyse_refusals.py
    experiments/e0 to e5/   one folder each: PREREGISTRATION.md, scripts/,
                            outputs/<model>/ (raw answers), results/RESULT_*.md
    shared/tasks/           the verified calculation tasks used by e4
    CHECKLIST.md            the methodology checklist, item by item
    DESIGN.md, STATUS.md    the design and the state of the work

## Reproduce

Every analysis runs from its CSVs without a GPU, for example

    python experiments/e2-deaf-contact/scripts/analyse_e2.py \
        experiments/e2-deaf-contact/outputs/*/e2_*.csv

Every experiment has an offline validator that injects known effects into a
stubbed model and checks that the analysis recovers them:
`scripts/validate_p4_checks.py`, `experiments/e0-instrument-floor/scripts/validate_e0.py`,
`experiments/e1-measurable-needs/scripts/validate_e1.py`,
`experiments/e2-deaf-contact/scripts/validate_e2.py`, `scripts/validate_e3_e4.py`,
`scripts/validate_e5.py`. Collection needs a GPU; the runners take a model key
(`qwen`, `llama`, `mistral`) and resume from their CSVs.

## Related papers

- Paper 2, Single Human-AI Fit, concept DOI 10.5281/zenodo.22364497.

Code under MIT. The paper and its Zenodo record under CC BY 4.0.
