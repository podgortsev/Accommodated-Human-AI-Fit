# RESULT e4: what the accommodation costs

Collected 2026-10-03 to 06 with e3 in one session per model. 2,310 answers per
model, complete: no duplicates, no missing jobs, no empty answers, no template
leakage.

Registered analysis: `analyse_e4_output.txt`.

---

## 1. The registered read: H6 not confirmed, and the models disagree

| model | pooled penalty (need minus neutral) | registered verdict |
|---|---|---|
| qwen | +0.013 [-0.009, +0.035] | NO PENALTY LARGER THAN 5 POINTS |
| llama | +0.060 [+0.035, +0.087] | REVERSED |
| mistral | -0.057 [-0.100, -0.014] | PENALTY, on 117 complete questions |

H6, a disclosure penalty on two models, is **not confirmed**. Stating a need
does not consistently cost accuracy on the person's own task.

## 2. What sits under each verdict

**Qwen.** Accuracy 0.688 with no lead-in, 0.62 to 0.63 with any of the three
neutral details, 0.62 to 0.67 with a need. All three neutral floors move: on
Qwen, putting any 16-word sentence about yourself first costs about 6 points of
accuracy, and a stated need costs no more than that.

**Llama.** Accuracy 0.893 with no lead-in, 0.82 to 0.88 with a neutral detail,
0.90 to 0.92 with a need. Two of three floors move. The "reversal" is the neutral
details costing accuracy while the needs do not: against saying nothing, the
need forms are level. It is not that stating a need makes Llama better at
arithmetic.

**Mistral.** The cost appears as format, not accuracy. Mistral drops the
requested "Answer:" line in 13 to 28 percent of neutral answers and in 20 to 49
percent of need answers (format miss pooled +0.09, claimed); after "reading is
slow and hard for me" it drops it in half of all answers. Only 117 questions have
an Answer line in all seven cells, and on those the pooled penalty is -0.06.
Read as registered, this is a penalty; read with the format result beside it, it
is mostly a model that stops following the requested format when a need is
stated.

So the neutral arm matters here as much as anywhere in Paper 4: against saying
nothing, Qwen looks penalised by a need and Llama does not; against a neutral
detail of the same length, Qwen is level and Llama looks improved. Both readings
come from the same fact, that a 16-word sentence about the person moves accuracy
on two of three models by itself. This repeats Paper 2's finding that length
alone moves accuracy, and it is why Paper 2's penalty, read against a
signal-free floor, and this one, read against a matched neutral detail, are not
the same quantity.

## 3. Exploratory: the deaf accommodation shrinks when the task is busier

The delivery benefits, secondary here, hold for wheelchair (+0.23 to +0.41) and
plain language (+0.13 to +0.23) on all three models. The deaf benefit does not:
Qwen -0.01, Mistral +0.02, Llama +0.10, against +0.26 to +0.43 for the same
models in e2. Two explanations, not separable in these data: answers are shorter
with a calculation first (truncation 1 to 25 percent here against 23 to 47 in
e2), leaving less room for a contact route; and the need now sits further from
the question, with the calculation in between, which the methodology checklist
warns dilutes a signal. Reported, not claimed.

## 4. What this means for Paper 4

- The accommodation is not bought at the price of accuracy, on any model, once
  the comparison is a neutral detail of the same length: no penalty above 5 points
  on Qwen, none on Llama, and on Mistral a cost carried mainly by dropped format.
- The real cost on Mistral is compliance: state a need and it is likelier to
  ignore the format it was asked for. That is the refusal channel of Paper 6 in a
  new place, and it is counted separately, as the checklist requires.
- Length matters again: the neutral detail itself costs Qwen and Llama accuracy.
  The paper should report need against nothing and need against neutral side by
  side, as here, rather than either alone.
