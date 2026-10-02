#!/usr/bin/env python3
"""
p4_gen.py - generation for any number of turns, and a resumable collector for
jobs that are not a question x cell grid. Used by e3 (a follow-up turn replayed
after the model's own first answer) and e4 (a single turn with a keyed task).

    generate = load_chat_generator("qwen")
    generate([[{"role": "user", "content": "..."}], ...], max_new_tokens)
        -> [(text, n_new_tokens), ...]
    collect_jobs(model_key, generate, out_path, jobs, meta_fields)

The model loading is run_e0's, so every Paper 4 experiment uses the same
settings: 4-bit, greedy, left padding, chat template, no system prompt.
"""

import csv
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "..", "experiments", "e0-instrument-floor", "scripts")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

import run_e0 as R0     # noqa: E402

BATCH = R0.BATCH
MAX_NEW_TOKENS = R0.MAX_NEW_TOKENS


def load_chat_generator(model_key):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    R0.check_environment()
    name = R0.MODELS[model_key]
    print(f"loading {name}, 4-bit={R0.LOAD_4BIT}")
    tok = AutoTokenizer.from_pretrained(name, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    kw = {"device_map": "auto"}
    if R0.LOAD_4BIT:
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(name, **kw)
    model.eval()

    def generate(conversations, max_new_tokens):
        chats = [tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True)
                 for c in conversations]
        enc = tok(chats, return_tensors="pt", padding=True,
                  add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=max_new_tokens,
                                 do_sample=False, pad_token_id=tok.pad_token_id)
        res = []
        for row in out[:, enc["input_ids"].shape[1]:]:
            ids = [t for t in row.tolist() if t != tok.pad_token_id]
            if ids and ids[-1] == tok.eos_token_id:
                ids = ids[:-1]
            res.append((tok.decode(ids, skip_special_tokens=True).strip(), len(ids)))
        return res

    return generate


def single_turn(generate):
    """Adapter so run_e0.smoke can check a chat generator."""
    return lambda prompts, m: generate([[{"role": "user", "content": p}]
                                        for p in prompts], m)


def done_ids(path):
    if not os.path.exists(path):
        return set()
    csv.field_size_limit(10 ** 8)
    with open(path, newline="", encoding="utf-8") as f:
        return {r["job_id"] for r in csv.DictReader(f)}


def collect_jobs(model_key, generate, out_path, jobs, meta_fields, batch=BATCH,
                 max_new_tokens=MAX_NEW_TOKENS):
    """jobs: dicts with job_id, messages (list of chat turns) and meta_fields.
    Appends and flushes every batch; a rerun skips every job_id already written."""
    fields = ["model", "job_id"] + list(meta_fields) + ["answer", "n_new_tokens",
                                                        "truncated"]
    have = done_ids(out_path)
    todo = [j for j in jobs if j["job_id"] not in have]
    todo.sort(key=lambda j: sum(len(m["content"]) for m in j["messages"]))
    new = not os.path.exists(out_path)
    total, t0 = len(todo), time.time()
    print(f"{model_key}: {total} jobs to generate, {len(have)} already in {out_path}")
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        for s in range(0, total, batch):
            chunk = todo[s:s + batch]
            outs = generate([j["messages"] for j in chunk], max_new_tokens)
            for j, (text, n) in zip(chunk, outs):
                w.writerow({"model": model_key, "job_id": j["job_id"],
                            **{k: j[k] for k in meta_fields}, "answer": text,
                            "n_new_tokens": n, "truncated": int(n >= max_new_tokens)})
            f.flush()
            os.fsync(f.fileno())
            k = s + len(chunk)
            if k % (batch * 5) == 0 or k == total:
                rate = k / max(time.time() - t0, 1e-9)
                print(f"  {k}/{total}  {rate * 60:.1f}/min  "
                      f"{(total - k) / max(rate, 1e-9) / 60:.0f} min left", flush=True)
    return out_path
