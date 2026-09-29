#!/usr/bin/env python3
"""
run_e1.py - Paper 4, e1: the three needs e0 could not measure, and a
replication of the two it could.

    python run_e1.py qwen                  collect in two phases, then analyse
    python run_e1.py qwen --analyse-only   analyse the CSV already in OUT_DIR
    python run_e1.py qwen --smoke          GPU self-check, writes nothing

180 questions x 17 cells = 3,060 generations per model at most. Resumable.

Phase 1 generates the `none` cell for all 180 questions. Gate 2 is then applied
per pool: if the pool's own need is delivered in more than 0.90 of its `none`
answers, the model already accommodates without being told and there is no room
for a benefit, so that pool's other 16 cells are not generated on this model.
The decision is written to e1_<model>_gate.json and never revisited. Phase 2
generates everything else for the pools that passed.

Registered: PREREGISTRATION.md. The read to trust: analyse_e1.py.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E0 = os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts")
for p in (HERE, E0, os.path.join(REPO, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import run_e0 as R0                  # noqa: E402
from p4_checks import check_v2       # noqa: E402

OUT_DIR = "/content/drive/MyDrive/afl/p4_e1"
CEILING = 0.90
csv_mod = __import__("csv")


def subset(stimuli, items=None, cells=None):
    return dict(stimuli,
                questions=[q for q in stimuli["questions"]
                           if items is None or q["item_id"] in items],
                cells=[c for c in stimuli["cells"]
                       if cells is None or c["cell_id"] in cells])


def headroom(out_path, stimuli):
    """None-cell delivery of each pool's own need, on that pool's questions."""
    csv_mod.field_size_limit(10 ** 8)
    pool_of = {q["item_id"]: q["pool"] for q in stimuli["questions"]}
    hits = {p: [] for p in stimuli["pools"]}
    with open(out_path, newline="", encoding="utf-8") as f:
        for r in csv_mod.DictReader(f):
            if r["cell_id"] == "none":
                pool = pool_of[r["item_id"]]
                hits[pool].append(int(check_v2(pool, r["answer"])["delivered"]))
    return {p: (sum(v) / len(v) if v else float("nan"), len(v))
            for p, v in hits.items()}


def gate(model_key, out_path, gate_path, stimuli):
    if os.path.exists(gate_path):
        with open(gate_path, encoding="utf-8") as f:
            g = json.load(f)
        print(f"gate already decided for {model_key}: kept {g['kept']}")
        return g
    rates = headroom(out_path, stimuli)
    kept = [p for p, (rate, n) in rates.items()
            if n == sum(1 for q in stimuli["questions"] if q["pool"] == p)
            and rate <= CEILING]
    g = {"model": model_key, "ceiling": CEILING, "kept": kept,
         "none_rate": {p: r for p, (r, n) in rates.items()}}
    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(g, f, indent=1)
    print("=" * 74)
    print(f"GATE 2 per pool, {model_key} (none-cell delivery of the pool's own need)")
    for p, (r, n) in rates.items():
        print(f"  {p:15}{r:6.2f}  n={n}  {'kept' if p in kept else 'DROPPED: at the ceiling'}")
    print("=" * 74)
    return g


def collect_all(model_key, generate, out_dir, stimuli, batch=R0.BATCH):
    out = os.path.join(out_dir, f"e1_{model_key}.csv")
    gate_path = os.path.join(out_dir, f"e1_{model_key}_gate.json")
    print("phase 1: the none cell for every question")
    R0.collect(model_key, generate, out, subset(stimuli, cells={"none"}), batch)
    g = gate(model_key, out, gate_path, stimuli)
    items = {q["item_id"] for q in stimuli["questions"] if q["pool"] in g["kept"]}
    print(f"phase 2: 16 more cells for {len(items)} questions")
    R0.collect(model_key, generate, out, subset(stimuli, items=items), batch)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(R0.MODELS))
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--batch", type=int, default=R0.BATCH)
    a = ap.parse_args()

    with open(os.path.join(HERE, "e1_stimuli.json"), encoding="utf-8") as f:
        stimuli = json.load(f)
    if a.smoke:
        sys.exit(0 if R0.smoke(R0.load_generator(a.model), stimuli_for_smoke())
                 else 1)
    os.makedirs(a.out_dir, exist_ok=True)
    if not a.analyse_only:
        collect_all(a.model, R0.load_generator(a.model), a.out_dir, stimuli, a.batch)
    import analyse_e1
    analyse_e1.main([os.path.join(a.out_dir, f"e1_{a.model}.csv")])


def stimuli_for_smoke():
    """The smoke check uses e0's first question; it tests the model path, not
    the stimuli, and e0's stimuli file ships in the same bundle."""
    with open(os.path.join(E0 if os.path.exists(os.path.join(E0, "e0_stimuli.json"))
                           else HERE, "e0_stimuli.json"), encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
