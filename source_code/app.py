"""Streamlit chat UI for the local RAG system.

Run:  streamlit run app.py
"""

from __future__ import annotations

from itertools import chain
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


def corpus_settings(corpus: str) -> Settings:
    cfg = Settings()
    cfg.data_dir = DATA_ROOT / corpus
    return cfg


@st.cache_resource(show_spinner="Loading vector index (first run embeds every document)...")
def get_db(corpus: str):
    return load_or_build(corpus_settings(corpus))


def rebuild(corpus: str) -> None:
    with st.spinner("Re-indexing documents..."):
        load_or_build(corpus_settings(corpus), rebuild=True)
    get_db.clear()
    st.rerun()


# ------------------------------------------------------------------ sidebar
cfg = Settings()
st.session_state.setdefault("messages", [])

with st.sidebar:
    st.title("📘 Handbook Assistant")
    st.caption("Local RAG · Ollama + Chroma · nothing leaves this machine")

    options = corpora()
    default = options.index("handbooks") if "handbooks" in options else 0
    corpus = st.selectbox("Document collection", options, index=default)

    models = list_models(cfg) or [cfg.llm_model]
    cfg.llm_model = st.selectbox(
        "Answer model", models,
        index=models.index(cfg.llm_model) if cfg.llm_model in models else 0,
    )
    with st.expander("Retrieval settings"):
        cfg.top_k = st.slider("Chunks to retrieve (top-k)", 1, 10, cfg.top_k)
        cfg.temperature = st.slider("Temperature", 0.0, 1.0, cfg.temperature, 0.1)
        cfg.score_threshold = st.slider("Min. best-chunk relevance (cosine)", 0.0, 1.0,
                                        cfg.score_threshold, 0.05)
        cfg.prompt_style = st.radio(
            "Prompt", ["strict", "baseline"],
            index=0 if cfg.prompt_style == "strict" else 1, horizontal=True,
            help="strict: answer only from the documents. baseline: course prompt, may use "
                 "general knowledge.",
        )

    with st.expander("Add documents"):
        uploads = st.file_uploader("PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True)
        if uploads and st.button("Save & re-index", use_container_width=True):
            for f in uploads:
                (DATA_ROOT / corpus / Path(f.name).name).write_bytes(f.getvalue())
            rebuild(corpus)
        if st.button("Rebuild index", use_container_width=True):
            rebuild(corpus)

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    files = sorted(f.name for f in (DATA_ROOT / corpus).iterdir() if f.suffix.lower() in LOADERS)
    st.caption("Indexed files: " + ", ".join(files))

cfg.data_dir = DATA_ROOT / corpus
db = get_db(corpus)


# ------------------------------------------------------------------ chat
def render_sources(msg: dict) -> None:
    if msg.get("used_fallback"):
        st.warning("No sufficiently relevant passages found — "
                   + ("the model was not asked." if msg.get("prompt_style") == "strict"
                      else "answered from model knowledge."),
                   icon="⚠️")
    if not msg.get("sources"):
        return
    label = f"📄 Sources · best relevance {msg['top_score']:.2f} · {msg['model']}"
    with st.expander(label):
        for s in msg["sources"]:
            st.markdown(f"**{format_source(s)}** — relevance `{s['score']:.2f}`")
            st.caption(s["content"][:600] + ("…" if len(s["content"]) > 600 else ""))


st.header("Ask about the Computer Science Major Handbook" if corpus == "handbooks"
          else f"Ask about: {corpus}")

messages = st.session_state.messages


def submit(text: str) -> None:
    messages.append({"role": "user", "content": text})
    st.rerun()


# A question is "waiting" until its answer is stored. Any new input makes Streamlit
# abort the running script, so the input stays disabled while an answer is being
# generated (CPU generation takes 30-50 s), and a question whose run was interrupted
# anyway (e.g. by a sidebar change) is simply answered on the next run.
waiting = bool(messages) and messages[-1]["role"] == "user"
question = st.chat_input(
    "Answering…" if waiting else "Ask a question about the documents...", disabled=waiting
)
if question and not waiting:
    submit(question)

if not messages:
    st.markdown("Try one of these:")
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLES):
        if cols[i % 2].button(example, use_container_width=True):
            submit(example)

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg)

if waiting:
    question = messages[-1]["content"]
    result = {"sources": [], "top_score": 0.0, "used_fallback": False}
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching documents..."):
                result = prepare(question, db, cfg)
            if result["answer"] is not None:  # strict mode refused without calling the LLM
                answer = result["answer"]
                st.markdown(answer)
            else:
                with st.spinner("Generating answer (can take ~30 s on CPU)..."):
                    stream = get_llm(cfg).stream(result["prompt"])
                    first = next(stream, "")
                answer = st.write_stream(chain([first], stream))
        except (httpx.HTTPError, ollama.ResponseError) as exc:  # server down, model missing
            answer = f"⚠️ Could not reach the model `{cfg.llm_model}` at {cfg.ollama_url}: {exc}"
            st.error(answer)
        except Exception as exc:  # never leave the question unanswered (input would stay locked)
            answer = f"⚠️ Error while answering: {exc}"
            st.error(answer)
    messages.append({"role": "assistant", "content": str(answer).strip(),
                     "model": cfg.llm_model, "prompt_style": cfg.prompt_style,
                     **{k: result[k] for k in ("sources", "top_score", "used_fallback")}})
    st.rerun()  # re-render with the sources expander and re-enable the input
