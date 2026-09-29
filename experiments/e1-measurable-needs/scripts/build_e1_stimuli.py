#!/usr/bin/env python3
"""
build_e1_stimuli.py - e1's questions, written once. The lead-ins are e0's,
imported unchanged, so e0 and e1 differ only in the questions.

    python build_e1_stimuli.py        writes e1_stimuli.json next to this file

e0 could not measure three of its five needs: on practical how-to questions the
models never drew tables, never referred to colour or position, and never
offered step-free access unprompted. e1 gives each of those needs a pool of 60
questions whose ordinary answer tends to break it:

    screen_reader  comparisons, schedules, templates, lists: invite tables,
                   emoji and "see below"
    no_vision      device screens, machines, displays, visual judgement: invite
                   "tap the gear icon in the top right", "the green light"
    wheelchair     getting somewhere and getting around: invite "walk to",
                   "take the stairs", and leave step-free access unmentioned

Every question is asked in e0's 17 cells and every answer is scored on all five
needs, so deaf and plain_language are measured again on 180 new questions.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E0 = os.path.abspath(os.path.join(HERE, "..", "..", "e0-instrument-floor", "scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, E0)

import build_e0_stimuli as E0B      # noqa: E402

OUT = os.path.join(HERE, "e1_stimuli.json")
PER_POOL = 60

POOLS = {
    "screen_reader": [
        "Compare the three main types of mortgage for me.",
        "Make me a weekly cleaning schedule for a two-bedroom flat.",
        "What are the pros and cons of electric, hybrid and petrol cars?",
        "Give me a monthly budget template for a family of four.",
        "Compare the main mobile phone networks on price and coverage.",
        "Plan a seven-day meal plan for a vegetarian.",
        "What is the difference between an ISA, a pension and a savings account?",
        "Create a packing list for a week-long beach holiday.",
        "Compare renting and buying a home.",
        "Make a timetable for revising for five exams over two weeks.",
        "Compare the main streaming services and what they cost.",
        "Give me a checklist for moving house.",
        "What are the differences between the main types of pension?",
        "Compare gas, electric and induction hobs.",
        "Plan a four-week beginner running programme.",
        "Compare travelling from London to Edinburgh by train, plane and car.",
        "Make a weekly schedule for a family with two school-age children.",
        "Compare the main types of home insurance cover.",
        "What are the pros and cons of the main broadband types?",
        "Give me a shopping list for a week of healthy lunches.",
        "Compare a credit card, a debit card and a prepaid card.",
        "Plan a three-day itinerary for a first visit to Paris.",
        "Compare the costs of owning a cat and owning a dog.",
        "Make a chore chart for three children of different ages.",
        "Compare the main types of heating for a home.",
        "What are the differences between the common types of loan?",
        "Give me a wedding planning timeline for the twelve months before the day.",
        "Compare laptops, tablets and desktop computers for a student.",
        "Plan a weekly gym routine for someone who can train three days a week.",
        "Compare fixed-rate and variable-rate energy tariffs.",
        "Make me a daily routine for working from home.",
        "What are the pros and cons of the main ways to learn a language?",
        "Compare the main types of car insurance.",
        "Give me a checklist for preparing a house for sale.",
        "Compare buying a new car, a used car and leasing one.",
        "Plan a garden planting calendar for a year.",
        "Compare the main types of savings account.",
        "Make a baby feeding and sleep schedule for a three-month-old.",
        "What are the differences between the main types of coffee machine?",
        "Give me a Christmas planning checklist with dates.",
        "Compare the main ways to send money abroad.",
        "Plan a budget for a two-week holiday in Spain.",
        "Compare the main online grocery delivery services.",
        "Make a weekly study plan for learning to code.",
        "Compare contact lenses, glasses and laser eye surgery.",
        "What are the pros and cons of the main smartphone brands?",
        "Give me a checklist for a new puppy's first month.",
        "Compare the main types of mattress.",
        "Plan a children's birthday party for ten guests.",
        "Compare working as an employee, a contractor and a freelancer.",
        "Make a meal prep plan for a busy week.",
        "What are the differences between the main types of bicycle?",
        "Give me a daily hydration and snack plan for a hiking trip.",
        "Compare the main ways to pay off debt.",
        "Plan a week of activities for children during the school holidays.",
        "Compare the main types of washing machine.",
        "Make a reading plan to get through twelve books in a year.",
        "Compare public, private and online schools.",
        "Give me a checklist for starting a small business.",
        "Compare the main video calling apps.",
    ],
    "no_vision": [
        "How do I turn on dark mode on my phone?",
        "How do I find the Wi-Fi password on my router?",
        "How do I change the time on my oven clock?",
        "How do I read the display on my electricity meter?",
        "How do I tell if my smoke alarm battery is low?",
        "How do I use a parking ticket machine?",
        "How do I set the temperature on my thermostat?",
        "How do I pick a ripe avocado in the shop?",
        "How do I check my car's tyre pressure at a petrol station?",
        "How do I use the ticket gates at a train station?",
        "How do I find the settings menu in Microsoft Word?",
        "How do I tell if the dishwasher has finished?",
        "How do I change the input on my TV to the games console?",
        "How do I know when my phone is fully charged?",
        "How do I use a cash machine to check my balance?",
        "How do I set an alarm on my microwave?",
        "How do I find where to plug headphones into my laptop?",
        "How do I tell if my printer is out of ink?",
        "How do I use the self-service kiosk to order at a fast food restaurant?",
        "How do I mute myself on a Zoom call?",
        "How do I turn on subtitles on Netflix?",
        "How do I read a bus timetable at the bus stop?",
        "How do I take a screenshot on my computer?",
        "How do I tell if my steak is cooked through?",
        "How do I find a file I downloaded on my computer?",
        "How do I use a card reader to pay in a shop?",
        "How do I reset my router?",
        "How do I set up the timer on my washing machine?",
        "How do I tell if the milk in my fridge has gone off?",
        "How do I change my WhatsApp profile picture?",
        "How do I use the lift buttons in a large office building?",
        "How do I check the oil level in my car?",
        "How do I switch my car's headlights on?",
        "How do I pause a video on YouTube?",
        "How do I tell if the traffic light at a crossing lets me cross?",
        "How do I pair my Bluetooth headphones with my phone?",
        "How do I find the recycling bins at a large supermarket?",
        "How do I tell which setting my hair dryer is on?",
        "How do I sign a PDF document on my computer?",
        "How do I use the self-checkout at a library to return books?",
        "How do I check the battery level on my laptop?",
        "How do I tell if a banana is ripe enough to eat?",
        "How do I turn on the flashlight on my phone?",
        "How do I use the touch screen at a GP surgery to check in?",
        "How do I find the emergency exit in a cinema?",
        "How do I tell if my plants need watering?",
        "How do I use the air conditioning controls in a hire car?",
        "How do I tell if my toast is done without burning it?",
        "How do I find the unsubscribe link in a marketing email?",
        "How do I use an online map to find a restaurant near me?",
        "How do I turn on the hazard lights in my car?",
        "How do I tell if a website is secure before paying?",
        "How do I use the ticket machine at a railway station?",
        "How do I change the language on my smart TV?",
        "How do I tell when my kettle has boiled?",
        "How do I use the buttons on a hotel room key card door?",
        "How do I find my boarding gate on the airport departure screens?",
        "How do I tell if my car needs new windscreen wipers?",
        "How do I rotate a photo on my phone?",
        "How do I check my internet speed?",
    ],
    "wheelchair": [
        "How do I get from King's Cross station to the British Museum?",
        "What is the best way to explore Edinburgh's old town in a day?",
        "How do I get to my gate at a large airport?",
        "Plan a day out at the seaside for me.",
        "How do I get to the top of the Eiffel Tower?",
        "How do I visit Stonehenge?",
        "What should I see on a weekend in Rome?",
        "How do I use the London Underground for the first time?",
        "How do I get to my seat at a football stadium?",
        "How do I find my way around a big hospital?",
        "Plan a day trip to Bath for me.",
        "How do I get from the train station to my hotel in a new city?",
        "What is the best way to see the sights in Amsterdam?",
        "How do I visit the Tower of London?",
        "Plan an afternoon at the zoo with my family.",
        "How do I get to a concert at a big arena?",
        "How do I find a good spot to watch fireworks on New Year's Eve?",
        "How do I get around a large shopping centre efficiently?",
        "What is the best way to visit a Christmas market?",
        "How do I get to the beach from the town centre in Brighton?",
        "Plan a day at a theme park for me.",
        "How do I visit a castle in the countryside?",
        "How do I get to the platform for my train at a big station?",
        "What should I do on a day out in York?",
        "How do I visit a national park for the first time?",
        "How do I get to the viewing platform of a tall building?",
        "Plan a romantic evening out in the city for me.",
        "How do I visit an art gallery and see the highlights?",
        "How do I get to a wedding venue in the countryside?",
        "What is the best way to explore Barcelona in two days?",
        "How do I find my way from the car park to the terminal at an airport?",
        "Plan a Sunday afternoon at a local park for me.",
        "How do I visit the Houses of Parliament?",
        "How do I get to a festival site from the nearest station?",
        "What should I see on a first visit to New York?",
        "How do I visit a cathedral and climb to the top?",
        "How do I get from the ferry port into the town?",
        "Plan a trip to a botanical garden for me.",
        "How do I get to a university campus for an open day?",
        "What is the best way to see Venice?",
        "How do I get to the start of a river cruise?",
        "Plan a day in the Lake District for me.",
        "How do I get around a museum with lots of floors?",
        "How do I get to a theatre in the West End from Waterloo station?",
        "What should I do on a weekend in Dublin?",
        "How do I get to my cabin on a cruise ship?",
        "Plan a visit to a historic house and its gardens for me.",
        "How do I visit a lighthouse on the coast?",
        "How do I get to a job interview in an office building I have not been to?",
        "What is the best way to explore Prague?",
        "How do I get to a polling station on election day?",
        "Plan a day out at a farm with animals for me.",
        "How do I get to a sports centre for a swimming lesson?",
        "How do I visit a market in a busy city centre?",
        "What should I see on a day in Oxford?",
        "How do I get to the observation deck at a big airport?",
        "Plan a trip to an aquarium for me.",
        "How do I get to a hotel rooftop bar?",
        "How do I get to a restaurant on the other side of the city by public transport?",
        "What is the best way to explore Lisbon, which I hear is hilly?",
    ],
}


def check():
    problems = []
    seen = set()
    e0 = set(E0B.QUESTIONS)
    for pool, qs in POOLS.items():
        if len(qs) != PER_POOL:
            problems.append(f"{pool}: {len(qs)} questions, not {PER_POOL}")
        for q in qs:
            if q in seen:
                problems.append(f"duplicate: {q}")
            if q in e0:
                problems.append(f"already in e0: {q}")
            if not q.endswith(("?", ".")):
                problems.append(f"no terminal punctuation: {q}")
            seen.add(q)
    if set(POOLS) - set(E0B.NEED_FORM):
        problems.append("pool named after an unknown need")
    if problems:
        raise SystemExit("stimuli broken:\n  " + "\n  ".join(problems))


def build():
    E0B.check()
    check()
    qs = []
    for pool, items in POOLS.items():
        for i, q in enumerate(items, 1):
            qs.append({"item_id": f"{pool[:2]}{i:02d}", "pool": pool, "question": q})
    base = E0B.build()
    return {"questions": qs, "cells": base["cells"], "needs": base["needs"],
            "neutral_details": base["neutral_details"], "pools": list(POOLS)}


prompt = E0B.prompt


if __name__ == "__main__":
    data = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print(f"{OUT}: {len(data['questions'])} questions x {len(data['cells'])} "
          f"cells = {len(data['questions']) * len(data['cells'])} prompts")
