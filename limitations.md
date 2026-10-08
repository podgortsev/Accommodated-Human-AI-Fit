# Limitations

What this study cannot claim, in one place. Each experiment's `RESULT_*.md` and
`PREREGISTRATION.md` carry their own limits in more detail.

## Models and setting

- **Three open models of 7 to 8 billion parameters, at 4-bit, greedy decoding.**
  Commercial frontier models format answers differently (they draw tables and use
  emoji), so the screen-reader null would very likely not hold for them, and none
  of the effect sizes should be assumed to transfer.
- **One user turn, no system prompt**, except e3, which replays a fixed first
  turn. Turn-by-turn disclosure across a conversation was not tested.
- **English only**, and questions written with a UK framing (councils, GP
  surgeries, the DVLA-style licensing agency).

## The instrument

- **Lexical checks.** Delivery is decided by word lists and counts, not by
  judgement. A phone instruction phrased in words outside the list is missed; a
  listed phrase used in a negative sense would be counted (checked by hand for
  deafness: at most two answers per model per cell).
- **The text-route list is conservative.** "Contact them by email" counts, "send
  them an email" does not. This undercounts additions in every cell, which makes
  "added, not substituted" harder to show, not easier.
- **Readability.** The syllable counter undercounts vowels in hiatus; the bias is
  the same in every cell and cancels in every contrast.
- **A 250-word window** (from e1 on) equalises what is read across cells whose
  answers are cut by the token cap at different rates; anything after word 250 is
  not scored.
- **No human judgement.** We did not ask disabled people which answers they would
  prefer. The checks measure specific, named properties.

## Design

- **Wrappers.** Only the deafness headline was tested under several wrappers
  (e5); the wrapper moved its size by up to a quarter of the scale. Every other
  figure is from one wrapper and should be read with that spread in mind.
- **Question pools were written to make each need arise.** Base rates are
  therefore not estimates of how often models fail these needs in ordinary use.
- **Screen reader and no vision share a check** (layout references), so their
  specificity is low by construction.
- **e4's calculation sits between the need and the question**, which may dilute
  the need; the deafness benefit shrank there, and the two explanations cannot be
  separated.

## Statistics

- **The 60-question pools (e1) resolve a benefit of about 0.25.** Smaller effects
  there are inconclusive, not absent. No vision is in this position.
- **One family per contrast type per model** for Benjamini-Hochberg; a reader who
  prefers one family across everything will find fewer claims.
- **Hypothesis H2 compares absolute changes.** For a rare barrier this lets a large
  addition outweigh a near-total removal; the wheelchair reading was corrected for
  exactly this reason, and the deafness result is also reported as the share of
  the barrier left.

## Process

- **Errors found and corrected during the work**, each reported where it occurs:
  the plain-language sentence splitter (e0), the deafness item set (e1), the
  wheelchair interpretation (e1), and the wording of one quoted example (e0).
- **Refusals were counted after the fact.** That analysis is exploratory.
- **The preregistrations were committed to a private repository** and made public
  at release. A private history can be rewritten, so the registrations prove less
  than a public timestamp would; the history supports "committed before the
  results", and nothing more is claimed.
- **The legal framing first intended was dropped** when the statute did not
  support it.
