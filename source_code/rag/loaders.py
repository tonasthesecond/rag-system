"""Turn files on disk into LangChain Documents."""

from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

# pypdf logs harmless "wrong pointing object" noise for many exported PDFs.
logging.getLogger("pypdf").setLevel(logging.ERROR)

MIN_PAGE_CHARS = 20  # pages with less text are likely images/scans (would need OCR)


def clean_text(text: str) -> str:
    """Normalise PDF-extracted text: unfold ligatures (ﬁ -> fi), collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_txt(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8")
    return [Document(page_content=text, metadata={"source": path.name})]


def load_pdf(path: Path) -> list[Document]:
    """One Document per page so answers can cite page numbers."""
    reader = PdfReader(path)
    documents = []
    skipped = []
    for number, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if len(text) < MIN_PAGE_CHARS:
            skipped.append(number)
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={"source": path.name, "page": number, "total_pages": len(reader.pages)},
            )
        )
    if skipped:
        print(f"    skipped {len(skipped)} page(s) with no extractable text: {skipped}")
    return documents


LOADERS = {".txt": load_txt, ".pdf": load_pdf}


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
