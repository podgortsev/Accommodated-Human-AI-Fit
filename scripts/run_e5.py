#!/usr/bin/env python3
"""
run_e5.py - Paper 4, e5: the deafness headline under two more wrappers.

    python run_e5.py qwen                  smoke, collect, analyse
    python run_e5.py qwen --analyse-only
    python run_e5.py qwen --smoke

90 questions x 2 wrappers x 4 cells = 720 generations per model, resumable.
Registered: experiments/e5-wrappers/PREREGISTRATION.md. The original wrapper is
read from e2's committed answers when they are present (locally, not in Colab).
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
for p in (HERE, os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "experiments", "e1-measurable-needs", "scripts"),
          os.path.join(REPO, "experiments", "e2-deaf-contact", "scripts"),
          os.path.join(REPO, "experiments", "e5-wrappers", "scripts")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

import run_e0 as R0            # noqa: E402
import p4_gen as G             # noqa: E402
import build_e5_jobs as E5     # noqa: E402

OUT_DIR = "/content/drive/MyDrive/afl/p4_e5"


def find(name):
    for p in sys.path:
        f = os.path.join(p, name)
        if os.path.exists(f):
            return f
    raise FileNotFoundError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(R0.MODELS))
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--batch", type=int, default=G.BATCH)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    out = os.path.join(a.out_dir, f"e5_{a.model}.csv")
    if a.smoke or not a.analyse_only:
        gen = G.load_chat_generator(a.model)
        with open(find("e0_stimuli.json"), encoding="utf-8") as f:
            ok = R0.smoke(G.single_turn(gen), json.load(f))
        if a.smoke or not ok:
            sys.exit(0 if ok else 1)
        with open(find("e5_stimuli.json"), encoding="utf-8") as f:
            d = json.load(f)
        G.collect_jobs(a.model, gen, out, E5.jobs(d), E5.META, a.batch)
    import analyse_e5
    analyse_e5.main([out])


if __name__ == "__main__":
    main()
