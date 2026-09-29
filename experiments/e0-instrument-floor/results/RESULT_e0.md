# RESULT e0: the instrument floor

Collected 2026-09-28 to 29, three models, 2,040 answers each, all complete: no
duplicates, no missing cells, prompts match the stimuli byte for byte, no empty
answers, no chat-template leakage. GPU smoke check `SMOKE OK` on all three.

Registered analysis: `analyse_e0_output.txt`. Post hoc checks, not
preregistered: `sensitivity_e0_output.txt` (script `scripts/sensitivity_e0.py`).

---

## 1. The registered decision: CONTINUE

| need | qwen | llama | mistral |
|---|---|---|---|
| screen_reader | UNMEASURABLE (none 1.00) | UNMEASURABLE (0.99) | UNMEASURABLE (1.00) |
| no_vision | UNMEASURABLE (0.98) | UNMEASURABLE (0.97) | UNMEASURABLE (0.97) |
| deaf | **PASS** +0.22 | **PASS** +0.24 | **PASS** +0.15 |
| plain_language | **PASS** +0.58 | **PASS** +0.37 | NULL, reversed: -0.23 |
| wheelchair | UNMEASURABLE (0.00) | UNMEASURABLE (0.00) | UNMEASURABLE (0.00) |

Need benefit = delivery under the need form minus delivery under a neutral
detail of the same length, paired within question. Two needs pass on Qwen and
Llama, one on Mistral: CONTINUE by the registered rule (two needs on two models).

## 2. What the registered result does NOT say, stated first

- **Three of five needs could not be measured.** On these how-to questions the
  models never produce tables, emoji, colour or position references in the first
  place (screen_reader, no_vision at the ceiling), and never offer step-free
  access unprompted (wheelchair at the floor). Gate 2 did its job. This is a
  property of the task set and the checks, not evidence that models serve blind
  or wheelchair users well or badly. DESIGN.md section 4 anticipated the
  wheelchair case; the ceiling on the visual needs was not anticipated.
- **The Mistral plain-language reversal is an instrument artefact.** See 4.2.
- **Wrappers.** One wrapper only, as registered.

## 3. The findings

### 3.1 The floor is clean: a neutral detail does not buy accommodation

Neutral detail against saying nothing: no detail moves delivery for any need on
Qwen or Mistral; one of six details moves plain_language on Llama (+0.10). The
"any person" effect PrefEval predicted is essentially absent for delivery. So
the benefit read against the neutral arm and the benefit read against nothing
are nearly the same here, and the neutral arm is what licenses saying the need
caused it.

### 3.2 Deaf: the model adds a text route and keeps telling you to phone

Robust on all three models, in the registered read and in both post hoc checks
(+0.15 to +0.24 need benefit; specificity claimed on all three, so it is not a
general accommodating register). The label form ("I am Deaf") works as well as
the need form on Qwen and Mistral, less on Llama (+0.09).

The parts show what the benefit is made of (exploratory, paired against the
neutral arm):

| model | offers a text route, need vs neutral | no phone instruction, need vs neutral |
|---|---|---|
| qwen | +0.32 [+0.23, +0.41] | -0.03 [-0.12, +0.05] |
| llama | +0.29 [+0.20, +0.39] | +0.06 [-0.02, +0.14] |
| mistral | +0.28 [+0.19, +0.37] | -0.05 [-0.15, +0.04] |

After "I cannot hear, so any step that needs sound or speaking will not work for
me", 18 to 35 percent of answers still tell the person to call, no fewer than
after a sentence about baking bread. Checked by hand against the matched
contexts: these are real instructions ("call the customer service number
provided on your policy"), and at most two answers per model per cell carry the
phrase only next to a negation. One begins "although you mentioned you cannot
hear" and goes on to recommend the hotline. **The accommodation is added; the
barrier is not removed.** Delivery of the whole need, text route and no phone,
peaks at 0.23 to 0.33.

### 3.3 Plain language: served when asked for, not when the person is named

Need form: large benefit on Qwen (+0.58) and Llama (+0.37). Label form ("I have
a learning disability"): no benefit on any model, point estimates negative
(-0.09 to -0.22), in every read. Taheri et al. report that people disclose by
need; this is the model-side counterpart: for reading difficulty the model
responds to the instruction and not to the identity. Deaf is the contrast case,
where the label works.

### 3.4 Wheelchair, below the gate

Unmeasurable by the registered rule (step-free access offered in 0 of 120
`none` answers on every model). Reported descriptively only: stating the need
raises it to 3 to 11 percent. On Llama the label ("I am a wheelchair user")
raises it more than the need form (0.17 against 0.05).

## 4. Post hoc checks, not preregistered

### 4.1 Window: truncation differs by cell

Answers hit the 400-token cap at different rates by cell (Llama: need 0.40,
label 0.81, none 0.82). Scoring every answer on its first 200 words only leaves
every registered verdict unchanged. Deaf need benefit +0.16 to +0.21.

### 4.2 Lines: the plain-language splitter

The registered splitter ends sentences at . ! ? only, so markdown list items
without a full stop merge into one "sentence". With lines as boundaries too:

| model | registered | line-aware |
|---|---|---|
| qwen | +0.58 | +0.32 |
| llama | +0.37 | +0.28 |
| mistral | **-0.23** | **+0.21** |

The Mistral reversal disappears: Mistral answers a stated reading difficulty with
more list items, which the registered check read as longer sentences. Under the
line-aware check plain_language passes on all three models and the decision is
CONTINUE with three models. The registered verdict stands as the registered
verdict; the paper reports both and says which one is the artefact.

## 5. What this means for Paper 4

- The instrument reads the need, not the presence of a person, for the two needs
  it can measure. Paper 4 continues.
- The headline candidate is 3.2: told that a person cannot hear, all three
  models add a text route and none removes the phone instruction.
- The second is 3.3: for reading difficulty the label buys nothing and the
  stated need buys a lot.
- Before any follow-up: the task set needs items where visual layout and
  step-free access are natural, or those three needs stay unmeasurable. And the
  plain-language check needs the line-aware splitter, registered before use.
