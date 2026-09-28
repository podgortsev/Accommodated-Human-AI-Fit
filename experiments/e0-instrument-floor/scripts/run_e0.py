#!/usr/bin/env python3
"""
run_e0.py - Paper 4, e0: does the delivery instrument read the need, or the
presence of a person?

    python run_e0.py qwen                  collect, then analyse
    python run_e0.py qwen --analyse-only   analyse the CSV already in OUT_DIR
    python run_e0.py qwen --smoke          GPU self-check, writes nothing

120 questions x 17 cells = 2,040 generations per model, greedy, one user turn.
Resumable: every batch is appended to the CSV in OUT_DIR and flushed, and a
rerun skips every (item_id, cell_id) already there. A dead session loses at
most one batch.

Stimuli: e0_stimuli.json (build_e0_stimuli.py). Instrument: scripts/p4_checks.py.
Registered decision: PREREGISTRATION.md. The read to trust: analyse_e0.py.
"""

import argparse
import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_e0_stimuli import prompt as make_prompt   # noqa: E402

MODELS = {
    "qwen":    "Qwen/Qwen2.5-7B-Instruct",
    "llama":   "meta-llama/Llama-3.1-8B-Instruct",
    "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
}
OUT_DIR = "/content/drive/MyDrive/afl/p4_e0"
LOAD_4BIT = True
MAX_NEW_TOKENS = 400
BATCH = 16
FIELDS = ["model", "item_id", "cell_id", "family", "key", "prompt", "answer",
          "n_new_tokens", "truncated"]
BNB_MIN = "0.46.1"


def plan(stimuli, limit=None):
    """Every prompt, as dicts, in a fixed order."""
    out = []
    for q in stimuli["questions"]:
        for c in stimuli["cells"]:
            out.append({"item_id": q["item_id"], "cell_id": c["cell_id"],
                        "family": c["family"], "key": c["key"],
                        "prompt": make_prompt(c["lead_in"], q["question"])})
    return out[:limit] if limit else out


def done_keys(path):
    if not os.path.exists(path):
        return set()
    csv.field_size_limit(10 ** 8)
    with open(path, newline="", encoding="utf-8") as f:
        return {(r["item_id"], r["cell_id"]) for r in csv.DictReader(f)}


def collect(model_key, generate, out_path, stimuli, batch=BATCH, limit=None,
            max_new_tokens=MAX_NEW_TOKENS):
    """generate(prompts, max_new_tokens) -> list of (text, n_new_tokens).

    Injected so the offline validator can run this exact function on a stub."""
    todo = [p for p in plan(stimuli, limit)
            if (p["item_id"], p["cell_id"]) not in done_keys(out_path)]
    # similar lengths together wastes less padding; order does not affect
    # greedy output
    # Sorted by length: similar lengths waste less padding, and the contrasts
    # that matter share batches, because need and neutral_long lead-ins are both
    # 16 words and label and neutral_short both 5. Whatever numerical drift left
    # padding causes is then shared by the two sides of each gate contrast.
    todo.sort(key=lambda p: len(p["prompt"]))
    new = not os.path.exists(out_path)
    total, t0 = len(todo), time.time()
    print(f"{model_key}: {total} prompts to generate, "
          f"{len(done_keys(out_path))} already in {out_path}")
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for s in range(0, total, batch):
            chunk = todo[s:s + batch]
            outs = generate([p["prompt"] for p in chunk], max_new_tokens)
            for p, (text, n_tok) in zip(chunk, outs):
                w.writerow({"model": model_key, **p, "answer": text,
                            "n_new_tokens": n_tok,
                            "truncated": int(n_tok >= max_new_tokens)})
            f.flush()
            os.fsync(f.fileno())
            k = s + len(chunk)
            if k % (batch * 5) == 0 or k == total:
                rate = k / max(time.time() - t0, 1e-9)
                print(f"  {k}/{total}  {rate * 60:.1f}/min  "
                      f"{(total - k) / max(rate, 1e-9) / 60:.0f} min left",
                      flush=True)
    return out_path


# ------------------------------------------------------------------ the model

