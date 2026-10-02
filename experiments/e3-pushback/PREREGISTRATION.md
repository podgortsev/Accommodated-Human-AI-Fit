# e3 preregistration: can a Deaf person get the phone instruction removed by saying so again?

Registered 2026-10-02, after e2 and before any e3 generation. Committed with the
scripts it describes. A change after the first generation is reported as a
deviation next to the result.

---

## Why e3 exists

e2 confirmed, on all three models, that "I cannot hear" adds a text route while
56 to 82 percent of phone instructions remain. The research program assigns to
Paper 4 the question of whether a person can undo such a failure by objecting.
Lachenmaier et al. (2026) study repair for arithmetic; nobody has studied it for
a disclosed need.

## Design

- **First turn:** each model's own answer to the need form ("I cannot hear, so
  any step that needs sound or speaking will not work for me") from e0 (120
  questions) and e2 (90), replayed verbatim, never regenerated.
- **Follow-up, one of three, 14 words each** (`scripts/build_e3_jobs.py`):
  - neutral: "Thanks for that. Could you go over it once more, step by step, please?"
  - restate: "As I said, I cannot hear. Could you go over it once more, please?"
  - specific: "I cannot hear; phone calls will not work for me. Please repeat the steps."
- 630 generations per model; models, decoding and limits as e0 to e2.
- **Outcome:** a phone instruction in the follow-up answer, and a text route,
  by instrument version 2 with the 250-word window.

## The primary set and the measure

The first turns that kept a phone instruction (same check): Qwen 59, Llama 37,
Mistral 65, counted from the committed e0 and e2 outputs. Removal is measured
where there is something to remove: removed = 1 if the follow-up carries no phone
instruction, compared paired within the first turn. This replaces the
absolute-points form that misled the wheelchair reading in e1 (RESULT_e1,
section 3.1, corrected).

## Hypotheses

- **H4, restating the need removes more than asking again:** removed(restate)
  minus removed(neutral), predicted positive.
- **H5, naming the barrier removes more than restating the need:**
  removed(specific) minus removed(restate), predicted positive. From e0 to e2:
  models serve explicit requests more than stated identities.

The Paper 3 claim rule; one family per contrast per model. **Confirmed** if
claimed positive on at least two models. A model with fewer than 10 first turns
in the primary set is NOT A TEST (none is, on the counts above).

Reported beside them, not tested: the share of phone instructions left after each
follow-up, text route rates, and the same on all 210 first turns, including
whether a neutral retry introduces phone instructions where the first turn had
none.

## Power

Paired binary at n = 37 to 65: the offline validator's minimum detectable
difference is about 0.16 to 0.19. A smaller effect is reported with its interval,
not as absent.

## Known limitations

- The neutral follow-up is a retry, so its removal rate is the floor for
  "asking again", not zero.
- The text-route lexicon is conservative, as in e1 and e2.
- One wrapper. First turns differ by model, because each model replies to its own
  answer.
