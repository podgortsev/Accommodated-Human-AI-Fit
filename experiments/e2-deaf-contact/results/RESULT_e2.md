# RESULT e2: the deaf need, tested where it arises

Collected 2026-10-01 to 02, three models, 1,530 answers each. Every file
complete: no duplicates, no missing cells, prompts match the stimuli, no empty
answers, no template leakage, smoke check `SMOKE OK` on all three.

Registered analysis: `analyse_e2_output.txt`. (Its per-model headers read
"e1 |" because e2 calls e1's analysis function unchanged; the numbers are e2's.)

---

## 1. The registered read

All three models pass the relevance check: a phone instruction appears in 0.26
(Qwen, Mistral) and 0.43 (Llama) of baseline answers. All three are tests.

| | qwen | llama | mistral | read |
|---|---|---|---|---|
| deaf need benefit | **PASS** +0.39 | **PASS** +0.43 | **PASS** +0.26 | **FINDING** on 3 of 3 |
| H2 added not removed | +0.46 | +0.36 | +0.23 | **CONFIRMED** on 3 of 3 |
| plain language (secondary) | PASS +0.32 | PASS +0.37 | PASS +0.26 | replicated |
| H3 need over label (secondary) | +0.41 | +0.40 | +0.22 | claimed on 3 |

## 2. What the deaf benefit is made of

| model | text route offered, neutral to need | still told to phone, neutral to need |
|---|---|---|
| qwen | 0.10 to 0.62 | 0.35 to 0.29 |
| llama | 0.13 to 0.62 | 0.32 to 0.18 |
| mistral | 0.18 to 0.48 | 0.34 to 0.28 |

After "I cannot hear, so any step that needs sound or speaking will not work for
me", 18 to 29 percent of answers still tell the person to phone. The addition is
three to six times the removal on every model. Llama is the only model whose
removal is distinguishable from zero (+0.14, descriptive), and its addition is
still +0.50.

The label ("I am Deaf") also works, less than the need form on Llama and Mistral
and close to it on Qwen (+0.19, +0.23, +0.30).

## 3. Floors

4 of 36 floor tests move, on two models. Qwen, plain language: three of six
neutral details make answers plainer than saying nothing (mean +0.20).
Mistral, deaf: one detail lowers delivery (-0.09). Both are subtracted by
design, since every benefit is read against the neutral arm, and both are
reported. Across e0, e1 and e2 a neutral detail has moved delivery in 5 of 198
floor tests.

## 4. What this settles for Paper 4

- **Added, not removed** is registered and confirmed for deaf on all three
  models, on questions written for it, after first appearing as an exploratory
  result in e0. 56 to 82 percent of the phone instructions remain once the
  person has said they cannot hear.
- It is not a two-need result. H2 is also claimed for wheelchair (e1), but there
  the walking barrier is rare at baseline and mostly removed (13 to 27 percent
  left); H2's absolute-points form let a large addition outweigh a near-total
  removal. Corrected 2026-10-02, see RESULT_e1.md section 3.1. A first version
  of this file said two needs.
- The deaf benefit replicates on new questions at a larger size than e0 (+0.26
  to +0.43 against +0.15 to +0.24), on questions where contacting someone is the
  point.
- Plain language replicates a third time with the corrected splitter, and the
  need form beats the label on every model in e1 and e2.
- The "any person" effect is not zero everywhere: Qwen writes more plainly for
  anyone who mentions anything about themselves. The neutral arm is what keeps
  that out of the benefit.
