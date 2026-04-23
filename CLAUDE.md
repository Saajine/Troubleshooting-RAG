# Troubleshooting-RAG

RAG-based customer support chatbot for "AwesomeApp" with built-in defense against prompt injection attacks. Built for CS 763 (ML Security) at UW-Madison.

## Quick Start

```bash
# Activate virtual environment
source myenv/bin/activate

# Process knowledge graph -> build vector DB -> run interactive Q&A
python -m src.main all

# Or step by step:
python -m src.main process      # ETL: knowledge_graph.json -> documents.json
python -m src.main build        # Load documents into ChromaDB
python -m src.main interactive  # CLI Q&A mode
python -m src.main web          # Flask web UI at http://localhost:5000
```

### Prerequisites

- Python 3.12 (venv in `myenv/`)
- Ollama running locally on port 11434 with `llama3` model pulled
- Dependencies: `pip install -r requirements.txt`

## Architecture

### RAG Pipeline (`src/query_processor.py`)

```
User Question
  -> [Query Analysis Chain] extract keywords + severity (LangChain + Ollama)
  -> [Vector Search] ChromaDB query with all-MiniLM-L6-v2 embeddings (top 3)
  -> [Defense Hook] if DEFENSE_ACTIVE=1, DistilBERT filters adversarial docs (threshold >= 0.7)
  -> [Answer Generation Chain] LLM generates answer from filtered context
  -> Response + timing metrics
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `src/main.py` | CLI entry point, command routing (`process`, `build`, `interactive`, `web`, `all`) |
| `src/query_processor.py` | RAG pipeline orchestrator (dual LangChain chains) |
| `src/vector_db.py` | ChromaDB wrapper (collection: `knowledge_graph`, embedding: `all-MiniLM-L6-v2`) |
| `src/ollama_interface.py` | Custom `OllamaLLM` class + LangChain chain factories |
| `src/process_knowledge_graph.py` | ETL: `data/raw/knowledge_graph.json` -> `data/processed/documents.json` |
| `src/web_server.py` | Flask server, `/api/query` endpoint, serves React frontend |
| `defense/classifier.py` | DistilBERT fine-tuning on 10 attack families + inference |
| `defense/sanitizer.py` | `filter_retrieved()` hook - scores & removes adversarial docs |
| `eval/harness.py` | Evaluation runner measuring Attack Success Rate (ASR) |
| `eval/queries.py` | 20 clean + 10 attack test queries |

### Data Flow

```
data/raw/knowledge_graph.json
  -> [process_knowledge_graph.py] flatten entities to documents
  -> data/processed/documents.json
  -> [vector_db.py] embed + store
  -> chroma_db/ (persistent ChromaDB)
```

## Defense System

### Activation

Set `DEFENSE_ACTIVE=1` environment variable. The defense is opt-in and doesn't require restart.

### Classifier

- Model: DistilBERT fine-tuned for binary classification (benign vs adversarial)
- Trained on synthetic data covering 10 attack families (instruction override, credential phishing, role hijack, etc.)
- Stored in `defense/model/` (~256MB)
- Training: `python -m defense.classifier`
- Accuracy: 96.3% (see `defense/model/metrics.json`)

### Evaluation

```bash
python -m eval.harness
```

Measures ASR by checking if the payload marker "SECURITY NOTICE" appears in generated answers. Results saved to `eval/results/`.

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Tests use `unittest.mock` to avoid requiring Ollama. ChromaDB tests use temp directories for isolation.

## Tech Stack

- **Python 3.12** - main language
- **ChromaDB** - vector database (persistent, `chroma_db/`)
- **LangChain** - LLM chain orchestration
- **Sentence Transformers** (`all-MiniLM-L6-v2`) - 384-dim embeddings
- **Ollama** (`llama3`) - local LLM inference at `http://localhost:11434`
- **PyTorch + HuggingFace Transformers** - DistilBERT defense classifier
- **Flask** - web backend
- **React 17** (CDN, no build step) - web frontend with Babel JSX transpilation

## Configuration Defaults

| Setting | Value |
|---------|-------|
| Ollama URL | `http://localhost:11434` |
| LLM model | `llama3` |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector DB path | `chroma_db/` |
| Query results | Top 3 |
| Defense threshold | 0.7 |
| Web server | `0.0.0.0:5000` |

## Project Conventions

- Virtual environment: `myenv/` (do not commit)
- Run all Python commands through `./myenv/bin/python` or activate the venv first
- Entry point pattern: `python -m <module>` (not direct file execution)
- Defense model weights in `defense/model/` (large files, ~256MB)
- Relevance scoring: `max(0, 1 - cosine_distance)` normalization
