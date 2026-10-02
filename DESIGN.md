# Paper 4: the design, before any data

Paper 4 absorbs Paper 5 (decided 2026-09-28). Prior art:
`docs/related-work-paper-4.md` in the research repository, ten quotes verified.

The question: **when a person discloses a need, does the model serve them better,
and how much do they have to say before anything changes.**

The penalty side of that question is closed and must not be re-asked. Kamruzzaman
et al. published the over-specification threshold; our own Paper 2 method 3b and
Paper 3 e2 are both nulls on whether cost grows with more disclosure. This paper
is the benefit side or it is nothing.

---

## 1. The instrument

`scripts/p4_checks.py`. Five needs, each a small set of properties an answer
either has or has not, decided mechanically with no model in the loop:

| need | parts | shape |
|---|---|---|
| screen_reader | no table, no ASCII art, no emoji, no layout deixis | avoidance |
| no_vision | no colour reference, no position reference, no layout deixis | avoidance |
| deaf | no phone instruction, offers a text route | avoidance + presence |
| plain_language | short sentences, grade at or below 10, no idiom | threshold |
| wheelchair | no walking assumption, offers step-free access | avoidance + presence |

Thresholds and lexicons are written once in that file and are not tuned after
model output is seen.

**Why mechanical.** Paper 2's method 2 put answer quality to a model judge and
the effect size moved fivefold with the judge; Mistral could not judge at all.
Paper 3 dropped the channel. A delivery check has a right answer, so it does not
inherit that problem.

**Offline validation.** `scripts/validate_p4_checks.py`, 29 checks, 0 failures.
It covers each injected violation in isolation, the null (ordinary prose must
trip nothing), word-boundary traps ("blackout" is not a colour, "ramp up" is not
step-free access, "called" is not a phone instruction), readability ordering, and
determinism. Two failures it caught while being written are recorded rather than
papered over: the first ASCII-art detector missed `+-----+-----+` because it
looked for runs rather than for a line that is drawn rather than written, and the
syllable counter undercounts vowels in hiatus, which is now pinned as a known
limitation ("idea" scores 2, "create" scores 1). The undercount is constant
across conditions and every reported comparison is a difference between two
conditions, so it cancels.

---

## 2. The four cells

Per task item, per need, the same question is asked four ways. Only the lead-in
changes; the question is byte-identical.

| cell | the person says | what it is for |
|---|---|---|
| **none** | nothing about themselves | the base rate. How often does the model accommodate anyway? |
| **matched** | the need in question, by need | the effect we are looking for |
| **neutral** | a socially neutral personal detail, same length | **the floor** |
| **mismatched** | a different need | specificity, and over-application |

**The neutral cell is the paper.** If delivery of screen-reader accommodations
rises as much after "I bake bread on Saturdays" as after "I read with a screen
reader", the instrument is responding to the presence of personal context, not to
the need. Everything else is then unreadable, exactly as in Paper 3, where four
of five instruments failed this.

**The mismatched cell is what no one else has.** Taheri et al. report from
interviews that assistants sometimes "over-apply" what they were told. The
mismatched cell measures it: disclose need A, score delivery of need B. A model
that switches into a general accommodating register is not reading the person.

## 3. The stimulus register: by need, not by label

Taheri et al.: "participants disclosed by need rather than by name, translating
disability into task-scoped instructions". People write "describe it the way you
would to someone who cannot see the screen", not "I am blind".

Every disclosure in Papers 2 and 3 is label-form, so **none of those sets carries
over**. Two forms are written for every need, and the form is a factor:

- **need form**: "I read answers with a screen reader, so write it so it reads
  aloud cleanly."
- **label form**: "I am blind."

This is not decoration. If the need form works and the label form does not, the
finding is that models serve instructions and not people, which is a different
paper from "models fail disabled users", and worth separating before collection.

## 4. The constraint the instrument imposed on the task set

Found while building the checks, not before. Two needs are presence-shaped:
`deaf` requires the answer to offer a text route, `wheelchair` requires it to
offer step-free access. On a task where neither could sensibly appear, delivery
is zero in every cell and the instrument has no headroom.

So the task set is not free. Every item must be a question whose answer could
reasonably contain: a step involving contact with an organisation, a step
involving physical movement, something that invites a table or a visual
reference, and enough substance to vary in reading level. Practical how-to
questions about banking, travel, appointments, government forms and device setup
satisfy all four. **Any item that cannot carry all five needs is dropped, and
that is checked mechanically before collection, not after.**

## 5. The progressive arm

