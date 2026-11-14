#!/usr/bin/env python3
"""Run the handbook test questions against one or more LLMs and record the results.

For every (model, question) pair this records the answer, the retrieved pages,
latency, and two automatic signals:
  * retrieval_hit  - did any expected handbook page appear in the top-k chunks?
  * fact_coverage  - share of the question's key facts mentioned in the answer
These are approximate. The final judgement (correct / incomplete / incorrect /
ambiguous) is made by hand in the `label` column of results.csv.

Example:
    python evaluate.py --models qwen2.5:0.5b qwen2.5:1.5b qwen2.5:3b
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
from datetime import datetime
from pathlib import Path

import yaml

from rag.config import PROJECT_ROOT, Settings
from rag.pipeline import ask, get_llm, retrieve
from rag.store import load_or_build

QUESTIONS_FILE = PROJECT_ROOT / "eval" / "questions.yaml"
RESULTS_DIR = PROJECT_ROOT / "eval" / "results"


def fact_coverage(answer: str, key_facts: list[str]) -> float | None:
    if not key_facts:
        return None
    text = answer.lower()
    hits = sum(any(alt.strip().lower() in text for alt in fact.split("|")) for fact in key_facts)
    return round(hits / len(key_facts), 2)


def retrieval_hit(sources: list[dict], expected_pages: list[int]) -> bool | None:
    if not expected_pages:
        return None
    return any(s.get("page") in expected_pages for s in sources)


def evidence_hit(sources: list[dict], evidence: str | None) -> bool | None:
    """Chunk-level retrieval: did a retrieved chunk contain the answer's evidence phrase?"""
    if not evidence:
        return None
    return any(alt in s["content"] for s in sources for alt in evidence.split("|"))


def mean(values: list[float]) -> float | None:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else None


def truncate(answer: str, limit: int = 2500) -> str:
    if len(answer) <= limit:
        return answer
    return answer[:limit] + f"\n\n*[... truncated: answer was {len(answer):,} characters]*"


LABELS = ("correct", "incomplete", "ambiguous", "incorrect")


def apply_labels(rows: list[dict], labels_file: Path) -> bool:
    """Merge hand labels from labels.yaml ({qid: {model: [label, note]}}) into rows."""
    if not labels_file.exists():
        return False
    labels = yaml.safe_load(labels_file.read_text(encoding="utf-8")) or {}
    for r in rows:
        label, note = labels.get(r["id"], {}).get(r["model"], ["", ""])
        if label and label not in LABELS:
            raise SystemExit(f"Unknown label {label!r} for {r['id']} / {r['model']}")
        r["label"], r["label_note"] = label, note
    return True


def write_csv(rows: list[dict], path: Path) -> None:
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_config(cfg: Settings) -> dict:
    return {
        "embed_model": cfg.embed_model, "chunk_size": cfg.chunk_size,
        "chunk_overlap": cfg.chunk_overlap, "top_k": cfg.top_k,
        "temperature": cfg.temperature, "prompt_style": cfg.prompt_style,
        "score_threshold": cfg.score_threshold, "max_tokens": cfg.max_tokens,
    }


