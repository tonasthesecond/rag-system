"""Build or open the Chroma vector store."""

from __future__ import annotations

import shutil

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import Settings
from .loaders import LOADERS, load_documents


def get_embeddings(cfg: Settings) -> OllamaEmbeddings:
    return OllamaEmbeddings(model=cfg.embed_model, base_url=cfg.ollama_url)


def load_or_build(cfg: Settings, rebuild: bool = False) -> Chroma:
    """Open the persisted store, or (re)index `cfg.data_dir` if missing or `rebuild`."""
    embeddings = get_embeddings(cfg)
    if rebuild and cfg.index_dir.exists():
        print(f"Removing existing vector store at {cfg.index_dir}")
        shutil.rmtree(cfg.index_dir)

    if cfg.index_dir.exists():
        print("Loading existing vector store...")
        return Chroma(
            collection_name=cfg.collection,
            embedding_function=embeddings,
            persist_directory=str(cfg.index_dir),
        )

    print(f"No vector store found. Indexing documents in {cfg.data_dir} ...")
    documents = load_documents(cfg.data_dir)
    if not documents:
        raise SystemExit(
            f"No supported files ({', '.join(LOADERS)}) found in '{cfg.data_dir}'"
        )
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap
    ).split_documents(documents)
    print(f"  Indexing {len(chunks)} chunks...")
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=cfg.collection,
        persist_directory=str(cfg.index_dir),
    )