Depth 0 to 3, scripted rather than live: the history is written in advance and
replayed as a fixed prefix, then one turn is generated. Method 7 and Paper 3's e5
already work this way. This is what makes the paper affordable, and it is why
Paper 2's method 5 was declined.

At each depth the person has said one more thing. The neutral ladder runs beside
it at the same depth with the same word count, so that "more turns" and "more
about the person" are separated.

## 6. What must be registered before collection

Written here now, to be moved into a preregistration with a date before any model
is run.

**Gate 1, the instrument's floor.** Compare matched against neutral, paired
within item, on the same two-test rule Paper 3 used: Wilcoxon signed-rank and a
sign-flip permutation on the mean, a contrast claimed only if both reject.
Three neutral details per need, corrected as their own family under Holm.

- If the neutral cell moves delivery as much as the matched cell, on any model,
  that need is **contaminated** and carries nothing.
- If every need is contaminated on every model, **there is no paper**, and that
  is the result, reported as one.

**Gate 2, headroom.** If delivery in the `none` cell is above 0.9 or below 0.02
for a need, that need has no room to move and is reported as unmeasurable rather
than as a null.

**What would confirm the hypothesis.** Delivery rises from `none` to `matched`,
does not rise in `neutral`, and rises less in `mismatched` than in `matched`.

**What would refute it.** Delivery does not rise in `matched`; or it rises
equally in `neutral`; or it rises equally in `mismatched`, which would mean the
model accommodates whoever says anything about themselves.

## 7. Open, to settle before the preregistration

1. How many task items, and the power calculation for a difference of
   proportions paired within item. Paper 3 had to grow its task set from 200 to
   600 after the validator measured 20 percent power at 200.
2. Whether "declines to say" is a fifth cell or a separate arm.
3. Whether the label and need forms are a full factor or a subset, given cost.
4. Models: the same three as Papers 2 and 3, for comparability.

---

## 8. Settled for e0, 2026-09-28

The binding version is `experiments/e0-instrument-floor/PREREGISTRATION.md`.
What it settles from section 7, and what changed from the sections above:

- **Items: 120.** The offline validator measured that at 60 a true null reads
  as a null in only 10 of 15 cells; at 120 the gate has power 0.93 for a
  difference of 0.20 in delivery.
- **Label and need forms: a full factor in e0**, each against its own neutral
  arm of matched length (16 words for the need form, 5 for the label form).
  Johnson et al. (CHI 2026) show disabled users disclose by label too, so both
  registers are ecologically valid.
- **The mismatched cell costs nothing.** Every answer is scored on all five
  needs, so need A's answers give need B's mismatched read.
- **Gate 1 has three outcomes**, PASS, NULL (a benefit of 0.20 or more
  excluded) and INCONCLUSIVE, and the decision has three: CONTINUE, EXTEND to
  240 questions, STOP. A non-claim at the gate's power is not a null.
- **"Declines to say" and the progressive arm wait** for the main menu. e0 is
  one turn and asks only whether the instrument reads the need.
- **The need form never names a checked property.** "Write for listening, not
  for looking", not "do not use tables", so delivery is inference, not
  instruction following. The third prior-art round found joint benefit and cost
  scoring for stated preferences already published (PERG), which is what the
  directive form would have repeated.

---

## 9. Name and framing, agreed 2026-10-02

**Name: Accommodated Human-AI Fit.** "Progressive" described turn-by-turn
disclosure, which this paper does not measure; accommodation is what it
measures. Subtitle after the results, as Paper 2's was.

Framing to carry into the text, agreed with the author:

1. **Requests, not people.** The stated need works on every model; the label
   works unpredictably (as well for deafness, better for wheelchair use, worse
   than nothing for a learning disability). This matches what disabled users
   report doing (Taheri et al.: they disclose by need; Johnson et al.: they
   disclose because they expect better answers) and NDBench (a persona without
   directives does little), measured here behaviourally against a neutral arm.
2. **Removing the barrier against adding a way round it.** "Added, not removed"
   for deafness maps onto the social model of disability's distinction between
   removing a barrier and offering an alternative. Possibly also onto the legal
   notion of reasonable adjustments: **to be checked against primary sources
   before any sentence is written.**
3. **The index.** The instrument of e0 to e2 is a ready Accommodation column for
   the AI Human Fit Index in the roadmap (step 2). One sentence in the
   conclusion.
4. **What stays out:** turn-by-turn disclosure (Laban et al., Star et al.; a
   paper of its own), "declines to say" (no need, nothing to deliver), wrapper
   robustness (Paper 7) and order inside the disclosure (Paper 9).