def write_summary(rows: list[dict], cfg: Settings, path: Path) -> None:
    models = list(dict.fromkeys(r["model"] for r in rows))
    # Describe the settings the run actually used, not the current defaults.
    config_file = path.parent / "config.json"
    c = json.loads(config_file.read_text()) if config_file.exists() else run_config(cfg)
    lines = [
        "# Handbook chatbot evaluation",
        "",
        f"- Run: `{path.parent.name}`",
        (f"- Embeddings: `{c['embed_model']}`, chunk {c['chunk_size']}/{c['chunk_overlap']}, "
        f"top-k {c['top_k']}, temperature {c['temperature']}, prompt `{c['prompt_style']}`, "
        f"threshold {c['score_threshold']}, max tokens {c['max_tokens']}"),
        f"- Questions: {len(rows) // max(len(models), 1)}",
        "",
        ("| Model | Page hit | Chunk hit | Avg fact coverage | Median latency (s) "
        "| Max latency (s) | Fallbacks |"),
        "|---|---|---|---|---|---|---|",
    ]
    for m in models:
        mr = [r for r in rows if r["model"] == m]
        hits = [r["retrieval_hit"] for r in mr if r["retrieval_hit"] is not None]
        chunk_hits = [r.get("evidence_hit") for r in mr if r.get("evidence_hit") is not None]
        chunk_col = f"{sum(chunk_hits)}/{len(chunk_hits)}" if chunk_hits else "—"
        lines.append(
            f"| `{m}` | {sum(hits)}/{len(hits)} | {chunk_col} | "
            f"{mean([r['fact_coverage'] for r in mr])} | "
            f"{statistics.median(r['latency_s'] for r in mr)} | "
            f"{max(r['latency_s'] for r in mr)} | {sum(r['used_fallback'] for r in mr)} |"
        )
    if any(r.get("label") for r in rows):
        lines += [
            "",
            "## Hand labels",
            "",
            "| Model | " + " | ".join(LABELS) + " |",
            "|---|" + "---|" * len(LABELS),
        ]
        for m in models:
            mr = [r for r in rows if r["model"] == m]
            counts = [sum(r.get("label") == lab for r in mr) for lab in LABELS]
            lines.append(f"| `{m}` | " + " | ".join(map(str, counts)) + " |")
    lines += ["", "## Answers", ""]
    for qid in dict.fromkeys(r["id"] for r in rows):
        qr = [r for r in rows if r["id"] == qid]
        first = qr[0]
        lines += [
            f"### `{qid}` — {first['question']}",
            "",
            f"*Category:* {first['category']} · *Expected pages:* {first['expected_pages'] or '—'}",
            "",
            f"> **Reference:** {first['reference']}",
            "",
        ]
        for r in qr:
            lines += [
                (f"**{r['model']}** (retrieved pages {r['retrieved_pages']}, "
                f"hit={r['retrieval_hit']}, chunk_hit={r.get('evidence_hit')}, coverage={r['fact_coverage']}, {r['latency_s']}s)"),
                "",
                *([f"*Label: **{r['label']}** — {r['label_note']}*", ""] if r.get("label") else []),
                truncate(r["answer"].strip()),
                "",
            ]
    path.write_text("\n".join(lines), encoding="utf-8")


