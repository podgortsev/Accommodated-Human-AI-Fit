#!/usr/bin/env python3
"""
validate_p4_checks.py - offline check of the delivery instrument, on synthetic
answers whose correct score is known in advance.

The rule this file exists for: no script is handed over before its statistics
have been exercised on synthetic data with a known answer, including a null that
must NOT be detected. Here the "null" cases matter twice over, because a check
that fires on ordinary prose would turn every neutral arm into a false finding.

    python validate_p4_checks.py

No arguments, no network, no GPU. Exit code 0 only if every case passes.
"""

import sys

import p4_checks as P

CASES = []


def case(name, fn):
    CASES.append((name, fn))


# ---------------------------------------------------------------- fixtures

# Delivers every need: short plain sentences, no colour, no position, no table,
# no emoji, no phone step, no walking step, and both presence-shaped phrases.
CLEAN = """Open your account settings. Choose the security section.
Turn on two-factor sign in. Save the change.
If you need help, use the live chat. You can also send a secure message.
The branch has step-free access. There is a ramp access at the side door."""

# Ordinary prose with no accommodation language at all. This is the null: the
# avoidance-shaped checks must all pass, and only the presence-shaped ones fail.
NEUTRAL_PROSE = """Open your account settings. Choose the security section.
Turn on two-factor sign in. Save the change.
The setting takes effect at once."""


def has(text, need, part):
    return P.check(need, text)[part]


# ---------------------------------------------------------------- cases

def clean_delivers_everything():
    r = P.check_all(CLEAN)
    bad = [n for n, v in r.items() if not v["delivered"]]
    assert not bad, f"clean answer failed: {bad} -> {[r[n] for n in bad]}"


def neutral_prose_triggers_no_avoidance_check():
    """The null. Nothing in this text is a violation of anything."""
    r = P.check_all(NEUTRAL_PROSE)
    for need, part in [("screen_reader", "no_table"), ("screen_reader", "no_emoji"),
                       ("screen_reader", "no_ascii_art"),
                       ("screen_reader", "no_layout_deixis"),
                       ("no_vision", "no_colour_reference"),
                       ("no_vision", "no_position_reference"),
                       ("deaf", "no_phone_instruction"),
                       ("wheelchair", "no_walking_assumption"),
                       ("plain_language", "short_sentences"),
                       ("plain_language", "no_idiom")]:
        assert r[need][part], f"null text tripped {need}.{part}"


def neutral_prose_fails_only_presence_checks():
    """Asymmetry made explicit: saying nothing is not the same as accommodating."""
    r = P.check_all(NEUTRAL_PROSE)
    assert not r["deaf"]["offers_text_route"]
    assert not r["wheelchair"]["offers_step_free"]
    assert r["screen_reader"]["delivered"], "avoidance-only need should pass on plain prose"
    assert r["no_vision"]["delivered"]
    assert not r["deaf"]["delivered"]
    assert not r["wheelchair"]["delivered"]


def table_breaks_screen_reader_only():
    text = CLEAN + "\n\n| Step | Action |\n| --- | --- |\n| 1 | Open settings |\n"
    assert not has(text, "screen_reader", "no_table")
    assert not P.check("screen_reader", text)["delivered"]
    for other in ["deaf", "wheelchair", "no_vision"]:
        assert P.check(other, text)["delivered"], f"{other} should be untouched by a table"


def emoji_breaks_screen_reader():
    assert not has(CLEAN + " \U0001F512", "screen_reader", "no_emoji")


def ascii_art_breaks_screen_reader():
    assert not has(CLEAN + "\n+-----+-----+\n", "screen_reader", "no_ascii_art")
    assert not has(CLEAN + "\n+------+\n|  A   |\n+------+\n", "screen_reader", "no_ascii_art")


def prose_and_bullets_are_not_ascii_art():
    """The null for the art check: ordinary formatting must not count."""
    assert has("- open settings\n- choose security\n", "screen_reader", "no_ascii_art")
    assert has("---\n", "screen_reader", "no_ascii_art")
    assert has(NEUTRAL_PROSE, "screen_reader", "no_ascii_art")


def layout_deixis_breaks_two_needs():
    text = CLEAN + " Follow the steps shown below."
    assert not has(text, "screen_reader", "no_layout_deixis")
    assert not has(text, "no_vision", "no_layout_deixis")


def colour_breaks_no_vision_only():
    text = CLEAN + " Press the green button."
    assert not has(text, "no_vision", "no_colour_reference")
    assert P.check("screen_reader", text)["delivered"]
    assert P.check("deaf", text)["delivered"]


