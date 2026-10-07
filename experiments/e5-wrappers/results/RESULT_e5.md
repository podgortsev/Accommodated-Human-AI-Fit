# RESULT e5: the headline under three wrappers

Collected 2026-10-07, three models, 720 answers each, complete: no duplicates,
no missing jobs, no empty answers, no template leakage, smoke check `SMOKE OK`
on all three. The original wrapper is e2's committed answers.

Registered analysis: `analyse_e5_output.txt`.

## The registered read: HOLDS under every wrapper, on every model

| wrapper | need benefit (qwen / llama / mistral) | H2 added not removed (qwen / llama / mistral) |
|---|---|---|
| original (e2) | +0.39 / +0.43 / +0.26 | +0.46 / +0.36 / +0.23 |
| opener ("Quick question for you." first) | +0.23 / +0.49 / +0.14 | +0.32 / +0.31 / +0.30 |
| after (lead-in after the question) | +0.23 / +0.68 / +0.16 | +0.40 / +0.35 / +0.33 |

Every entry is claimed under the two-test rule. The headline holds on 3 of 3
models under each of the three wrappers.

## The error bar

The size moves with the wrapper, as the checklist expects: the deafness need
benefit spans +0.23 to +0.39 on Qwen, +0.43 to +0.68 on Llama and +0.14 to +0.26
on Mistral. H2 is steadier: +0.32 to +0.46, +0.31 to +0.36, +0.23 to +0.33.
Single-wrapper estimates in this paper carry a spread of up to a quarter of the
scale and are reported as a range, not a point.

## The removal side

Phone instructions removed after the need, against the neutral mean: Qwen +0.06,
+0.02, -0.01; Mistral +0.07, -0.03, -0.05; Llama +0.14, +0.19, +0.30. On Qwen and
Mistral, under the two new wrappers, stating "I cannot hear" removes no phone
instructions at all. Llama removes more when the need comes after the question,
and still adds far more than it removes.

## Checklist

The two items that waited on e5, several neutral wrappers and position, pass.
