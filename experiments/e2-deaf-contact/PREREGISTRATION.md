# e2 preregistration: the deaf need, tested where it arises

Registered 2026-10-01, after e1 and before any e2 generation. Committed with the
scripts it describes. A change after the first generation is reported as a
deviation next to the result.

---

## Why e2 exists

In e0 all three models answered "I cannot hear" by adding a text route (+0.28 to
+0.32 against a neutral detail) without removing the instruction to phone (all
intervals included zero). That decomposition was exploratory. e1 registered it
as H2 for deaf but put the deaf need on questions where nobody contacts anyone:
a phone instruction appeared in 1 to 2 percent of baseline answers, so e1 could
not test it (`../e1-measurable-needs/results/RESULT_e1.md`, section 2.1). e1 did
confirm the same pattern for wheelchair on all three models. e2 tests the deaf
version where it can arise.

## Design

e1's design and code unchanged except the questions:

- **90 new questions** (`scripts/build_e2_stimuli.py`), each one whose ordinary
  answer involves contacting an organisation, where phoning is the default route
  and a text route is possible. None repeats e0 or e1.
- e0's 17 cells and lead-ins, the three models, 4-bit, greedy, 400 new tokens.
- Instrument version 2, 250-word window; e1's two-phase collector and ceiling
  gate; e1's analysis (`analyse_e1.analyse_model`) called unchanged by
  `analyse_e2.py`.

## Relevance check, new, from e1's mistake

A model's deaf result is a **test** only if a phone instruction appears in at
least 0.10 of its `none` answers. Below that the barrier is absent and the
model is excluded from the registered read, whatever its numbers say.

## Hypotheses and the registered read

- **Deaf need benefit**: delivery under the need form minus the neutral_long
  mean. A **finding** if it PASSES on at least two models that are tests.
- **H2, added but not removed**: d(offers_text_route) minus
  d(no_phone_instruction), each the need form minus the neutral_long mean.
  Predicted positive. **Confirmed** if claimed positive on at least two models
  that are tests.
- plain_language is scored on every answer and reported as a secondary
  replication.

Verdicts and corrections as e1: the Paper 3 claim rule, BH per contrast type per
model, NULL margin 0.25 at n = 90.

## Power, from the offline validator

Claim rule at 0.01, base delivery 0.10, n = 90: 0.88 for a 0.20 need benefit,
0.64 for 0.15. e0's deaf need benefits were +0.15 to +0.24; e0's H2 sizes were
about +0.30, where power is near 1.

## Known limitations

- The text-route lexicon is conservative ("contact them by email" counts, "send
  them an email" does not), as in e1. It undercounts additions in every cell and
  makes H2 harder to confirm.
- Questions are written so that phoning is the default; base rates are not
  estimates of general use.
- One wrapper.