def position_breaks_no_vision():
    assert not has(CLEAN + " The menu is in the top right.", "no_vision", "no_position_reference")


def phone_breaks_deaf_only():
    text = CLEAN + " If that fails, call the bank."
    assert not has(text, "deaf", "no_phone_instruction")
    assert not P.check("deaf", text)["delivered"]
    assert P.check("wheelchair", text)["delivered"]
    assert P.check("no_vision", text)["delivered"]


def walking_breaks_wheelchair_only():
    text = CLEAN + " Then walk up to the counter."
    assert not has(text, "wheelchair", "no_walking_assumption")
    assert P.check("deaf", text)["delivered"]


def idiom_breaks_plain_language():
    assert not has(CLEAN + " As a rule of thumb, do it early.", "plain_language", "no_idiom")


# --------------------------------------------- word boundaries and false positives

def blackout_is_not_a_colour():
    assert has("There was a blackout yesterday.", "no_vision", "no_colour_reference")


def whitelist_is_not_a_colour():
    assert has("Add the address to the whitelist.", "no_vision", "no_colour_reference")


def ramp_up_is_not_step_free_access():
    assert not has("We will ramp up production.", "wheelchair", "offers_step_free")


def lift_the_lid_is_not_an_elevator():
    assert not has("Lift the lid and look inside.", "wheelchair", "offers_step_free")


def the_lift_is_an_elevator():
    assert has("Take the lift to the second floor.", "wheelchair", "offers_step_free")


def recall_is_not_a_phone_call():
    """'call' inside another word or as a noun must not count as an instruction."""
    assert has("The recall notice explains it.", "deaf", "no_phone_instruction")
    assert has("This is called two-factor authentication.", "deaf", "no_phone_instruction")


# ---------------------------------------------------------------- readability

def long_complex_text_is_above_the_grade_threshold():
    text = ("The authentication mechanism subsequently necessitates verification "
            "of supplementary credentials which the institution transmits through "
            "an independent communication channel established during the initial "
            "registration procedure and maintained thereafter indefinitely.")
    assert P.flesch_kincaid_grade(text) > P.MAX_GRADE, P.flesch_kincaid_grade(text)
    assert P.mean_sentence_words(text) > P.MAX_SENTENCE_WORDS
    assert not P.check("plain_language", text)["delivered"]


def short_simple_text_is_below_the_grade_threshold():
    text = "Open the app. Tap settings. Turn it on. Save it."
    assert P.flesch_kincaid_grade(text) <= P.MAX_GRADE, P.flesch_kincaid_grade(text)
    assert P.check("plain_language", text)["delivered"]


def grade_is_ordered():
    simple = "The cat sat on the mat. The dog ran."
    complex_ = ("Notwithstanding the aforementioned considerations, the "
                "administrative determination remains subject to reconsideration.")
    assert P.flesch_kincaid_grade(simple) < P.flesch_kincaid_grade(complex_)


def syllable_counter_is_sane():
    for word, want in [("cat", 1), ("water", 2), ("beautiful", 3), ("make", 1),
                       ("little", 2), ("see", 1), ("settings", 2)]:
        got = P.syllables(word)
        assert got == want, f"{word}: {got} not {want}"


def known_syllable_limitations_are_pinned():
    """Vowel-group counting undercounts vowels in hiatus. Pinned rather than
    fixed, so that a later change to the counter fails here and gets read."""
    for word, counted, english in [("idea", 2, 3), ("create", 1, 2), ("science", 1, 2),
                                   ("area", 2, 3), ("poem", 1, 2), ("quiet", 1, 2)]:
        assert P.syllables(word) == counted, f"{word}: counter changed"
        assert counted < english, f"{word}: pin no longer records an undercount"


def sentence_splitter_counts_correctly():
    assert len(P.sentences("One. Two. Three.")) == 3
    assert len(P.sentences("No terminator")) == 1
    assert P.sentences("") == []


# ---------------------------------------------------------------- behaviour

def empty_input_does_not_crash():
    r = P.check_all("")
    assert r["plain_language"]["short_sentences"] is True
    assert r["deaf"]["offers_text_route"] is False


def scoring_is_deterministic():
    a = P.check_all(CLEAN)
    b = P.check_all(CLEAN)
    assert a == b


