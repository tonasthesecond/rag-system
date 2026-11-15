"""Build or open the Chroma vector store."""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import Settings
from .loaders import LOADERS, load_documents


def get_embeddings(cfg: Settings) -> OllamaEmbeddings:
    return OllamaEmbeddings(model=cfg.embed_model, base_url=cfg.ollama_url)


def load_or_build(cfg: Settings, rebuild: bool = False) -> Chroma:
    """Open the persisted store, or (re)index `cfg.data_dir` if it is empty or `rebuild`."""
    db = Chroma(
        collection_name=cfg.collection,
        embedding_function=get_embeddings(cfg),
        persist_directory=str(cfg.index_dir),
    )
    if rebuild:
        # Empty the collection rather than deleting the folder: Chroma caches one
        # client per path, and re-creating a deleted folder in the same process
        # fails with "attempt to write a readonly database" (the UI rebuild button).
        print(f"Clearing existing vector store at {cfg.index_dir}")
        db.reset_collection()
    elif db.get(limit=1)["ids"]:
        print("Loading existing vector store...")
        return db

    print(f"Indexing documents in {cfg.data_dir} ...")
    documents = load_documents(cfg.data_dir)
    if not documents:
        raise SystemExit(
            f"No supported files ({', '.join(LOADERS)}) found in '{cfg.data_dir}'"
        )
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap
    ).split_documents(documents)
    print(f"  Indexing {len(chunks)} chunks...")
    # from_documents batches large inserts; it reuses the collection opened above.
    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(cfg),
        collection_name=cfg.collection,
        persist_directory=str(cfg.index_dir),
    )
