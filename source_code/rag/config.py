"""Runtime configuration, overridable through environment variables or a .env file."""

from __future__ import annotations

import os
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
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "qwen2.5:0.5b"))
    temperature: float = field(default_factory=lambda: float(_env("TEMPERATURE", "0.7")))
    ollama_url: str = field(default_factory=lambda: _env("OLLAMA_URL", "http://127.0.0.1:11434"))
    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "5")))
    score_threshold: float = field(default_factory=lambda: float(_env("SCORE_THRESHOLD", "0.3")))

    @property
    def index_dir(self) -> Path:
        """One persisted index per document folder, so corpora never get mixed."""
        return self.vector_store / self.data_dir.name
