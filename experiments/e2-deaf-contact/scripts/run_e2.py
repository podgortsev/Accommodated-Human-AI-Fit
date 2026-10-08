#!/usr/bin/env python3
"""
run_e2.py - Paper 4, e2: the deaf need, tested where it arises.

    python run_e2.py qwen                  collect in two phases, then analyse
    python run_e2.py qwen --analyse-only   analyse the CSV already in OUT_DIR
    python run_e2.py qwen --smoke          GPU self-check, writes nothing

90 questions x 17 cells = 1,530 generations per model. e1's two-phase collector
unchanged (none first, the ceiling gate, then the rest), with e2's file names.

Registered: PREREGISTRATION.md. The read to trust: analyse_e2.py.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(EXP, ".."))
for p in (HERE, os.path.join(EXP, "e1-measurable-needs", "scripts"),
          os.path.join(EXP, "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "experiments", "shared", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import run_e0 as R0      # noqa: E402
import run_e1 as R1      # noqa: E402

OUT_DIR = "/content/drive/MyDrive/afl/p4_e2"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(R0.MODELS))
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--batch", type=int, default=R0.BATCH)
    a = ap.parse_args()

    with open(os.path.join(HERE, "e2_stimuli.json"), encoding="utf-8") as f:
        stimuli = json.load(f)
    if a.smoke:
        sys.exit(0 if R0.smoke(R0.load_generator(a.model), R1.stimuli_for_smoke())
                 else 1)
    os.makedirs(a.out_dir, exist_ok=True)
    if not a.analyse_only:
        R1.collect_all(a.model, R0.load_generator(a.model), a.out_dir, stimuli,
                       a.batch, prefix="e2")
    import analyse_e2
    analyse_e2.main([os.path.join(a.out_dir, f"e2_{a.model}.csv")])


if __name__ == "__main__":
    main()
