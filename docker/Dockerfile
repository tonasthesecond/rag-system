# Local RAG chatbot - application image (Streamlit UI + CLI).
# The LLM and embedding model are served by a separate Ollama container
# (see docker-compose.yml); this image only holds the Python app.
#
# Build from the repository root:
#   docker build -f docker/Dockerfile -t rag-system source_code

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Defaults; docker-compose overrides OLLAMA_URL to reach the ollama service.
    OLLAMA_URL=http://ollama:11434 \
    EMBED_MODEL=nomic-embed-text \
    LLM_MODEL=qwen2.5:1.5b \
    DATA_DIR=data/handbooks \
    VECTOR_STORE=/app/vector_store \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Dependencies first so code changes don't invalidate this layer.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY rag/ rag/
COPY app.py run.py evaluate.py ./
COPY eval/questions.yaml eval/questions.yaml
# Default documents; usually replaced by a bind mount of ./source_code/data.
COPY data/ data/

# Run as an unprivileged user; it needs to write the index and uploads.
RUN useradd --create-home --uid 1000 rag \
    && mkdir -p /app/vector_store \
    && chown -R rag:rag /app
USER rag

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "app.py"]
