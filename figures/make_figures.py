#!/usr/bin/env python3
"""
make_figures.py - the paper's two figures, computed from the committed answers.

    python figures/make_figures.py

No constants are transcribed: every value is computed here from the CSVs with
the paper's instrument (p4_checks version 2, 250-word window), so a figure
cannot drift from the data. Colours are the validated reference palette
(categorical blue and orange; an ordinal blue ramp, steps 250, 450, 650),
checked with the palette validator before use, on the white page surface.

    fig_deaf_parts.png   e2: text route offered and phone instruction kept,
                         after a neutral detail and after the deafness need
    fig_pushback.png     e3: share of follow-ups still telling the person to
                         phone, by follow-up
"""

import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
EXP = os.path.join(ROOT, "experiments")
sys.path.insert(0, os.path.join(EXP, "shared", "scripts"))
from p4_checks import check_v2    # noqa: E402

MODELS = ("qwen", "llama", "mistral")
NAMES = {"qwen": "Qwen2.5-7B", "llama": "Llama-3.1-8B", "mistral": "Mistral-7B"}
SURFACE, INK, INK2, GRID = "#ffffff", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"
RAMP = ("#86b6ef", "#2a78d6", "#104281")
csv.field_size_limit(10 ** 8)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "savefig.facecolor": SURFACE})


def rows(exp, stem, model):
    path = os.path.join(EXP, exp, "outputs", model, f"{stem}_{model}.csv")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def deaf_parts():
    out = {}
    for m in MODELS:
        acc = {"neutral": [], "need": []}
        for r in rows("e2-deaf-contact", "e2", m):
            if r["cell_id"] == "need:deaf":
                key = "need"
            elif r["cell_id"].startswith("neutral_long:"):
                key = "neutral"
            else:
                continue
            c = check_v2("deaf", r["answer"])
            acc[key].append((int(c["offers_text_route"]), int(not c["no_phone_instruction"])))
        out[m] = {k: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v))
                  for k, v in acc.items()}
    return out


def pushback():
    import json
    with open(os.path.join(EXP, "e3-pushback", "scripts", "e3_turn1.json"), encoding="utf-8") as f:
        t1 = json.load(f)["turn1"]
    phone = lambda s: int(not check_v2("deaf", s)["no_phone_instruction"])
    out = {}
    for m in MODELS:
        kept = {f"{t['source']}:{t['item_id']}" for t in t1[m] if phone(t["turn1"])}
        acc = {"neutral": [], "restate": [], "specific": []}
        for r in rows("e3-pushback", "e3", m):
            if f"{r['source']}:{r['item_id']}" in kept:
                acc[r["follow_up"]].append(phone(r["answer"]))
        out[m] = {k: sum(v) / len(v) for k, v in acc.items()}
    return out


def style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def fig_deaf_parts(d):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6), sharey=True)
    panels = (("Text route offered", 0, BLUE), ("Still told to phone", 1, ORANGE))
    ys = list(range(len(MODELS)))[::-1]
    for ax, (title, i, colour) in zip(axes, panels):
        style(ax)
        for y, m in zip(ys, MODELS):
            a, b = d[m]["neutral"][i], d[m]["need"][i]
            ax.plot([a, b], [y, y], color=colour, linewidth=2, alpha=0.45, zorder=1)
            ax.scatter([a], [y], s=46, facecolor=SURFACE, edgecolor=colour, linewidth=2, zorder=2)
            ax.scatter([b], [y], s=46, color=colour, edgecolor=SURFACE, linewidth=2, zorder=3)
            # the smaller value is labelled on its left, the larger on its right,
            # so labels never collide when the two points are close
            lo, hi = (a, b) if a <= b else (b, a)
            for x, side in ((lo, "right"), (hi, "left")):
                ink = INK2 if x == a else INK
                off = -0.022 if side == "right" else 0.022
                ax.text(x + off, y, f"{x:.2f}", ha=side, va="center", color=ink, fontsize=8)
        ax.set_xlim(0, 0.8)
        ax.set_ylim(-0.6, len(MODELS) - 0.3)
        ax.set_title(title, loc="left", color=INK, fontsize=9.5, fontweight="bold")
        ax.set_xlabel("share of answers")
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([NAMES[m] for m in MODELS], color=INK)
    h1 = axes[0].scatter([], [], s=46, facecolor=SURFACE, edgecolor=INK2, linewidth=2)
    h2 = axes[0].scatter([], [], s=46, color=INK2)
    fig.legend([h1, h2], ["after a neutral detail", "after “I cannot hear …”"],
               loc="lower center", ncol=2, frameon=False, fontsize=8.5,
               bbox_to_anchor=(0.55, -0.04), labelcolor=INK2)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(os.path.join(HERE, "fig_deaf_parts.png"), dpi=300)
    plt.close(fig)


def fig_pushback(p):
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    kinds = (("neutral", "“Could you go over it once more?”"),
             ("restate", "“As I said, I cannot hear.”"),
             ("specific", "“Phone calls will not work for me.”"))
    w, gap = 0.26, 0.02
    for k, (kind, label) in enumerate(kinds):
        xs = [i + (k - 1) * (w + gap) for i in range(len(MODELS))]
        vals = [p[m][kind] for m in MODELS]
        ax.bar(xs, vals, width=w, color=RAMP[k], label=label, zorder=2)
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.015, f"{v:.2f}", ha="center", va="bottom", color=INK2, fontsize=7.5)
    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([NAMES[m] for m in MODELS], color=INK)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("still told to phone")
    ax.legend(frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5),
              labelcolor=INK2, title="second turn", title_fontsize=8, alignment="left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_pushback.png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    d = deaf_parts()
    fig_deaf_parts(d)
    p = pushback()
    fig_pushback(p)
    for m in MODELS:
        print(m, "deaf parts", {k: tuple(round(x, 2) for x in v) for k, v in d[m].items()},
              "| pushback", {k: round(v, 2) for k, v in p[m].items()})