def check_environment():
    import torch
    problems = []
    if not torch.cuda.is_available():
        problems.append("No GPU. Runtime > Change runtime type > T4 GPU.")
    elif LOAD_4BIT:
        try:
            import bitsandbytes
            have = [int("".join(c for c in x if c.isdigit()) or 0)
                    for x in bitsandbytes.__version__.split(".")]
            need = [int(x) for x in BNB_MIN.split(".")]
            if have < need:
                problems.append(f"bitsandbytes {bitsandbytes.__version__} < {BNB_MIN}")
        except ImportError as e:
            problems.append(f"bitsandbytes is not installed ({e}).")
    if problems:
        print("=" * 74)
        print("ENVIRONMENT NOT READY. Nothing was downloaded or run.")
        for p in problems:
            print("  " + p)
        print(f'  Fix: !pip install -U "bitsandbytes>={BNB_MIN}" accelerate '
              f"transformers, then Runtime > Restart session, rerun all cells.")
        print("=" * 74)
        sys.exit(1)


def load_generator(model_key):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    check_environment()
    name = MODELS[model_key]
    print(f"loading {name}, 4-bit={LOAD_4BIT}")
    tok = AutoTokenizer.from_pretrained(name, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    kw = {"device_map": "auto"}
    if LOAD_4BIT:
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(name, **kw)
    model.eval()

    def generate(prompts, max_new_tokens):
        chats = [tok.apply_chat_template([{"role": "user", "content": p}],
                                         tokenize=False, add_generation_prompt=True)
                 for p in prompts]
        enc = tok(chats, return_tensors="pt", padding=True,
                  add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=max_new_tokens,
                                 do_sample=False, pad_token_id=tok.pad_token_id)
        gen = out[:, enc["input_ids"].shape[1]:]
        res = []
        for row in gen:
            ids = [t for t in row.tolist() if t != tok.pad_token_id]
            if ids and ids[-1] == tok.eos_token_id:
                ids = ids[:-1]
            n = len(ids)
            res.append((tok.decode(ids, skip_special_tokens=True).strip(), n))
        return res

    return generate


LEAK = ("<|im_start|>", "<|im_end|>", "[INST]", "[/INST]", "<|eot_id|>",
        "<|start_header_id|>")


def smoke(generate, stimuli):
    """Run on the GPU before any row is written. Four prompts, generated one at
    a time and then as one batch. Stops on template leakage or empty answers;
    reports batch-against-single agreement as information."""
    pick = {"none", "need:screen_reader", "neutral_long:bread", "label:deaf"}
    ps = [p for p in plan(stimuli) if p["item_id"] == "q01" and p["cell_id"] in pick]
    single = [generate([p["prompt"]], 120)[0] for p in ps]
    batch = generate([p["prompt"] for p in ps], 120)
    problems = []
    print("=" * 74)
    print("SMOKE: four prompts, single and batched, 120 new tokens")
    print("=" * 74)
    for p, (t1, n1), (t2, n2) in zip(ps, single, batch):
        print(f"[{p['cell_id']}] {n1} tokens, batch identical: {t1 == t2}")
        print("   " + " / ".join(t1[:240].splitlines()))
        if not t1.strip() or n1 == 0:
            problems.append(f"{p['cell_id']}: empty answer")
        if any(x in t1 for x in LEAK):
            problems.append(f"{p['cell_id']}: chat template leaked into the answer")
    same = sum(a[0] == b[0] for a, b in zip(single, batch))
    print(f"batch equals single on {same} of {len(ps)} (drift from left padding is "
          f"shared by both sides of each contrast; recorded, not fatal)")
    print("SMOKE PROBLEM: " + "; ".join(problems) if problems else "SMOKE OK")
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(MODELS))
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--batch", type=int, default=BATCH)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    out = os.path.join(a.out_dir, f"e0_{a.model}.csv")
    with open(os.path.join(HERE, "e0_stimuli.json"), encoding="utf-8") as f:
        stimuli = json.load(f)
    if a.smoke:
        sys.exit(0 if smoke(load_generator(a.model), stimuli) else 1)
    if not a.analyse_only:
        collect(a.model, load_generator(a.model), out, stimuli, a.batch, a.limit)
    import analyse_e0
    analyse_e0.main([out])


if __name__ == "__main__":
    main()
