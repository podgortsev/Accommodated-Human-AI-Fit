#!/usr/bin/env python3
"""
build_e2_stimuli.py - e2's questions, written once. Lead-ins are e0's, unchanged.

    python build_e2_stimuli.py        writes e2_stimuli.json next to this file

e2 exists because e1 put the deaf need on questions where nobody has to contact
anyone (a phone instruction in 1 to 2 percent of answers), so e1 could not test
it. e2 tests it where it arises: 90 questions whose ordinary answer involves
contacting an organisation, where a phone call is the default route and a text
route is possible. The add-not-remove decomposition, exploratory in e0, is the
registered hypothesis here.

No question repeats e0 or e1. Every question is asked in e0's 17 cells.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, os.path.join(EXP, "e0-instrument-floor", "scripts"),
          os.path.join(EXP, "e1-measurable-needs", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_e0_stimuli as E0B     # noqa: E402
import build_e1_stimuli as E1B     # noqa: E402

OUT = os.path.join(HERE, "e2_stimuli.json")
N = 90

QUESTIONS = [
    "How do I cancel my broadband contract?",
    "How do I report a power cut in my area?",
    "How do I change my energy tariff?",
    "How do I complain to my mobile network about a wrong bill?",
    "What should I do if I smell gas in my home?",
    "How do I book a repair for my washing machine under warranty?",
    "How do I get a refund from an airline for a cancelled flight?",
    "How do I tell my bank I am going abroad?",
    "How do I report a fraudulent transaction on my credit card?",
    "How do I change my appointment with the council housing office?",
    "How do I chase a late tax rebate?",
    "How do I tell my landlord about a leak in the bathroom?",
    "How do I get a quote for car insurance?",
    "How do I book a taxi to the airport for an early flight?",
    "How do I cancel a hotel booking?",
    "How do I arrange a boiler service?",
    "How do I report a stolen bicycle to the police?",
    "How do I get an emergency dentist appointment?",
    "How do I ask my GP surgery for a repeat prescription?",
    "How do I reschedule a parcel delivery with a courier?",
    "How do I cancel a magazine subscription?",
    "How do I dispute a parking charge from a private company?",
    "How do I get a replacement bank card sent to a new address?",
    "How do I report a noisy party next door late at night?",
    "How do I arrange a home visit from a district nurse?",
    "How do I tell my child's school they are off sick?",
    "How do I book a vet appointment for my dog?",
    "How do I ask for a higher limit on my credit card?",
    "How do I get breakdown recovery when my car will not start?",
    "How do I report a missing pet?",
    "How do I make a claim on my phone insurance?",
    "How do I set up a payment plan for an overdue bill?",
    "How do I tell the council I have moved out of my flat?",
    "How do I book a plumber for a blocked drain?",
    "How do I change my train ticket to a different time?",
    "How do I get my water supply reconnected?",
    "How do I report a fault with my landline?",
    "How do I contact my energy company about a faulty smart meter?",
    "How do I book a removal company for a house move?",
    "How do I ask my employer for a copy of my payslip?",
    "How do I report a car accident to my insurer?",
    "How do I cancel a doctor's appointment?",
    "How do I book non-emergency patient transport to hospital?",
    "How do I report a change of circumstances for my benefits?",
    "How do I book a babysitter through an agency?",
    "How do I find out how much is in my workplace pension?",
    "How do I complain about a rude member of staff at a shop?",
    "How do I order a replacement part for my fridge?",
    "How do I report a broken lift in my block of flats?",
    "How do I get help from my bank when I am locked out of the app?",
    "How do I change the name on a utility bill?",
    "How do I make a reservation at a busy restaurant?",
    "How do I cancel a car rental booking?",
    "How do I report a scam call I received?",
    "How do I get a refund from a delivery company for a broken item?",
    "How do I report damp and mould to my housing association?",
    "How do I get a sick note from my doctor?",
    "How do I report a lost credit card while I am abroad?",
    "How do I arrange a gas safety check as a landlord?",
    "How do I contact the licensing agency about a problem with my driving licence?",
    "How do I ask my lender for a mortgage statement?",
    "How do I follow up on a job application I have not heard back about?",
    "How do I contact my local MP about an issue?",
    "How do I report graffiti to the council?",
    "How do I book a carpet cleaning service?",
    "How do I cancel an online order that has not been sent yet?",
    "How do I get an engineer to fix my broadband?",
    "How do I query a mistake on my council tax bill?",
    "How do I change the date of a ferry booking?",
    "How do I ask my university for an extension on an assignment?",
    "How do I report mice in my rented flat to my landlord?",
    "How do I get my energy supplier to refund the credit on my account?",
    "How do I report a faulty traffic light?",
    "How do I order a new recycling box from the council?",
    "How do I complain to a hospital about my care?",
    "How do I get a copy of my car insurance documents?",
    "How do I get legal advice about a dispute with my builder?",
    "How do I chase a prescription delivery that has not arrived?",
    "How do I book an appointment at the passport office?",
    "How do I stop a direct debit to a charity?",
    "How do I complain to my train company about overcrowding?",
    "How do I get a refund for a gym class that was cancelled?",
    "How do I claim for appliances damaged by a power surge?",
    "How do I sort out being charged twice by a shop?",
    "How do I upgrade my internet speed with my provider?",
    "How do I ask a hotel for a late checkout?",
    "How do I report anti-social behaviour on my street?",
    "How do I book an electrician for an emergency repair?",
    "How do I tell my insurer I have changed my car?",
    "How do I find out why my pension payment is late?",
]


def check():
    problems = []
    earlier = set(E0B.QUESTIONS) | {q for qs in E1B.POOLS.values() for q in qs}
    if len(QUESTIONS) != N:
        problems.append(f"{len(QUESTIONS)} questions, not {N}")
    if len(set(QUESTIONS)) != len(QUESTIONS):
        problems.append("duplicate question")
    for q in QUESTIONS:
        if q in earlier:
            problems.append(f"already used in e0 or e1: {q}")
        if not q.endswith("?"):
            problems.append(f"not a question: {q}")
    if problems:
        raise SystemExit("stimuli broken:\n  " + "\n  ".join(problems))


def build():
    E0B.check()
    check()
    base = E0B.build()
    return {"questions": [{"item_id": f"de{i:02d}", "pool": "deaf", "question": q}
                          for i, q in enumerate(QUESTIONS, 1)],
            "cells": base["cells"], "needs": base["needs"],
            "neutral_details": base["neutral_details"], "pools": ["deaf"]}


prompt = E0B.prompt


if __name__ == "__main__":
    data = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print(f"{OUT}: {len(data['questions'])} questions x {len(data['cells'])} "
          f"cells = {len(data['questions']) * len(data['cells'])} prompts")
