"""Streamlit chat UI for the local RAG system.

Run:  streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import httpx
import ollama
import streamlit as st

from rag.config import PROJECT_ROOT, Settings
from rag.loaders import LOADERS
from rag.pipeline import format_source, get_llm, list_models, prepare
from rag.store import load_or_build

DATA_ROOT = PROJECT_ROOT / "data"
EXAMPLES = [
    "What are the requirements for the Computer Science major?",
    "What is the prerequisite for CS311 Advanced Deep Learning?",
    "What GPA do I need for the capstone project?",
    "What jobs have CS graduates gone on to?",
]

st.set_page_config(page_title="Handbook Assistant", page_icon="📘", layout="wide")


def corpora() -> list[str]:
    return sorted(
        d.name for d in DATA_ROOT.iterdir()
        if d.is_dir() and any(f.suffix.lower() in LOADERS for f in d.iterdir())
    )


@st.cache_resource(show_spinner="Loading vector index (first run embeds every document)...")
def get_db(corpus: str, embed_model: str, ollama_url: str, chunk_size: int, chunk_overlap: int,
           _rebuild_token: int = 0):
    cfg = Settings()
    cfg.data_dir = DATA_ROOT / corpus
    cfg.embed_model, cfg.ollama_url = embed_model, ollama_url
    cfg.chunk_size, cfg.chunk_overlap = chunk_size, chunk_overlap
    return load_or_build(cfg, rebuild=_rebuild_token > 0)


# ------------------------------------------------------------------ sidebar
cfg = Settings()
st.session_state.setdefault("messages", [])
st.session_state.setdefault("rebuild", 0)

with st.sidebar:
    st.title("📘 Handbook Assistant")
    st.caption("Local RAG · Ollama + Chroma · nothing leaves this machine")

    options = corpora()
    default = options.index("handbooks") if "handbooks" in options else 0
    corpus = st.selectbox("Document collection", options, index=default)

    models = list_models(cfg) or [cfg.llm_model]
    preferred = "qwen2.5:1.5b" if "qwen2.5:1.5b" in models else cfg.llm_model
    cfg.llm_model = st.selectbox(
        "Answer model", models, index=models.index(preferred) if preferred in models else 0
    )
    with st.expander("Retrieval settings"):
        cfg.top_k = st.slider("Chunks to retrieve (top-k)", 1, 10, cfg.top_k)
        cfg.temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
        cfg.score_threshold = st.slider("Min. avg relevance", 0.0, 1.0, cfg.score_threshold, 0.05)

    with st.expander("Add documents"):
        uploads = st.file_uploader("PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True)
        if uploads and st.button("Save & re-index", use_container_width=True):
            for f in uploads:
                (DATA_ROOT / corpus / Path(f.name).name).write_bytes(f.getvalue())
            st.session_state.rebuild += 1
            st.cache_resource.clear()
            st.rerun()
        if st.button("Rebuild index", use_container_width=True):
            st.session_state.rebuild += 1
            st.cache_resource.clear()
            st.rerun()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    files = sorted(f.name for f in (DATA_ROOT / corpus).iterdir() if f.suffix.lower() in LOADERS)
    st.caption("Indexed files: " + ", ".join(files))

cfg.data_dir = DATA_ROOT / corpus
db = get_db(corpus, cfg.embed_model, cfg.ollama_url, cfg.chunk_size, cfg.chunk_overlap,
            st.session_state.rebuild)
# A rebuild only has to happen once; later cache hits should reuse the new index.
st.session_state.rebuild = 0


# ------------------------------------------------------------------ chat
def render_sources(msg: dict) -> None:
    if msg.get("used_fallback"):
        st.warning("No sufficiently relevant passages found — answered from model knowledge.",
                   icon="⚠️")
    if not msg.get("sources"):
        return
    label = f"📄 Sources · avg relevance {msg['avg_score']:.2f} · {msg['model']}"
    with st.expander(label):
        for s in msg["sources"]:
            st.markdown(f"**{format_source(s)}** — relevance `{s['score']:.2f}`")
            st.caption(s["content"][:600] + ("…" if len(s["content"]) > 600 else ""))


st.header("Ask about the Computer Science Major Handbook" if corpus == "handbooks"
          else f"Ask about: {corpus}")

if not st.session_state.messages:
    st.markdown("Try one of these:")
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLES):
        if cols[i % 2].button(example, use_container_width=True):
            st.session_state.pending = example
            st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg)

question = st.chat_input("Ask a question about the documents...") or st.session_state.pop(
    "pending", None
)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            result = prepare(question, db, cfg)
        try:
            answer = st.write_stream(get_llm(cfg).stream(result["prompt"]))
        except (httpx.HTTPError, ollama.ResponseError) as exc:  # server down, model missing
            answer = f"⚠️ Could not reach the model `{cfg.llm_model}` at {cfg.ollama_url}: {exc}"
            st.error(answer)
        msg = {"role": "assistant", "content": str(answer).strip(), "model": cfg.llm_model,
               **{k: result[k] for k in ("sources", "avg_score", "used_fallback")}}
        render_sources(msg)
    st.session_state.messages.append(msg)
