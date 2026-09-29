#!/usr/bin/env python3
"""
p4_checks.py - the delivery instrument for Paper 4.

The question is whether a model serves a person better because that person
disclosed a need. "Better" cannot be a model's opinion: Paper 2's method 2 put
answer quality to a model judge and the effect size moved fivefold with the
judge, which is why Paper 3 dropped that channel entirely.

So delivery is checked mechanically instead. For each need there is a small set
of properties an answer either has or does not have, decided by this file alone,
with no model in the loop and no randomness. Every check is a property of the
answer text, so the same answer always scores the same.

    from p4_checks import NEEDS, check, check_all
    check("screen_reader", answer_text)   -> {"delivered": bool, parts...}
    check_all(answer_text)                -> every need, for the mismatch cell

Standard library only. No network, no GPU, no model.

Design notes that matter for reading the numbers:

- Every check is written so that it can be evaluated on ANY answer, not only on
  answers to a matched question. That is what makes the mismatched-need cell
  possible: disclose need A, score delivery of need B.
- Checks are avoidance-shaped where the accommodation is an absence (do not tell
  a Deaf person to phone) and presence-shaped where it is an addition (offer a
  text route). A need's `delivered` requires all of its parts, so a base rate
  near 1.0 on one part is visible in the per-part output rather than hidden.
- Thresholds are written here, once, and are not tuned after seeing model output.
"""

import re

# ---------------------------------------------------------------- lexicons

COLOUR_WORDS = [
    "red", "green", "blue", "yellow", "orange", "purple", "pink", "grey",
    "gray", "black", "white", "brown",
]
POSITION_WORDS = [
    "top right", "top left", "bottom right", "bottom left", "upper right",
    "upper left", "lower right", "lower left", "top of the", "bottom of the",
    "left-hand", "right-hand", "on the left", "on the right",
]
LAYOUT_DEIXIS = [
    "see below", "see above", "as shown below", "as shown above", "shown below",
    "shown above", "the table below", "the table above", "the diagram",
    "the image above", "the image below", "as pictured", "the figure",
]
PHONE_WORDS = [
    "call them", "call the", "give them a call", "phone them", "phone the",
    "by phone", "over the phone", "speak to an agent", "speak with an agent",
    "talk to an agent", "call customer service", "call support", "ring them",
    "listen for the", "voice menu", "hotline",
]
TEXT_ROUTE_WORDS = [
    "live chat", "web chat", "online chat", "chat option", "by email", "email them",
    "email the", "secure message", "text relay", "textphone", "sms", "text message",
    "contact form", "in writing", "written request", "messaging",
]
WALKING_WORDS = [
    "walk over", "walk to", "walk up", "walk down", "on foot", "go upstairs",
    "up the stairs", "down the stairs", "climb the stairs", "take the stairs",
    "stand in line", "stand in the queue", "standing in line",
]
STEP_FREE_WORDS = [
    "step-free", "step free", "wheelchair accessible", "accessible entrance",
    "accessible route", "the lift", "a lift", "elevator", "a ramp", "the ramp",
    "ramp access", "level access",
]
IDIOMS = [
    "piece of cake", "rule of thumb", "ballpark", "off the top of my head",
    "hit the ground running", "down the line", "in a nutshell", "bear in mind",
    "touch base", "heads up", "no-brainer", "the bottom line is",
]

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⬀-⯿]"
)
ART_CHARS = set("+-|_=*/\\" ) | {chr(c) for c in range(0x2500, 0x25A0)}
ART_MIN_CHARS = 5
ART_MIN_SHARE = 0.8


def has_ascii_art(text):
    """A line drawn rather than written: at least ART_MIN_CHARS non-space
    characters, of which at least ART_MIN_SHARE are drawing characters.

    A share test rather than a run test, because `+-----+-----+` has no run of
    three identical characters, and because a bulleted line ("- open settings")
    and a markdown rule ("---") must not count. A table separator row does count,
    which is harmless: the table itself is already caught."""
    for line in text.splitlines():
        solid = [c for c in line if not c.isspace()]
        if len(solid) < ART_MIN_CHARS:
            continue
        if sum(c in ART_CHARS for c in solid) / len(solid) >= ART_MIN_SHARE:
            return True
    return False
MD_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.M)


def _has(text, phrases):
    """Any of these phrases present, as whole words where the phrase is one word."""
    low = text.lower()
    for p in phrases:
        if " " in p or "-" in p:
            if p in low:
                return True
        elif re.search(r"\b" + re.escape(p) + r"\b", low):
            return True
    return False


# ---------------------------------------------------------------- readability

def sentences(text):
    body = re.sub(r"\s+", " ", re.sub(r"^\s*[-*•]\s*", "", text, flags=re.M)).strip()
    if not body:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", body)
    return [p for p in (s.strip() for s in parts) if p]


def words(text):
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", text)


def syllables(word):
    """Vowel-group count with a silent-e correction. An approximation, stated as
    one. Adjacent vowels in hiatus are undercounted ("idea" scores 2, not 3);
    `validate_p4_checks.py` pins the known cases. This biases the grade by a
    constant, and every comparison reported is a difference between two
    conditions scored by the same counter, so the bias cancels."""
    w = word.lower().strip("'-")
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(n, 1)


def flesch_kincaid_grade(text):
    ss, ws = sentences(text), words(text)
    if not ss or not ws:
        return 0.0
    syl = sum(syllables(w) for w in ws)
    return 0.39 * (len(ws) / len(ss)) + 11.8 * (syl / len(ws)) - 15.59