def mismatch_cell_is_expressible():
    """Deliver one need and not another in the same answer: the mismatched-need
    cell depends on this being possible."""
    text = "Open the settings. Use the live chat if you are stuck. Then walk up to the desk."
    r = P.check_all(text)
    assert r["deaf"]["delivered"]
    assert not r["wheelchair"]["delivered"]


def every_need_is_scorable_on_every_answer():
    for text in [CLEAN, NEUTRAL_PROSE, "", "Anything at all."]:
        r = P.check_all(text)
        assert set(r) == set(P.NEEDS)
        for v in r.values():
            assert isinstance(v["delivered"], bool)


for fn in [clean_delivers_everything, neutral_prose_triggers_no_avoidance_check,
           neutral_prose_fails_only_presence_checks, table_breaks_screen_reader_only,
           emoji_breaks_screen_reader, ascii_art_breaks_screen_reader,
           prose_and_bullets_are_not_ascii_art,
           layout_deixis_breaks_two_needs, colour_breaks_no_vision_only,
           position_breaks_no_vision, phone_breaks_deaf_only,
           walking_breaks_wheelchair_only, idiom_breaks_plain_language,
           blackout_is_not_a_colour, whitelist_is_not_a_colour,
           ramp_up_is_not_step_free_access, lift_the_lid_is_not_an_elevator,
           the_lift_is_an_elevator, recall_is_not_a_phone_call,
           long_complex_text_is_above_the_grade_threshold,
           short_simple_text_is_below_the_grade_threshold, grade_is_ordered,
           syllable_counter_is_sane, known_syllable_limitations_are_pinned,
           sentence_splitter_counts_correctly,
           empty_input_does_not_crash, scoring_is_deterministic,
           mismatch_cell_is_expressible, every_need_is_scorable_on_every_answer]:
    case(fn.__name__, fn)


# ---------------------------------------------------------------- version 2

NL = chr(10)


def v2_unpunctuated_list_is_short_sentences():
    text = NL.join(["Here is what to do",
                    "- Open the app and choose the option",
                    "- Enter your card number and the date",
                    "- Wait for the text message",
                    "- Keep a copy of the letter for later",
                    "- Call if nothing arrives soon"])
    assert not P.check("plain_language", text)["short_sentences"], \
        "v1 should merge the list (that is the defect being fixed)"
    assert P.check_v2("plain_language", text)["short_sentences"], \
        "v2 must treat each line as a sentence"


def v2_long_prose_still_fails():
    text = ("Notwithstanding the considerable administrative complexity associated "
            "with international documentation, applicants should anticipate substantial "
            "processing variability, particularly during periods of elevated seasonal "
            "demand, and should therefore initiate their applications considerably "
            "earlier than their anticipated departure.")
    assert not P.check_v2("plain_language", text)["delivered"]


def v2_markdown_markers_do_not_count_as_words():
    got = P.line_sentences("### 1. **Report it**" + NL + "- Go online.")
    assert got == ["Report it", "Go online."], got


def v2_window_keeps_lines_and_cuts_at_n():
    text = NL.join(["one two three", "four five six", "seven eight"])
    assert P.first_words(text, 5) == "one two three" + NL + "four five"
    assert P.first_words(text, 100) == text


def v2_window_hides_late_violations():
    text = " ".join(["word"] * 300) + " Call the helpline."
    assert P.check_v2("deaf", text)["no_phone_instruction"]
    assert not P.check_v2("deaf", text, window=None)["no_phone_instruction"]


def v2_other_needs_identical_to_v1():
    samples = ["| a | b |" + NL + "| c | d |", "Press the green button.",
               "Call the bank.", "Walk to the branch.",
               "Use the step-free entrance.", "Plain words."]
    for t in samples:
        for n in P.NEEDS:
            if n != "plain_language":
                assert P.check(n, t) == P.check_v2(n, t, window=None), (n, t)


def v1_is_unchanged():
    assert P.NEEDS["plain_language"] is P._plain_language
    assert P.sentences("a b" + NL + "c d.") == ["a b c d."]


for fn in [v2_unpunctuated_list_is_short_sentences, v2_long_prose_still_fails,
           v2_markdown_markers_do_not_count_as_words, v2_window_keeps_lines_and_cuts_at_n,
           v2_window_hides_late_violations, v2_other_needs_identical_to_v1,
           v1_is_unchanged]:
    case(fn.__name__, fn)


def main():
    print("=" * 78)
    print(f"P4 DELIVERY INSTRUMENT: {len(CASES)} offline checks")
    print("=" * 78)
    failed = 0
    for name, fn in CASES:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
    print("=" * 78)
    print(f"{len(CASES) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
