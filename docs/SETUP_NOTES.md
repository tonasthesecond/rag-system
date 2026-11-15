# Local setup notes

Machine used for development and all experiments in this project.

## Hardware / OS

| | |
|---|---|
| OS | Fedora Linux 44 (KDE Plasma) |
| CPU | 13th Gen Intel Core i7-1365U (12 threads) |
| GPU | Intel Iris Xe (integrated) — no CUDA; all inference runs on CPU |
| RAM | 30 GB |

## Ollama

- Installed Ollama 0.12.11 from the Fedora package (`dnf install ollama`), running
  as a systemd service (`ollama.service`) on the default `http://127.0.0.1:11434`.
- Pulled general-purpose models to test local inference speed on CPU:
  - `gemma3:4b` (3.4 GB)
  - `qwen3:30b-a3b-instruct-2507-q4_K_M` (18 GB, mixture-of-experts, ~3B active params)

- Pulled for the project: `nomic-embed-text` (embeddings) and `qwen2.5:0.5b`,
  `qwen2.5:1.5b`, `qwen2.5:3b` (answer models compared in the evaluation).