def retrieval_report(db, cfg: Settings, questions: list[dict], probes: dict) -> None:
    """Retrieval-only evaluation: seconds instead of an hour, useful for sweeps."""
    print(f"chunk {cfg.chunk_size}/{cfg.chunk_overlap}, top-k {cfg.top_k}, "
          f"threshold {cfg.score_threshold}, index {cfg.index_dir.name}")
    page_hits, chunk_hits, top_scores = [], [], []
    for q in questions:
        sources = retrieve(q["question"], db, cfg)
        if not q.get("pages"):
            continue
        page_hits.append(retrieval_hit(sources, q["pages"]))
        chunk = evidence_hit(sources, q.get("evidence"))
        if chunk is not None:
            chunk_hits.append(chunk)
        top_scores.append(sources[0]["score"])
        if chunk is False:
            print(f"  chunk miss: {q['id']} (pages {[s['page'] for s in sources]})")
    print(f"page hit {sum(page_hits)}/{len(page_hits)} | chunk hit "
          f"{sum(chunk_hits)}/{len(chunk_hits)} | in-scope best-chunk score min "
          f"{min(top_scores):.3f}, median {statistics.median(top_scores):.3f}")
    for kind, items in probes.items():
        scores = [retrieve(p, db, cfg)[0]["score"] for p in items]
        caught = sum(sc < cfg.score_threshold for sc in scores)
        print(f"probes {kind}: fallback {caught}/{len(items)} | best-chunk scores "
              + ", ".join(f"{sc:.3f}" for sc in scores))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models", nargs="+", default=["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b"])
    parser.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data" / "handbooks")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="0 = deterministic, so runs are comparable (default 0)")
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--prompt", choices=["baseline", "strict"],
                        help="Prompt style (default: PROMPT_STYLE setting, i.e. strict)")
    parser.add_argument("--chunk-size", type=int)
    parser.add_argument("--chunk-overlap", type=int)
    parser.add_argument("--retrieval-only", action="store_true",
                        help="Only measure retrieval (page/chunk hits, probe scores); no LLM")
    parser.add_argument("--only", nargs="*", help="Run only these question ids")
    parser.add_argument("--tag", default="", help="Suffix for the results folder name")
    parser.add_argument("--summarize", type=Path,
                        help="Only regenerate summary.md for an existing results folder")
    parser.add_argument("--resume", type=Path,
                        help="Existing results folder to continue (skips finished answers)")
    args = parser.parse_args()

    cfg = Settings()
    cfg.data_dir = args.data_dir.resolve()
    cfg.temperature = args.temperature
    if args.prompt:
        cfg.prompt_style = args.prompt
    if args.top_k:
        cfg.top_k = args.top_k
    if args.chunk_size:
        cfg.chunk_size = args.chunk_size
    if args.chunk_overlap is not None:
        cfg.chunk_overlap = args.chunk_overlap

    if args.summarize:
        rows = json.loads((args.summarize / "results.json").read_text(encoding="utf-8"))
        if apply_labels(rows, args.summarize / "labels.yaml"):
            write_csv(rows, args.summarize / "results.csv")
        write_summary(rows, cfg, args.summarize / "summary.md")
        print(f"Rewrote summary.md / results.csv in {args.summarize}")
        return

    spec = yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))
    questions = [q for q in spec["questions"] if not args.only or q["id"] in args.only]

    db = load_or_build(cfg)
    if args.retrieval_only:
        retrieval_report(db, cfg, questions, spec.get("probes", {}))
        return
    if args.resume:
        out_dir = args.resume.resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        out_dir = RESULTS_DIR / (stamp + (f"-{args.tag}" if args.tag else ""))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Answers are appended to a JSONL file as they arrive, so an interrupted run
    # loses at most one answer and can be continued with --resume.
    partial = out_dir / "results.jsonl"
    rows: list[dict] = (
        [json.loads(line) for line in partial.read_text().splitlines() if line.strip()]
        if partial.exists() else []
    )
    done = {(r["model"], r["id"]) for r in rows}
    (out_dir / "config.json").write_text(json.dumps(run_config(cfg), indent=2))
    total = len(args.models) * len(questions)
    print(f"Writing to {out_dir.relative_to(PROJECT_ROOT)}/ ({len(done)}/{total} already done)",
          flush=True)

    for model in args.models:
        cfg.llm_model = model
        llm = get_llm(cfg)
        print(f"\n=== {model} ===", flush=True)
        for q in questions:
            if (model, q["id"]) in done:
                continue
            start = time.perf_counter()
            result = ask(q["question"], db, llm, cfg)
            latency = round(time.perf_counter() - start, 1)
            row = {
                "model": model,
                "id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "reference": " ".join(q["reference"].split()),
                "expected_pages": q.get("pages", []),
                "retrieved_pages": [s.get("page") for s in result["sources"]],
                "retrieval_hit": retrieval_hit(result["sources"], q.get("pages", [])),
                "evidence_hit": evidence_hit(result["sources"], q.get("evidence")),
                "fact_coverage": fact_coverage(result["answer"], q.get("key_facts", [])),
                "top_score": result["top_score"],
                "avg_score": result["avg_score"],
                "used_fallback": result["used_fallback"],
                "latency_s": latency,
                "answer": result["answer"],
                "label": "",  # filled in by hand: correct / incomplete / incorrect / ambiguous
            }
            rows.append(row)
            with open(partial, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"  [{len(rows)}/{total}] {q['id']:<26} hit={row['retrieval_hit']!s:<5} "
                  f"cov={row['fact_coverage']!s:<5} {latency:>5}s", flush=True)

    (out_dir / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    write_csv(rows, out_dir / "results.csv")
    write_summary(rows, cfg, out_dir / "summary.md")
    print(f"\nSaved results to {out_dir.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
