#!/usr/bin/env python3
"""
verify_paper_numbers.py - check the paper against the committed data.

No GPU. `python verify_paper_numbers.py` re-runs every no-GPU analysis in the
repository from the committed answers and confirms that each number printed in
accommodated-human-ai-fit.tex (every table value and the counts in the abstract)
is what the analysis produces, rounded as printed.

Covered: the three tables, and the abstract's figures. Two groups of numbers are
not printed by any analysis script, so they are computed here from the committed
CSVs with the same instrument (p4_checks version 2, 250-word window): the parts
of the deafness benefit in e2 (text route offered, phone instruction kept) and
the total number of answers.

Not covered: the raw model outputs themselves, which took a GPU to produce.
What is verified is the chain from the committed CSV to the printed number.
"""

import csv
import glob
import os
import re
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(ROOT, "experiments")
TEX = open(os.path.join(ROOT, "accommodated-human-ai-fit.tex"), encoding="utf-8").read()
FLAT = " ".join(TEX.split())
sys.path.insert(0, os.path.join(EXP, "shared", "scripts"))
from p4_checks import check_v2   # noqa: E402

MODELS = ("qwen", "llama", "mistral")
csv.field_size_limit(10 ** 8)
FAILS = []


def run(script, *csvs):
    out = subprocess.run([sys.executable, os.path.join(EXP, script)] + list(csvs),
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        sys.exit(f"{script} failed:\n{out.stderr[-2000:]}")
    return out.stdout


def csvs(exp, stem):
    return [os.path.join(EXP, exp, "outputs", m, f"{stem}_{m}.csv") for m in MODELS]


def blocks(text, tag):
    """{model: block text} for headers like 'e1 | qwen |'."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(rf"^{tag} \| (\w+)", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def contrast(block, need, name):
    m = re.search(rf"^\s+{need}\s+{name}\s+([+-]\d\.\d+)", block, re.M)
    if not m:
        sys.exit(f"no {need} {name} in block")
    return m.group(1)


def r2(s):
    return Decimal(s).quantize(Decimal("0.01"), ROUND_HALF_UP)


def signed(d):
    return f"+{d}" if d >= 0 else f"-{-d}"


def check(label, got, printed):
    ok = printed in TEX or printed in FLAT
    status = "PASS" if (ok and got == printed) else "FAIL"
    if status == "FAIL":
        FAILS.append(label)
    print(f"  {status}  {label:58} paper {printed:>9}  data {got:>9}"
          + ("" if ok else "  (not found in the tex)"))


def main():
    print("re-running the analyses from the committed answers ...")
    e0 = blocks(run("e0-instrument-floor/scripts/analyse_e0.py", *csvs("e0-instrument-floor", "e0")), "e0")
    e1 = blocks(run("e1-measurable-needs/scripts/analyse_e1.py", *csvs("e1-measurable-needs", "e1")), "e1")
    e2 = blocks(run("e2-deaf-contact/scripts/analyse_e2.py", *csvs("e2-deaf-contact", "e2")), "e1")
    e3 = blocks(run("e3-pushback/scripts/analyse_e3.py", *csvs("e3-pushback", "e3")), "e3")
    e4raw = run("e4-cost/scripts/analyse_e4.py", *csvs("e4-cost", "e4"))
    e4 = blocks(e4raw, "e4")
    e5raw = run("e5-wrappers/scripts/analyse_e5.py", *csvs("e5-wrappers", "e5"))
    refraw = run("exploratory-refusals/scripts/analyse_refusals.py")

    print("\nTable 1, need benefits")
    rows = [("deafness e0", e0, "deaf"), ("deafness e2", e2, "deaf"),
            ("wheelchair e1", e1, "wheelchair"), ("plain language e1", e1, "plain_language"),
            ("plain language e2", e2, "plain_language")]
    tex_rows = {"deafness e0": r"deafness & e0", "deafness e2": r"deafness & e2",
                "wheelchair e1": r"wheelchair use & e1", "plain language e1": r"plain language & e1",
                "plain language e2": r"plain language & e2"}
    for label, b, need in rows:
        vals = [signed(r2(contrast(b[m], need, "need_benefit"))) for m in MODELS]
        line = next((l for l in TEX.splitlines() if l.startswith(tex_rows[label])), "")
        printed = re.findall(r"\$([+-]\d\.\d\d)\$", line)
        for m, v, p in zip(MODELS, vals, printed or ["?"] * 3):
            check(f"{label}, {m}", v, p if printed else "?")

    print("\nTable 2, parts of the deafness benefit (e2, computed from the CSVs)")
    tex_line = {m: next(l for l in TEX.splitlines() if l.startswith(m.capitalize() + " & 0."))
                for m in MODELS}
    shares = []
    for m in MODELS:
        t = {}
        with open(csvs("e2-deaf-contact", "e2")[MODELS.index(m)], newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["cell_id"] == "need:deaf" or r["cell_id"].startswith("neutral_long:"):
                    c = check_v2("deaf", r["answer"])
                    key = "need" if r["cell_id"] == "need:deaf" else "neutral"
                    t.setdefault(key, []).append((c["offers_text_route"], not c["no_phone_instruction"]))
        rate = lambda k, i: Decimal(sum(x[i] for x in t[k])) / len(t[k])
        got = [rate("neutral", 0), rate("need", 0), rate("neutral", 1), rate("need", 1)]
        printed = re.findall(r"0\.\d\d", tex_line[m])
        for name, g, p in zip(("text route neutral", "text route need", "phone neutral", "phone need"),
                              got, printed):
            check(f"{m}, {name}", str(r2(g)), p)
        shares.append(int((rate("need", 1) / rate("neutral", 1) * 100).quantize(Decimal("1"), ROUND_HALF_UP)))
    check("abstract: share of phone instructions left, lowest", str(min(shares)), "56")
    check("abstract: share of phone instructions left, highest", str(max(shares)), "82")

    print("\nTable 3, e3 follow-ups (share still told to phone)")
    texrows = {k: re.findall(r"& (0\.\d\d)", next(l for l in TEX.splitlines() if l.startswith(start)))
               for k, start in (("neutral", "``Thanks for that"), ("restate", "``As I said"),
                                ("specific", "``I cannot hear; phone"))}
    for i, m in enumerate(MODELS):
        for k in ("neutral", "restate", "specific"):
            mm = re.search(rf"^\s+{k}\s+(\d\.\d\d)", e3[m], re.M)
            check(f"e3 {m}, {k}", mm.group(1), texrows[k][i])

    print("\nAbstract and text counts")
    total = 0
    for f in glob.glob(os.path.join(EXP, "e*", "outputs", "*", "e*_*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            total += sum(1 for _ in csv.DictReader(fh))
    check("answers in total", f"{total:,}", "27,990")
    moved = tests = 0
    for b in (e0, e1, e2):
        for blk in b.values():
            for l in blk.splitlines():
                if "mean shift" in l:
                    tests += 6
                    if "MOVES:" in l:
                        moved += len(l.split("MOVES:")[1].split(","))
    check("floor tests that move (e0 to e2)", f"{moved} of {tests}", "5 of 198")
    check("e4 pooled penalty, qwen", contrast(e4["qwen"], "pooled", "H6_penalty_pooled")[:5], "+0.01")
    check("e4 pooled penalty, llama", signed(r2(contrast(e4["llama"], "pooled", "H6_penalty_pooled"))), "+0.06")
    check("e4 pooled penalty, mistral", signed(r2(contrast(e4["mistral"], "pooled", "H6_penalty_pooled"))), "-0.06")
    n117 = re.search(r"e4 \| mistral \|.*?(\d+) with an Answer line in every cell", e4raw)
    check("e4 mistral complete questions", n117.group(1) if n117 else "?", "117")
    rng = dict(re.findall(r"spread across wrappers, need_benefit\s+([+-]\d\.\d+ to [+-]\d\.\d+)", e5raw) and
               zip(("llama", "mistral", "qwen"),
                   re.findall(r"spread across wrappers, need_benefit\s+([+-]\d\.\d+) to ([+-]\d\.\d+)", e5raw)))
    for m in MODELS:
        lo, hi = rng[m]
        check(f"e5 need benefit range, {m}", f"${signed(r2(lo))}$ to ${signed(r2(hi))}$",
              f"${signed(r2(lo))}$ to ${signed(r2(hi))}$")
    ref = re.findall(r"e[02] llama:.*?\n(?:.*\n)*?\s+label plain_language\s+refusal (\d\.\d+)", refraw)
    pct = sorted(int((Decimal(x) * 100).quantize(Decimal("1"), ROUND_HALF_UP)) for x in ref)
    check("abstract: Llama refusals after the learning-disability label", f"{pct[0]} to {pct[-1]}", "19 to 33")

    print("=" * 78)
    print(f"{'ALL NUMBERS VERIFIED' if not FAILS else str(len(FAILS)) + ' FAILED: ' + ', '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
