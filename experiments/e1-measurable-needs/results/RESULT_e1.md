# RESULT e1: the needs e0 could not measure

Collected 2026-09-29 to 10-01, three models. Phase 1 (`none`, 180 questions)
then the pool gate, then phase 2. Every file complete: 2,100 rows per model as
the gate implies, no duplicates, no missing cells, prompts match the stimuli,
no empty answers, no template leakage, smoke check `SMOKE OK` on all three.

Registered analysis: `analyse_e1_output.txt`. Instrument version 2, every
answer read through its first 250 words.

---

## 1. The registered read

| need | qwen | llama | mistral | read |
|---|---|---|---|---|
| screen_reader | UNMEASURABLE (none 1.00) | UNMEASURABLE (1.00) | UNMEASURABLE (0.98) | pool dropped at gate 2 |
| no_vision | INCONCLUSIVE +0.13 | NULL +0.13 | **PASS** +0.17 | not a finding |
| deaf | NULL +0.01 | NULL +0.02 | NULL +0.01 | not a finding, and not a test: see 2.1 |
| plain_language | **PASS** +0.10 | **PASS** +0.09 | **PASS** +0.09 | **FINDING** |
| wheelchair | **PASS** +0.66 | **PASS** +0.61 | **PASS** +0.43 | **FINDING** |

| hypothesis | qwen | llama | mistral | read |
|---|---|---|---|---|
| H2 added not removed, wheelchair | +0.58 | +0.48 | +0.32 | **CONFIRMED** on 3 |
| H2 added not removed, deaf | +0.02 | -0.02 | +0.02 | not confirmed, and not a test: see 2.1 |
| H3 need over label, plain language | +0.17 | +0.33 | +0.27 | **CONFIRMED** on 3 |

Floors: no neutral detail moves delivery for any need on any model (0 of 72).

## 2. What it does not say, first

### 2.1 The deaf replication was mis-specified. My error.

The preregistration put deaf on all 180 e1 questions. They are device screens and
travel routes, and almost none involves contacting an organisation: a phone
instruction appears in 1 to 2 percent of `none` answers here, against 19 to 26
percent on e0's questions. With no barrier to remove and no contact to route by
text, deaf delivery is near zero in every cell. The registered verdict is NULL
and it stands as registered, but it is not evidence against e0's deaf result. It
says the deaf need was tested where it does not arise. The deaf evidence in
Paper 4 is e0's, and e0's add-not-remove decomposition stays exploratory.

### 2.2 Screen reader cannot be measured on these models with this instrument

Even on comparisons, schedules and templates written to invite tables, the three
models drew no tables and used no emoji: one table in 180 `none` answers, in
Mistral. They format comparisons as nested lists. The instrument's
screen_reader parts (table, ASCII art, emoji, layout deixis) therefore never
vary on open 7B models. This is a property of these models' formatting, not
evidence about how they serve screen-reader users; nested lists, which these
models use instead, are not scored.

### 2.3 no_vision sits on the margin

Point estimates +0.13, +0.13, +0.17. One model claims; the other two miss the
claim rule by a hair, one of them with an upper bound of 0.245 against a NULL
margin of 0.25, so it is labelled NULL by the registered rule while its point
estimate is the same as Qwen's INCONCLUSIVE. Read: a benefit of about 0.13 is
plausible, a benefit of 0.25 or more is excluded on two models. The 60-question
pool was powered for 0.25 (power 0.79), not for 0.13.

## 3. The findings

### 3.1 Wheelchair: the step-free route is added, the walking stays

Large and on all three models: stating "I cannot walk or use stairs" raises
delivery from about 0.05 to 0.48 to 0.67. H2 confirmed on all three, by a wide
margin. The parts:

| model | offers step-free access, need vs neutral | no walking assumption, need vs neutral |
|---|---|---|
| qwen | +0.67 | +0.09 |
| llama | +0.59 | +0.11 |
| mistral | +0.41 | +0.09 |

The model adds a lift, a ramp or an accessible entrance, and keeps telling the
person to walk to it, at nearly the rate it does for a person who mentioned
baking bread. This is the e0 deaf pattern, registered in advance this time, on a
different need, on different questions, confirmed on every model.

And the label beats the need: "I am a wheelchair user" (5 words) delivers more
than the 16-word functional statement on Llama (0.82 against 0.67) and Mistral
(0.62 against 0.48), and the same on Qwen (0.67).

### 3.2 Plain language: the label makes answers harder to read

With the line-aware splitter, plain-language delivery is high at baseline (0.77
to 0.88), so the need benefit is small but claimed on all three (+0.09 to +0.10).
H3 is confirmed on all three, and the label does worse than nothing: "I have a
learning disability" lowers delivery below the neutral arm on all three models
(-0.23 Llama and -0.17 Mistral, both claimed; -0.09 Qwen, not claimed after
correction). Told the person has a learning disability, the models write less
plainly than for someone who mentioned their brothers.

### 3.3 The floor holds

0 of 72 floor tests move. Across e0 and e1, a socially neutral personal detail
has moved delivery in 1 of 162 tests. The benefit is the need, not the presence
of a person.

## 4. Across e0 and e1, what Paper 4 can claim

1. Stating a need buys accommodation that a neutral personal detail of the same
   length does not, for deaf (e0, three models), plain language (e0 and e1,
   three models with the corrected splitter) and wheelchair (e1, three models).
2. **The accommodation is added; the barrier is not removed.** Registered and
   confirmed for wheelchair on all three models; exploratory for deaf in e0 on all
   three.
3. Whether the label or the need works better depends on the need: the label
   works as well for deafness, better for wheelchair use, and actively worse for
   learning disability.
4. A neutral personal detail does not move delivery (1 of 162 floor tests).

What it cannot claim: anything about screen-reader users (unmeasurable on these
models); a no-vision benefit (about +0.13, not established); a deaf result on e1's
questions (not tested there, my error).
