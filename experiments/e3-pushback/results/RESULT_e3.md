# RESULT e3: saying it again, and naming the barrier

Collected 2026-10-03 to 06 with e4 in one session per model. 630 follow-ups per
model, complete: no duplicates, no missing jobs, no empty answers, no template
leakage, smoke check `SMOKE OK` on all three. Consoles are filed under this
experiment's outputs as `e34_<model>_*`.

Registered analysis: `analyse_e3_output.txt`.

---

## 1. The registered read

Primary set: first turns that kept a phone instruction after "I cannot hear"
(Qwen 59, Llama 37, Mistral 65). All three are tests.

| | qwen | llama | mistral | read |
|---|---|---|---|---|
| H4 restating the need removes more than asking again | +0.05 | **+0.49** | **+0.23** | **CONFIRMED**, 2 of 3 |
| H5 naming the barrier removes more than restating | **+0.46** | **+0.22** | **+0.49** | **CONFIRMED**, 3 of 3 |

## 2. How much of the phone instruction is left

Share of follow-up answers that still tell the person to phone, among first turns
that kept it:

| follow-up | qwen | llama | mistral |
|---|---|---|---|
| "Thanks for that. Could you go over it once more, step by step, please?" | 0.58 | 0.76 | 0.95 |
| "As I said, I cannot hear. Could you go over it once more, please?" | 0.53 | 0.27 | 0.72 |
| "I cannot hear; phone calls will not work for me. Please repeat the steps." | 0.07 | 0.05 | 0.23 |

Told a second time that the person cannot hear, Mistral still tells them to phone
in 72 percent of these answers and Qwen in 53 percent. Only when the person says
in so many words that phone calls will not work does the instruction mostly go
(5 to 23 percent left).

## 3. Reading it

- The pattern of e0 to e2 holds in a second turn: models act on an explicit
  request (do not phone) far more than on a stated fact about the person (cannot
  hear), even when the fact makes the request obvious and has just been repeated.
- The burden of translating the need into an instruction falls on the person.
  That is what Taheri et al.'s participants describe doing; e3 measures why they
  have to.
- A neutral retry is not a fix: it leaves 58 to 95 percent of phone
  instructions in place.

## 4. Limits

- Follow-up answers are long and often hit the 400-token cap (55 to 82 percent);
  every answer is read through the same 250-word window, as registered, so the
  comparison between follow-ups is like for like.
- The first turns differ by model, since each model replies to its own answer.
- The text-route lexicon is conservative, as before.
