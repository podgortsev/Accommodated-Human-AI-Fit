# What this study found, in plain language

## The question

You ask an AI assistant how to cancel your broadband contract, and you mention
first that you cannot hear. A good answer gives you a way to do it without a
phone call.

Does the assistant give you that answer? And does it give it because of what you
said, or just because you said something about yourself?

## How we tested it

We asked three freely available AI models hundreds of everyday questions:
replacing a passport, booking a GP appointment, reporting a power cut. Each
question was asked many times. Sometimes the person said nothing about
themselves. Sometimes they said what they needed ("I cannot hear, so any step
that needs sound or speaking will not work for me"). Sometimes they gave a label
("I am Deaf"). And sometimes they said something ordinary of exactly the same
length ("I bake bread most Saturday mornings").

That last version is the important one. If the answer improves as much after
the sentence about bread as after the sentence about hearing, the model is not
responding to the need at all. Most earlier studies compared "said the need"
with "said nothing", which cannot tell these apart.

A computer program, not another AI, checked every answer: did it tell a Deaf
person to phone, did it offer email or chat, did it assume a wheelchair user
could take the stairs, was it written in short, plain sentences.

## What we found

**Saying what you need works.** For deafness, wheelchair use and difficulty
reading, all three models gave more suitable answers after the need was stated,
and not after the sentence about bread.

**But for deafness the model adds, it does not replace.** Told that the person
cannot hear, the models started offering email or chat in about half their
answers. Yet between half and four fifths of the instructions to phone stayed in.
The answer said "you can email them", and also "call this number".

**Saying it twice is not always enough.** When the person replied "As I said, I
cannot hear", one model still told them to phone in 72 percent of those answers.
Only "phone calls will not work for me", spelling out the barrier, removed it on
all three models.

**How you say it matters, and not in a predictable way.** "I am a wheelchair
user" worked better than describing the need. "I am Deaf" worked about as well.
"I have a learning disability" made the answers harder to read than the sentence
about bread, and one model refused to explain ordinary things, such as how to
pay in a cheque, in up to a third of cases.

**Stating a need does not make the model worse at the rest of your task**, on
the whole. One model became more likely to ignore the format it had been asked to
use.

## What this does not show

- We tested three small, free models, not the large commercial ones.
- We could not test what blind people using screen readers get: these models
  already answer in a format that suits screen readers, so there was nothing to
  change.
- A program checked the answers, not people. It counts phone instructions and
  sentence lengths; it does not judge whether an answer is good.
- The refusal finding was noticed after the experiments were designed, so it is
  reported as something to test, not as a proven result.

## Why it matters

Disabled people say they tell AI assistants about their disability because they
expect better answers. This study shows they are partly right: the answers do
change. It also shows the work of getting a usable answer still falls on them. To
be sure the model will not send a Deaf person to the phone, they have to say, in
so many words, that the phone will not work.
