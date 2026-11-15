"""Runtime configuration, overridable through environment variables or a .env file."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else PROJECT_ROOT / p


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: _resolve(_env("DATA_DIR", "data/sample_txt")))
    vector_store: Path = field(
        default_factory=lambda: _resolve(_env("VECTOR_STORE", "vector_store"))
    )
    collection: str = field(default_factory=lambda: _env("COLLECTION", "rag_documents"))
    chunk_size: int = field(default_factory=lambda: int(_env("CHUNK_SIZE", "1000")))
    chunk_overlap: int = field(default_factory=lambda: int(_env("CHUNK_OVERLAP", "200")))
    embed_model: str = field(default_factory=lambda: _env("EMBED_MODEL", "nomic-embed-text"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "qwen2.5:1.5b"))
    temperature: float = field(default_factory=lambda: float(_env("TEMPERATURE", "0.2")))
    # Hard cap on generated tokens. Without it a small model can fall into a
    # repetition loop and generate for tens of minutes (observed with 0.5b).
    max_tokens: int = field(default_factory=lambda: int(_env("MAX_TOKENS", "512")))
    ollama_url: str = field(default_factory=lambda: _env("OLLAMA_URL", "http://127.0.0.1:11434"))
    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "5")))
    # Fallback when even the best retrieved chunk has a cosine similarity below
    # this. Calibrated on the CS handbook: every handbook question scores >= 0.656,
    # clearly off-topic questions <= 0.55 (see docs/DECISIONS.md D-17).
    score_threshold: float = field(default_factory=lambda: float(_env("SCORE_THRESHOLD", "0.6")))
    # "strict" (default) = answer only from the documents, otherwise say so (D-18);
    # "baseline" = the course prompt, which allows general-knowledge answers.
    prompt_style: str = field(default_factory=lambda: _env("PROMPT_STYLE", "strict"))

    @property
    def index_dir(self) -> Path:
        """One index per (document folder, embedding model, chunking), so corpora and
        experiments never overwrite each other."""
        embed = re.sub(r"[^A-Za-z0-9.-]+", "-", self.embed_model)
        return self.vector_store / f"{self.data_dir.name}__{embed}__{self.chunk_size}-{self.chunk_overlap}"
