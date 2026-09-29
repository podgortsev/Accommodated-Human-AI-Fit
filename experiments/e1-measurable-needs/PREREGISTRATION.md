# e1 preregistration: the needs e0 could not measure

Registered 2026-09-29, after e0 and before any e1 generation. Committed with
the scripts it describes. A change after the first generation is reported as a
deviation next to the result.

---

## Why e1 exists

e0 (`../e0-instrument-floor/results/RESULT_e0.md`) passed its registered gate,
CONTINUE, but measured only two of five needs. On practical how-to questions the
models never drew tables or referred to colour or position (screen_reader and
no_vision at the ceiling) and never offered step-free access unprompted
(wheelchair at the floor). Two post hoc checks in e0 also found that the
plain-language check partly measured list punctuation, and that truncation at
the token cap differed by cell. e1 fixes all three, in advance.

## What changes from e0, and why

1. **Questions.** Three new pools of 60 (`scripts/build_e1_stimuli.py`), one per
   unmeasured need, chosen so that the ordinary answer tends to break that need:
   comparisons and schedules (screen_reader), device screens and visual
   judgements (no_vision), getting somewhere and getting around (wheelchair).
   No question repeats e0.
2. **Instrument version 2** (`scripts/p4_checks.py`, version 2 section, 36
   offline checks). plain_language uses a line-aware sentence splitter;
   everything else is version 1 unchanged. Version 1 remains for e0.
3. **Window.** Every answer is scored on its first 250 words.
4. **Gate 2 counts only the ceiling.** A need is UNMEASURABLE if its `none`
   delivery exceeds 0.90. e0 also excluded rates below 0.02; that was wrong for
   a benefit, which is a rise, and it excluded wheelchair where the base rate of
   zero leaves the whole range to rise into. e0's registered verdicts are not
   revised.
5. **Early stop per pool.** The `none` cell is generated first for all 180
   questions. A pool whose own need is above the ceiling on a model is dropped
   for that model before its other 16 cells are generated, and reported as
   UNMEASURABLE. The decision is written once and not revisited.

Unchanged from e0: the 17 cells and every lead-in, models, 4-bit, greedy,
400 new tokens, one user turn, no system prompt, the claim rule, the corrections.

## Item sets

- screen_reader, no_vision, wheelchair: the 60 questions of their own pool.
- deaf, plain_language: every collected question, up to 180 (a replication of
  e0 on new questions).

## Contrasts, per model and need N, paired within question

As e0: need benefit (the gate), label benefit, specificity, over-application,
six floors. Plus two registered hypotheses, each from an exploratory e0 result:

- **H2, added but not removed.** For deaf, d(offers_text_route) minus
  d(no_phone_instruction); for wheelchair, d(offers_step_free) minus
  d(no_walking_assumption). Each d is the need form minus the neutral_long mean.
  Predicted positive: stating the need buys an addition more than it removes the
  barrier. In e0 all three models added a text route (+0.28 to +0.32) and none
  removed the phone instruction.
- **H3, need over label.** For plain_language, D(need) minus D(label). Predicted
  positive. In e0 the label form bought nothing on any model.

## Tests, corrections, verdicts

The Paper 3 claim rule (`scripts/p4_stats.py`): signed-rank and sign-flip both
reject after Benjamini-Hochberg at 0.05, same direction. One BH family per
contrast type per model; H2's two tests (deaf, wheelchair) are one family. Floors
one Holm family per model, either test.

Per need and model: UNMEASURABLE (ceiling); PASS (need benefit claimed and
positive); NULL (not claimed and upper 95 percent bound below 0.25 for a
60-question pool, 0.20 for 180 questions); INCONCLUSIVE otherwise.

## The registered read

- A need is a **finding** of Paper 4 if it PASSES on at least two of three models.
- H2 (each of deaf and wheelchair) and H3 are **confirmed** if claimed positive
  on at least two models.
- Everything else is reported with its verdict, including nulls and
  unmeasurable cells. There is no stop decision: e0 already made it.

## Power, from the offline validator

Claim rule at 0.01, base delivery 0.40. n = 60: 0.24, 0.51, 0.79, 0.94 for
differences of 0.15, 0.20, 0.25, 0.30. n = 180: 0.76, 0.99, 1.00, 1.00. The
pools resolve a benefit of 0.25; smaller ones are INCONCLUSIVE, not absent.

## Known limitations, stated before the data

- One wrapper, as e0.
- The text-route lexicon is conservative: "send them an email" does not count,
  "contact them by email" does. The validator found this. It undercounts
  additions equally in every cell, so it makes H2 harder to confirm, not easier.
  The lexicon is not changed, because it is registered.
- Pool questions are written to break their need; that is their purpose, and it
  means pool base rates are not estimates of how often models break these needs
  in general use.
- screen_reader and no_vision share the layout-deixis part.
- Left padding in batches, as e0: both sides of each gate contrast share batches.
