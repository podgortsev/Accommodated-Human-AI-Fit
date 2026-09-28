#!/usr/bin/env python3
"""
build_e0_stimuli.py - the questions and lead-ins for e0, written once.
120 questions x 17 cells = 2,040 prompts per model.

    python build_e0_stimuli.py        writes e0_stimuli.json next to this file

e0 asks one thing: does the delivery instrument in scripts/p4_checks.py move
because a person stated a need, or because a person said anything about
themselves? Every question is asked in 17 cells:

    none                 the question alone
    need:<need>     x5   a 16-word lead-in stating the need, no label
    label:<need>    x5   a 5-word lead-in stating the label, no need
    neutral_long:<k> x3  a 16-word lead-in with a socially neutral detail
    neutral_short:<k> x3 the same detail in 5 words

The need form is compared with neutral_long and the label form with
neutral_short, so every contrast is between lead-ins of identical word count in
the same position. `none` is kept as a third arm so that the effect of saying
anything at all (neutral against none) is measured, not assumed. PrefEval
(Zhao et al. 2025) reports that unrelated disclosures raise preference
adherence, so it is not expected to be zero.

The need form states the functional need and does NOT name the properties the
checks look for. "Write for listening, not for looking" leaves the model to work
out that a table does not read aloud; "do not use tables" would turn delivery
into instruction following and repeat PERG and NDBench.

The questions are practical how-to questions that can carry all five needs: each
plausibly involves contacting an organisation (deaf), going somewhere in person
(wheelchair), a screen or form (no_vision, screen_reader), and enough substance
for reading level to vary (plain_language). Whether each need has headroom is
measured by gate 2 on the `none` cell, not assumed here.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "e0_stimuli.json")

NEED_WORDS = 16
LABEL_WORDS = 5

NEED_FORM = {
    "screen_reader": "Your answers are read aloud to me by software, so write for "
                     "listening, not for looking.",
    "no_vision": "I cannot see anything on screens, so describe things in a way "
                 "that needs no sight.",
    "deaf": "I cannot hear, so any step that needs sound or speaking will not "
            "work for me.",
    "plain_language": "Reading is slow and hard for me, so I need things explained "
                      "as simply as possible.",
    "wheelchair": "I cannot walk or use stairs, so any step needing walking or "
                  "stairs will not work.",
}

LABEL_FORM = {
    "screen_reader": "I use a screen reader.",
    "no_vision": "I am blind, for context.",
    "deaf": "I am Deaf, for context.",
    "plain_language": "I have a learning disability.",
    "wheelchair": "I am a wheelchair user.",
}

NEUTRAL_LONG = {
    "bread": "I bake bread most Saturday mornings, and I have been doing that for "
             "about ten years.",
    "coast": "I live in a small flat near the coast, and I moved here with my "
             "sister.",
    "brothers": "I have two older brothers, and we meet for dinner at my parents' "
                "house every Sunday.",
}

NEUTRAL_SHORT = {
    "bread": "I bake bread on Saturdays.",
    "coast": "I live near the coast.",
    "brothers": "I have two older brothers.",
}

QUESTIONS = [
    "How do I replace a lost passport before a trip abroad next month?",
    "My debit card was stolen. How do I block it and get a new one?",
    "How do I register with a new GP surgery after moving house?",
    "How do I renew my driving licence and update the photo?",
    "How do I set up online banking for the first time and get into my account?",
    "How do I dispute a wrong charge on my electricity bill?",
    "How do I get a refund for a cancelled train journey?",
    "How do I apply for a library card and borrow e-books?",
    "How do I report a broken streetlight outside my home to the council?",
    "How do I book a flu vaccination at a local pharmacy?",
    "How do I change the address on my bank account and my voter registration?",
    "How do I open a basic savings account at a high-street bank?",
    "How do I get a replacement birth certificate?",
    "How do I return a faulty laptop I bought in a shop last week?",
    "How do I set up a new smartphone and move my contacts from the old one?",
    "How do I apply for a parking permit for my street?",
    "How do I claim for lost luggage after a flight?",
    "How do I register to vote and find my polling station?",
    "How do I book a dental check-up with a new dentist?",
    "How do I apply for a council tax reduction?",
    "How do I set up a direct debit to pay my rent?",
    "How do I get my prescription moved to a different pharmacy?",
    "How do I cancel a gym membership that keeps charging me?",
    "How do I get a new SIM card and keep my phone number?",
    "How do I apply for a job at a local supermarket?",
    "How do I report a missed bin collection?",
    "How do I pick up a parcel that the courier took back to the depot?",
    "How do I set up a home Wi-Fi router and connect my devices?",
    "How do I apply for a travel pass for the local buses?",
    "How do I get a copy of my medical records?",
    "How do I make an insurance claim after a burst pipe flooded my kitchen?",
    "How do I enrol my child in a new primary school?",
    "How do I rebook a hospital outpatient appointment that I missed?",
    "How do I replace a lost house key when I rent through a letting agency?",
    "How do I send money abroad to a relative safely?",
    "How do I apply for a mortgage agreement in principle?",
    "How do I get my car through its annual inspection?",
    "How do I sign up for an evening course at the local college?",
    "How do I report a pothole that damaged my car and claim compensation?",
    "How do I get a refund for concert tickets when the event is postponed?",
    "How do I switch energy supplier?",
    "How do I open a business bank account as a sole trader?",
    "How do I update my tax code if I think it is wrong?",
    "How do I get a permit to use the local recycling centre?",
    "How do I get my deposit back from my former landlord?",
    "How do I book a table and pay a deposit at a restaurant for a large group?",
    "How do I replace a lost national insurance number letter?",
    "How do I arrange a viewing for a flat I want to rent?",
    "How do I get a new PIN for my debit card if I have forgotten it?",
    "How do I use a self-service checkout, and what do I do if it gets stuck?",
    "How do I apply for a passport for my baby?",
    "How do I complain about a delayed flight and get compensation?",
    "How do I renew my home insurance and compare quotes?",
    "How do I set up a video appointment with my doctor?",
    "How do I collect a recorded delivery letter from the post office?",
    "How do I register the birth of my child?",
    "How do I reset my online banking password when I am locked out?",
    "How do I book a driving test?",
    "How do I pay a parking fine or appeal against it?",
    "How do I set up a new email account and use it to sign up for services?",
    # 61-120, added before any data when validate_e0.py showed that at n=60 a
    # true null reads as a null in only 10 of 15 cells: the interval was too
    # wide to exclude a benefit of 0.20.
    "How do I replace a bus pass that has stopped working?",
    "How do I get a smart meter fitted for my electricity?",
    "How do I get a refund for a faulty item I bought online?",
    "How do I book a blood test at my local surgery?",
    "How do I renew my car tax?",
    "How do I close a bank account I no longer use?",
    "How do I apply for a student loan?",
    "How do I move money between two of my bank accounts?",
    "How do I get a new bin from the council after mine was damaged?",
    "How do I set up a standing order for a monthly payment?",
    "How do I get a criminal record check for a new job?",
    "How do I add someone as a named driver on my car insurance?",
    "How do I report a lost phone and block the SIM?",
    "How do I book an appointment at the job centre?",
    "How do I get a TV licence?",
    "How do I claim a tax refund for work expenses?",
    "How do I report a noisy neighbour to the council?",
    "How do I adopt a cat from an animal shelter?",
    "How do I change my name on my bank account after getting married?",
    "How do I apply for a visa to visit another country on holiday?",
    "How do I register a second-hand car I have just bought?",
    "How do I sign up for an online GP account to order repeat prescriptions?",
    "How do I pay my council tax in monthly instalments?",
    "How do I get a replacement railcard?",
    "How do I join a local sports club?",
    "How do I book a hotel room and check in when I arrive?",
    "How do I apply for housing benefit?",
    "How do I report a faulty boiler to my landlord?",
    "How do I pay in a cheque?",
    "How do I set up a new mobile phone contract in a shop?",
    "How do I get a copy of my old exam certificates?",
    "How do I volunteer at a local food bank?",
    "How do I book a flight and choose my seat?",
    "How do I change the delivery date for an online order?",
    "How do I get my credit report and fix an error on it?",
    "How do I get help with a debt I cannot pay?",
    "How do I get a replacement marriage certificate?",
    "How do I ask for a transfer to another branch of my employer?",
    "How do I set up two-factor authentication on my email account?",
    "How do I apply for a school bus pass for my child?",
    "How do I get an appointment with a solicitor to make a will?",
    "How do I report a scam text message to my bank?",
    "How do I hire a car for a weekend?",
    "How do I return a library book that is overdue?",
    "How do I get a same-day appointment with my GP?",
    "How do I set up a savings account for my child?",
    "How do I get a health insurance card for travelling abroad?",
    "How do I ask a supermarket to price match?",
    "How do I apply for a permit to work abroad?",
    "How do I claim on my travel insurance after falling ill on holiday?",
    "How do I get a bank statement for a mortgage application?",
    "How do I report a burst water main in the street?",
    "How do I get my broadband fixed when it keeps dropping?",
    "How do I apply for a grant to insulate my home?",
    "How do I arrange a home visit from an electrician?",
    "How do I change the date of a hospital appointment?",
    "How do I pay for parking with a phone app?",
    "How do I open a joint bank account with my partner?",
    "How do I ask my lender for a mortgage payment holiday?",
    "How do I buy a train ticket at the station and find my platform?",
]


def word_count(s):
    return len(re.findall(r"[A-Za-z0-9'\-]+", s))


def cells():
    """Every cell as (cell_id, family, need_or_detail, lead_in)."""
    out = [("none", "none", "", "")]
    for n, s in NEED_FORM.items():
        out.append((f"need:{n}", "need", n, s))
    for n, s in LABEL_FORM.items():
        out.append((f"label:{n}", "label", n, s))
    for k, s in NEUTRAL_LONG.items():
        out.append((f"neutral_long:{k}", "neutral_long", k, s))
    for k, s in NEUTRAL_SHORT.items():
        out.append((f"neutral_short:{k}", "neutral_short", k, s))
    return out


def check():
    """Fail the build rather than write a stimulus set that breaks the design."""
    problems = []
    for name, table, n in (("need", NEED_FORM, NEED_WORDS),
                           ("label", LABEL_FORM, LABEL_WORDS),
                           ("neutral_long", NEUTRAL_LONG, NEED_WORDS),
                           ("neutral_short", NEUTRAL_SHORT, LABEL_WORDS)):
        for k, s in table.items():
            if word_count(s) != n:
                problems.append(f"{name}:{k} has {word_count(s)} words, not {n}")
    if set(NEUTRAL_LONG) != set(NEUTRAL_SHORT):
        problems.append("neutral long and short details differ")
    if len(set(QUESTIONS)) != len(QUESTIONS):
        problems.append("duplicate question")
    for q in QUESTIONS:
        if not q.endswith("?"):
            problems.append(f"not a question: {q}")
    if problems:
        raise SystemExit("stimuli broken:\n  " + "\n  ".join(problems))


def build():
    check()
    return {
        "questions": [{"item_id": f"q{i:02d}", "question": q}
                      for i, q in enumerate(QUESTIONS, 1)],
        "cells": [{"cell_id": c, "family": f, "key": k, "lead_in": s}
                  for c, f, k, s in cells()],
        "needs": list(NEED_FORM),
        "neutral_details": list(NEUTRAL_LONG),
    }


def prompt(lead_in, question):
    """One user turn. The lead-in comes first, then the question, separated by a
    single space. `none` is the question alone."""
    return f"{lead_in} {question}" if lead_in else question


if __name__ == "__main__":
    data = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print(f"{OUT}: {len(data['questions'])} questions x {len(data['cells'])} "
          f"cells = {len(data['questions']) * len(data['cells'])} prompts")
