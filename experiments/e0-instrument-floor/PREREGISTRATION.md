# e0 preregistration: does the delivery instrument read the need?

Registered 2026-09-28, before any model was run. Committed with the scripts it
describes; the commit hash is the timestamp. Nothing below changes after the
first generation. A change made after that is reported as a deviation, with its
reason, next to the result.

---

## Question

When a person states a need, does a model deliver the accommodation that need
calls for more often than when the person states a socially neutral detail of
the same length in the same position?

This is the gate for Paper 4. The prior-art pass (`docs/related-work-paper-4.md`
in the research repository, three rounds, 55 quotes verified) found that every
published benefit result is scored as adherence to the disclosed thing, which is
undefined without the disclosure, so none can say how much of the benefit the
disclosure caused. e0 scores the accommodated behaviour itself, which is defined
in every cell, and reads it against a neutral arm.

## Design

- **Models.** Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct,
  Mistral-7B-Instruct-v0.3, 4-bit, greedy, one user turn, no system prompt,
  400 new tokens.
- **Items.** 120 practical how-to questions (`scripts/build_e0_stimuli.py`),
  chosen so each could involve contacting an organisation, going somewhere in
  person, a screen or form, and enough substance for reading level to vary.
- **Cells, 17 per question.** `none`; the need form of each of five needs
  (16 words, states the functional need, never names a checked property); the
  label form of each (5 words); three neutral details at 16 words and the same
  three at 5 words. 2,040 generations per model.
- **Outcome.** Delivery of each need, decided by `scripts/p4_checks.py` alone,
  with no model in the loop. Thresholds and lexicons as committed on
  2026-09-28 in commit 9e26eb8 of this repository and not tuned afterwards.
  Every answer is scored on all five needs.
- **Needs.** screen_reader, no_vision, deaf, plain_language, wheelchair.

## Contrasts, per model and need N, paired within question

| name | definition | role |
|---|---|---|
| need benefit | D(need:N) minus the mean of D(neutral_long:k) over k | **the gate** |
| label benefit | D(label:N) minus the mean of D(neutral_short:k) | reported |
| specificity | D(need:N) minus the mean of D(need:M), M not N | reported |
| over-application | mean D(need:M), M not N, minus mean D(neutral_long:k) | reported |
| floor | D(neutral_*:k) minus D(none), six per need | reported |

## Tests and corrections

The Paper 3 claim rule, `scripts/p4_stats.py` (copied verbatim from Paper 3):
an effect is claimed only if the Wilcoxon signed-rank test and the sign-flip
permutation test on the mean both reject after Benjamini-Hochberg at 0.05, and
both lean the same way. One BH family per contrast type per model, five tests
each. Floors: one Holm family per model on either test, "moves" if either
rejects. Means reported with a percentile bootstrap interval (4,000 draws) and
the minimum detectable effect.

## Gates and the decision

- **Gate 2, headroom.** A need is UNMEASURABLE on a model if its delivery rate
  in `none` is above 0.90 or below 0.02.
- **Gate 1, benefit.** Otherwise a need PASSES if its need benefit is claimed
  and positive; is NULL if not claimed and the upper bound of its 95 percent
  interval is below 0.20; is INCONCLUSIVE otherwise.

**Decision across the three models:**

- **CONTINUE** Paper 4 if at least two needs PASS on at least two models.
- **EXTEND** if not, but counting INCONCLUSIVE as PASS would reach CONTINUE:
  collect e0b, 120 further questions written to the same rules, and decide on
  all 240 with the same analysis.
- **STOP** otherwise. e0 is then the result, reported as one.

## Power, from the offline validator

Simulated on the claim rule at 0.01 (a lower bound for a BH family of five),
n = 120, base delivery 0.40: power 0.17, 0.61, 0.93, 0.97 for differences of
0.10, 0.15, 0.20, 0.25. The margin for NULL, 0.20, is therefore the size e0 can
both detect and exclude. A benefit smaller than 0.20 is not resolved by e0 and
is not reported as absent.

The validator first ran at 60 questions. There a true null read as NULL in only
10 of 15 cells, because the interval could not exclude 0.20. The item count was
doubled before any data. Recorded here because it is a design choice made on
simulated evidence.

## What would confirm, what would refute

**Confirms the instrument, and Paper 4 goes on:** delivery rises from the
neutral arm to the need arm for at least two needs on at least two models.

**Refutes:** the need arm delivers no more than the neutral arm. If the neutral
arm also moves delivery against `none`, the model is responding to the presence
of a person, not to the need, and that is the finding.

**Secondary, registered now so they cannot be chosen later:**

1. The neutral arm moves delivery against `none` (the "any person" effect).
   PrefEval (Zhao et al. 2025) predicts it does. Direction not predicted.
2. The label form delivers less than the need form. Predicted, from Taheri et
   al. and NDBench: models serve instructions more than identities.
3. Over-application is positive: a stated need raises delivery of other needs.
   Predicted, from PRISK (Wang et al. 2026) and Taheri et al.

## Known limitations, stated before the data

- One wrapper (no system prompt, lead-in then question). Paper 2 method 3c
  showed neutral wrappers move baselines by 2 to 5 points. The three neutral
  details give the floor's own spread; wrapper robustness is left to the main
  menu if e0 passes.
- The syllable counter undercounts vowels in hiatus (`validate_p4_checks.py`
  pins the cases). The bias is constant across cells and cancels in every
  contrast.
- screen_reader and no_vision share the layout-deixis part, so specificity
  between them is expected to be low by construction. Reported, not
  interpreted as over-application.
- Left padding in batched generation can move greedy text numerically. Prompts
  are sorted by length, so both sides of each gate contrast (16 against 16
  words, 5 against 5) share batches. The GPU smoke check reports batch against
  single agreement before collection.
