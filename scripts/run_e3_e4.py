#!/usr/bin/env python3
"""
run_e3_e4.py - Paper 4, e3 (pushback) and e4 (the cost of accommodation) in one
session: the model is loaded once and serves both.

    python run_e3_e4.py qwen                  smoke, e3, e4, then both analyses
    python run_e3_e4.py qwen --only e3        one experiment
    python run_e3_e4.py qwen --analyse-only   analyse the CSVs already in OUT_DIR
    python run_e3_e4.py qwen --smoke          GPU self-check only, writes nothing

e3: 210 first turns x 3 follow-ups = 630 generations per model.
e4: 330 questions x 7 cells = 2,310 generations per model. Both resumable.

Registered: experiments/e3-pushback/PREREGISTRATION.md and
experiments/e4-cost/PREREGISTRATION.md.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
for p in (HERE,
          os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "experiments", "e1-measurable-needs", "scripts"),
          os.path.join(REPO, "experiments", "e2-deaf-contact", "scripts"),
          os.path.join(REPO, "experiments", "e3-pushback", "scripts"),
          os.path.join(REPO, "experiments", "e4-cost", "scripts")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

import run_e0 as R0            # noqa: E402
import p4_gen as G             # noqa: E402
import build_e3_jobs as E3     # noqa: E402
import build_e4_stimuli as E4  # noqa: E402

OUT_DIR = "/content/drive/MyDrive/afl/p4_e34"


def find(name):
    for p in sys.path:
        f = os.path.join(p, name)
        if os.path.exists(f):
            return f
    raise FileNotFoundError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(R0.MODELS))
    ap.add_argument("--only", choices=("e3", "e4"))
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--batch", type=int, default=G.BATCH)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    e3_csv = os.path.join(a.out_dir, f"e3_{a.model}.csv")
    e4_csv = os.path.join(a.out_dir, f"e4_{a.model}.csv")
    run = {"e3", "e4"} if a.only is None else {a.only}

    if a.smoke or not a.analyse_only:
        gen = G.load_chat_generator(a.model)
        with open(find("e0_stimuli.json"), encoding="utf-8") as f:
            ok = R0.smoke(G.single_turn(gen), json.load(f))
        if a.smoke or not ok:
            sys.exit(0 if ok else 1)
        if "e3" in run:
            with open(find("e3_turn1.json"), encoding="utf-8") as f:
                d3 = json.load(f)
            print("e3: follow-up turns")
            G.collect_jobs(a.model, gen, e3_csv, E3.jobs(d3, a.model), E3.META, a.batch)
        if "e4" in run:
            with open(find("e4_stimuli.json"), encoding="utf-8") as f:
                d4 = json.load(f)
            print("e4: calculation plus question")
            G.collect_jobs(a.model, gen, e4_csv, E4.jobs(d4), E4.META, a.batch)
    if "e3" in run and os.path.exists(e3_csv):
        import analyse_e3
        analyse_e3.main([e3_csv], find("e3_turn1.json"))
    if "e4" in run and os.path.exists(e4_csv):
        import analyse_e4
        analyse_e4.main([e4_csv])


if __name__ == "__main__":
    main()
