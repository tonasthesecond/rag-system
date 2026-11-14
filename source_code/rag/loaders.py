"""Turn files on disk into LangChain Documents."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


def load_txt(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8")
    return [Document(page_content=text, metadata={"source": path.name})]


LOADERS = {".txt": load_txt}


def load_documents(directory: Path) -> list[Document]:
    """Load every supported file in `directory` (non-recursive, sorted for determinism)."""
    documents: list[Document] = []
    for path in sorted(Path(directory).iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            continue
        print(f"  Loading: {path.name}")
        documents.extend(loader(path))
    return documents
