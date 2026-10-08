# Combined results

Six preregistered experiments, three open models (Qwen2.5-7B, Llama-3.1-8B,
Mistral-7B), one question: when a person states a need, does the model serve
them better than a neutral personal detail of the same length would?

This document holds the argument across experiments. Each experiment's own
`results/RESULT_*.md` holds its design, numbers and caveats in full, and where the
two differ the experiment document is the authority. Every number below is
checked against the committed data by `verify_paper_numbers.py`.

---

## 1. The design in one paragraph

Every question is asked in seventeen versions that differ only in a lead-in: none;
a 16-word statement of each of five needs, never naming what is checked ("I cannot
hear, so any step that needs sound or speaking will not work for me"); a 5-word
label for each ("I am Deaf, for context"); and three neutral details at 16 and 5
words ("I bake bread most Saturday mornings..."). Delivery of each need is decided
by a script with no model in the loop (`experiments/shared/scripts/p4_checks.py`).
The need is compared with the neutral detail of the same length, paired within
question, under a rule that requires two tests to agree.

## 2. The findings

| # | finding | where | status |
|---|---|---|---|
| 1 | Stating a need buys accommodation a neutral detail does not, for deafness, wheelchair use and reading difficulty, on all three models | e0, e1, e2 | registered, confirmed |
| 2 | For deafness the accommodation is added, not substituted: a text route appears (10-18 to 48-62 percent of answers) while 56 to 82 percent of phone instructions remain | e2 | registered, confirmed on 3 of 3 |
| 3 | Finding 2 holds under three wrappers, including the lead-in after the question; the wrapper moves the size by up to a quarter of the scale | e5 | registered, holds 9 of 9 |
| 4 | Restating "I cannot hear" removes the phone instruction more than a neutral retry on two models; naming the barrier removes it on all three | e3 | registered, H4 2 of 3, H5 3 of 3 |
| 5 | The label matters by need: close to the need for deafness, better than the need for wheelchair use, worse than a neutral detail for a learning disability | e1, e2 | H3 registered, confirmed |
| 6 | Llama refuses ordinary banking and administrative help in 19 to 33 percent of answers after "I have a learning disability", and almost never after the stated need | e0, e2 | exploratory |
| 7 | Stating a need does not consistently cost accuracy on a keyed task in the same answer; on Mistral the cost is dropped formatting | e4 | H6 registered, not confirmed |
| 8 | A neutral detail moves delivery in 5 of 198 floor tests | e0 to e2 | registered |

## 3. Need benefit by experiment

Delivery after the need form minus delivery after the neutral details.

| need | experiment | Qwen | Llama | Mistral |
|---|---|---|---|---|
| deafness | e0 | +0.22 | +0.24 | +0.15 |
| deafness | e2 | +0.39 | +0.43 | +0.26 |
| wheelchair use | e1 | +0.66 | +0.61 | +0.43 |
| plain language | e1 | +0.10 | +0.09 | +0.09 |
| plain language | e2 | +0.32 | +0.37 | +0.26 |

## 4. What could not be shown, and what was corrected

- **Screen reader**: unmeasurable. These models' default answers contain no
  tables or emoji even on comparison questions (one table in 180 answers), so
  there is nothing to adapt on the dimensions the check scores.
- **No vision**: +0.13 to +0.17, claimed on one model of three. Not established.
- **Wheelchair, removal side**: the walking assumption is rare at baseline and
  mostly removed once the need is stated (13 to 27 percent left). "Added, not
  substituted" is a deafness result. First reported the other way and corrected.
- **Plain language in e0**: the first sentence splitter merged unpunctuated list
  items; Mistral's -0.23 became +0.21 with the corrected splitter, registered
  before e1.
- **Deafness in e1**: tested on questions where nobody contacts anyone, so not a
  test; e2 exists to fix that, with a registered relevance check.
- **Legal framing**: dropped. The UK Equality Act counts a reasonable means of
  avoiding a barrier as an adjustment, so "added, not removed" is not framed as
  non-compliance.

## 5. Where each finding lives

| experiment | folder | result |
|---|---|---|
| e0 instrument floor | `experiments/e0-instrument-floor/` | `results/RESULT_e0.md` |
| e1 measurable needs | `experiments/e1-measurable-needs/` | `results/RESULT_e1.md` |
| e2 deafness where it arises | `experiments/e2-deaf-contact/` | `results/RESULT_e2.md` |
| e3 pushback | `experiments/e3-pushback/` | `results/RESULT_e3.md` |
| e4 cost | `experiments/e4-cost/` | `results/RESULT_e4.md` |
| e5 wrappers | `experiments/e5-wrappers/` | `results/RESULT_e5.md` |
| refusals, exploratory | `experiments/exploratory-refusals/` | `results/RESULT_refusals.md` |
