"""Retrieve relevant chunks and generate an answer with the LLM."""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM

from .config import Settings

PROMPTS: dict[str, str] = {}

# The course baseline prompt, unchanged.
PROMPTS["baseline"] = """You are a helpful AI assistant that answers questions based on provided documents.

CONTEXT FROM DOCUMENTS:
{context}
---
QUESTION: {question}

INSTRUCTIONS:
1. If the context contains relevant information, answer based on that.
2. If the context is insufficient, use your general knowledge.
3. Be concise - 2-4 sentences unless more detail is needed.

ANSWER:"""

# Answer only from the documents (D-18): no general-knowledge fallback, explicit
# "not found" phrase, attention to which section a passage belongs to, citations.
NOT_FOUND = "I couldn't find that in the documents."
PROMPTS["strict"] = """You answer questions using ONLY the document excerpts below.
Each excerpt starts with its source tag in square brackets.

DOCUMENT EXCERPTS:
{context}
---
QUESTION: {question}

RULES:
1. Use only facts stated in the excerpts. Do not use outside knowledge and do not guess.
2. If the excerpts do not contain the answer, reply exactly: "{not_found}"
3. Check that the excerpt you rely on is about exactly what was asked
   (for example major vs. minor requirements, or the right course code).
4. Answer directly in 1-4 sentences or a short list, then cite the source tag(s) you used.

ANSWER:""".replace("{not_found}", NOT_FOUND)

# Kept for backwards compatibility with code that imports it.
PROMPT_TEMPLATE = PROMPTS["baseline"]


def list_models(cfg: Settings) -> list[str]:
    """Names of models installed in the Ollama server (excluding embedding models)."""
    try:
        with urllib.request.urlopen(f"{cfg.ollama_url}/api/tags", timeout=3) as resp:
            names = [m["name"] for m in json.load(resp).get("models", [])]
    except OSError:
        return []
    return sorted(n for n in names if "embed" not in n)


def get_llm(cfg: Settings) -> OllamaLLM:
    return OllamaLLM(
        model=cfg.llm_model,
        base_url=cfg.ollama_url,
        temperature=cfg.temperature,
        num_predict=cfg.max_tokens,
    )


def retrieve(question: str, db: Chroma, cfg: Settings) -> list[dict[str, Any]]:
    results = db.similarity_search_with_score(question, k=cfg.top_k)
    return [
        {
            "source": str(doc.metadata.get("source", "Unknown")),
            "page": doc.metadata.get("page"),
            # Chroma returns squared L2 distance. Ollama's embeddings are unit
            # length, so d = 2 - 2*cos and cosine similarity is 1 - d/2.
            # (The baseline used 1/(1+d), which compresses everything to ~0.5-0.7.)
            "score": round(1 - distance / 2, 4),
            "content": doc.page_content,
        }
        for doc, distance in results
    ]


def format_source(s: dict[str, Any]) -> str:
    return f"{s['source']} p.{s['page']}" if s.get("page") else s["source"]


def build_prompt(question: str, sources: list[dict[str, Any]], used_fallback: bool,
                 style: str = "baseline") -> str:
    if used_fallback:
        context = "No sufficiently relevant documents found. Use your general knowledge."
    else:
        context = "\n\n---\n\n".join(f"[{format_source(s)}]\n{s['content']}" for s in sources)
    return PROMPTS[style].replace("{context}", context).replace("{question}", question)


def prepare(question: str, db: Chroma, cfg: Settings) -> dict[str, Any]:
    """Retrieval half of the pipeline: sources, relevance and the final prompt."""
    if cfg.prompt_style not in PROMPTS:
        raise ValueError(f"PROMPT_STYLE must be one of {sorted(PROMPTS)}, got {cfg.prompt_style!r}")
    sources = retrieve(question, db, cfg)
    top_score = sources[0]["score"] if sources else 0.0
    avg_score = sum(s["score"] for s in sources) / len(sources) if sources else 0.0
    # Judge relevance by the BEST chunk: one strong match is enough to answer from.
    used_fallback = top_score < cfg.score_threshold
    result = {
        "sources": sources,
        "top_score": round(top_score, 4),
        "avg_score": round(avg_score, 4),
        "used_fallback": used_fallback,
        "prompt": build_prompt(question, sources, used_fallback, cfg.prompt_style),
        "answer": None,
    }
    if used_fallback and cfg.prompt_style == "strict":
        # Nothing relevant was retrieved: refuse without calling the LLM at all.
        result["answer"] = NOT_FOUND
    return result


def ask(question: str, db: Chroma, llm: OllamaLLM, cfg: Settings) -> dict[str, Any]:
    result = prepare(question, db, cfg)
    if result["answer"] is None:
        result["answer"] = llm.invoke(result["prompt"]).strip()
    return result
