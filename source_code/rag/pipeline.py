"""Retrieve relevant chunks and generate an answer with the LLM."""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM

from .config import Settings

PROMPT_TEMPLATE = """You are a helpful AI assistant that answers questions based on provided documents.

CONTEXT FROM DOCUMENTS:
{context}
---
QUESTION: {question}

INSTRUCTIONS:
1. If the context contains relevant information, answer based on that.
2. If the context is insufficient, use your general knowledge.
3. Be concise - 2-4 sentences unless more detail is needed.

ANSWER:"""


def list_models(cfg: Settings) -> list[str]:
    """Names of models installed in the Ollama server (excluding embedding models)."""
    try:
        with urllib.request.urlopen(f"{cfg.ollama_url}/api/tags", timeout=3) as resp:
            names = [m["name"] for m in json.load(resp).get("models", [])]
    except OSError:
        return []
    return sorted(n for n in names if "embed" not in n)


def get_llm(cfg: Settings) -> OllamaLLM:
    return OllamaLLM(model=cfg.llm_model, base_url=cfg.ollama_url, temperature=cfg.temperature)


def retrieve(question: str, db: Chroma, cfg: Settings) -> list[dict[str, Any]]:
    results = db.similarity_search_with_score(question, k=cfg.top_k)
    return [
        {
            "source": str(doc.metadata.get("source", "Unknown")),
            "page": doc.metadata.get("page"),
            # Chroma returns an L2 distance; map it to a (0, 1] similarity.
            "score": round(1 / (1 + distance), 4),
            "content": doc.page_content,
        }
        for doc, distance in results
    ]


def format_source(s: dict[str, Any]) -> str:
    return f"{s['source']} p.{s['page']}" if s.get("page") else s["source"]


def build_prompt(question: str, sources: list[dict[str, Any]], used_fallback: bool) -> str:
    if used_fallback:
        context = "No sufficiently relevant documents found. Use your general knowledge."
    else:
        context = "\n\n---\n\n".join(f"[{format_source(s)}]\n{s['content']}" for s in sources)
    return PROMPT_TEMPLATE.replace("{context}", context).replace("{question}", question)


def prepare(question: str, db: Chroma, cfg: Settings) -> dict[str, Any]:
    """Retrieval half of the pipeline: sources, relevance and the final prompt."""
    sources = retrieve(question, db, cfg)
    avg_score = sum(s["score"] for s in sources) / len(sources) if sources else 0.0
    used_fallback = not sources or avg_score < cfg.score_threshold
    return {
        "sources": sources,
        "avg_score": round(avg_score, 4),
        "used_fallback": used_fallback,
        "prompt": build_prompt(question, sources, used_fallback),
    }


def ask(question: str, db: Chroma, llm: OllamaLLM, cfg: Settings) -> dict[str, Any]:
    result = prepare(question, db, cfg)
    result["answer"] = llm.invoke(result["prompt"]).strip()
    return result
