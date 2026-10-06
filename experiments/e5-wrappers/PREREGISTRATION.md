# e5 preregistration: the deafness headline under other wrappers

Registered 2026-10-06, before any e5 generation. Committed with its scripts.

## Why

The methodology checklist requires several neutral wrappers: in Paper 2 six
arbitrary openings moved baselines by 2 to 5 points. e0 to e4 used one wrapper
(lead-in, one space, question). The checklist also asks for position to be
counterbalanced. e5 re-tests the paper's headline, e2's deafness result, under
two further wrappers.

## Design

e2's 90 contact questions; the four cells the headline rests on (the deafness
need form and the three 16-word neutral details); two wrappers:

- **opener**: "Quick question for you." before the lead-in (a neutral opening,
  as in Paper 2's method 3c);
- **after**: the question first, the lead-in after it.

720 generations per model; models, decoding and instrument (v2, 250 words) as
e2. The original wrapper is e2's committed answers.

## Registered read

Per model and wrapper: the deafness need benefit and H2 (text route added minus
phone instruction removed), each against the neutral mean, paired within
question, under the Paper 3 claim rule. The headline **holds** under a wrapper if
both are claimed positive on at least two models. The spread of each estimate
across the three wrappers is reported as the error bar the checklist asks for.

Validated offline: `scripts/validate_e5.py`, 9 checks, 0 failures.
