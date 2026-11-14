#!/usr/bin/env python3
"""Command-line RAG Q&A.

Examples:
    python run.py
    python run.py -q "Where is the FUV campus?"
    python run.py --data-dir data/handbooks --rebuild -q "What are the CS core courses?"
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rag.config import Settings
from rag.pipeline import ask, format_source, get_llm
from rag.store import load_or_build

SAMPLE_QUESTION = "How many students are there at Fulbright?"


def main() -> None:
    parser = argparse.ArgumentParser(description="Local RAG Q&A over TXT/PDF documents")
    parser.add_argument("-q", "--question", default=SAMPLE_QUESTION)
    parser.add_argument("--data-dir", type=Path, help="Folder of documents to index")
    parser.add_argument("--vector-store", type=Path, help="Where to persist the Chroma index")
    parser.add_argument("--model", help="Ollama LLM to answer with (e.g. qwen2.5:1.5b)")
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--prompt", choices=["baseline", "strict"], help="Prompt style")
    parser.add_argument("--rebuild", action="store_true", help="Re-index from scratch")
    args = parser.parse_args()

    cfg = Settings()
    if args.data_dir:
        cfg.data_dir = args.data_dir.resolve()
    if args.vector_store:
        cfg.vector_store = args.vector_store.resolve()
    if args.model:
        cfg.llm_model = args.model
    if args.top_k:
        cfg.top_k = args.top_k
    if args.prompt:
        cfg.prompt_style = args.prompt

    print(f"Embeddings: {cfg.embed_model} | LLM: {cfg.llm_model} | Ollama: {cfg.ollama_url}")
    db = load_or_build(cfg, rebuild=args.rebuild)
    llm = get_llm(cfg)

    print(f"Q: {args.question}")
    result = ask(args.question, db, llm, cfg)
    print(f"\nA: {result['answer']}\n")
    if result["used_fallback"]:
        print("(answered from model knowledge — no relevant documents found)")
    else:
        print(f"Sources (best score {result['top_score']}):")
        for s in result["sources"][:3]:
            print(f"   {format_source(s)}  score={s['score']}")


if __name__ == "__main__":
    main()