def mean_sentence_words(text):
    ss = sentences(text)
    return (sum(len(words(s)) for s in ss) / len(ss)) if ss else 0.0


# ---------------------------------------------------------------- thresholds
# Written once, before any model output is seen. Not tuned afterwards.

MAX_SENTENCE_WORDS = 20.0
MAX_GRADE = 10.0


# ---------------------------------------------------------------- the needs

def _screen_reader(text):
    return {
        "no_table": len(MD_TABLE_ROW.findall(text)) == 0,
        "no_ascii_art": not has_ascii_art(text),
        "no_emoji": EMOJI.search(text) is None,
        "no_layout_deixis": not _has(text, LAYOUT_DEIXIS),
    }


def _no_vision(text):
    return {
        "no_colour_reference": not _has(text, COLOUR_WORDS),
        "no_position_reference": not _has(text, POSITION_WORDS),
        "no_layout_deixis": not _has(text, LAYOUT_DEIXIS),
    }


def _deaf(text):
    return {
        "no_phone_instruction": not _has(text, PHONE_WORDS),
        "offers_text_route": _has(text, TEXT_ROUTE_WORDS),
    }


def _plain_language(text):
    return {
        "short_sentences": mean_sentence_words(text) <= MAX_SENTENCE_WORDS,
        "low_grade": flesch_kincaid_grade(text) <= MAX_GRADE,
        "no_idiom": not _has(text, IDIOMS),
    }


def _wheelchair(text):
    return {
        "no_walking_assumption": not _has(text, WALKING_WORDS),
        "offers_step_free": _has(text, STEP_FREE_WORDS),
    }


NEEDS = {
    "screen_reader": _screen_reader,
    "no_vision": _no_vision,
    "deaf": _deaf,
    "plain_language": _plain_language,
    "wheelchair": _wheelchair,
}


def check(need, text):
    """One need. `delivered` is true only if every part of it holds."""
    if need not in NEEDS:
        raise KeyError(f"unknown need: {need}")
    parts = NEEDS[need](text)
    return {"delivered": all(parts.values()), **parts}


def check_all(text):
    """Every need, for the matched, mismatched and neutral cells at once."""
    return {need: check(need, text) for need in NEEDS}


# ---------------------------------------------------------------- version 2
# Added 2026-09-29 for e1, after e0. Version 1 above is unchanged, so e0 stays
# reproducible from its own registered instrument.
#
# e0 showed that the version 1 sentence splitter ends a sentence only at . ! or
# ?, so markdown list items without a full stop merge into one long "sentence".
# The plain_language check then partly measured list punctuation: Mistral's
# registered plain-language result was -0.23 and +0.21 with lines as sentence
# boundaries. Version 2 makes every non-empty line a boundary and drops
# markdown markers before counting. Thresholds are unchanged.
#
# first_words() gives every answer the same observation window. In e0 the share
# of answers cut by the token cap differed by cell (Llama: 0.40 need form,
# 0.81 label form), and a presence check is likelier to be seen in an answer
# that ends inside the window.

MD_MARKER = re.compile(r"^\s*(#{1,6}\s*|[-*•]\s+|\d+[.)]\s+)")
WINDOW_WORDS = 250
NL = chr(10)


def first_words(text, n=WINDOW_WORDS):
    """The first n words, keeping line breaks so list structure survives."""
    out, count = [], 0
    for line in text.splitlines():
        w = line.split()
        if count + len(w) >= n:
            out.append(" ".join(w[:n - count]))
            break
        out.append(line)
        count += len(w)
    return NL.join(out)


def line_sentences(text):
    parts = []
    for line in text.splitlines():
        line = line.replace("**", "")
        # markers stack ("### 1. Report it"), so strip until none is left
        while MD_MARKER.match(line):
            line = MD_MARKER.sub("", line, count=1)
        line = line.strip()
        if not line:
            continue
        parts += [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
                  if p.strip()]
    return parts


def flesch_kincaid_grade_v2(text):
    ss, ws = line_sentences(text), words(text)
    if not ss or not ws:
        return 0.0
    syl = sum(syllables(w) for w in ws)
    return 0.39 * (len(ws) / len(ss)) + 11.8 * (syl / len(ws)) - 15.59


def mean_sentence_words_v2(text):
    ss = line_sentences(text)
    return (sum(len(words(s)) for s in ss) / len(ss)) if ss else 0.0


def _plain_language_v2(text):
    return {
        "short_sentences": mean_sentence_words_v2(text) <= MAX_SENTENCE_WORDS,
        "low_grade": flesch_kincaid_grade_v2(text) <= MAX_GRADE,
        "no_idiom": not _has(text, IDIOMS),
    }


NEEDS_V2 = dict(NEEDS, plain_language=_plain_language_v2)


def check_v2(need, text, window=WINDOW_WORDS):
    """Version 2: line-aware plain_language, and the answer read through the
    same window of `window` words (None reads the whole answer)."""
    if need not in NEEDS_V2:
        raise KeyError(f"unknown need: {need}")
    t = first_words(text, window) if window else text
    parts = NEEDS_V2[need](t)
    return {"delivered": all(parts.values()), **parts}


def check_all_v2(text, window=WINDOW_WORDS):
    return {need: check_v2(need, text, window) for need in NEEDS_V2}


if __name__ == "__main__":
    import json
    import sys
    body = sys.stdin.read()
    print(json.dumps({"needs": check_all(body),
                      "mean_sentence_words": round(mean_sentence_words(body), 2),
                      "grade": round(flesch_kincaid_grade(body), 2)}, indent=2))
