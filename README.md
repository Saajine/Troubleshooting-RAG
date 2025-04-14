# Knowledge Graph Query System

Querying technical knowledge graphs using vector search and LLM. This application allows users to ask natural language questions about software issues, symptoms, causes, and solutions, and get accurate answers based on structured knowledge data.

## System Architecture

The system consists of several key components:

1. **Knowledge Graph Processing** (`process_knowledge_graph.py`): Processes raw JSON knowledge data into structured format
2. **Vector Database** (`vector_db.py`): Manages the ChromaDB vector database
4. **Query Processor** (`query_processor.py`): Handle processing pipeline end-to-end
5. **Web Server** (`web_server.py`): Web user interface with Flask and React

## Prerequisites

- Python 3.8+ 
- [Ollama](https://ollama.com) installed and running locally
- Required Python packages mentioned in requirement.txt

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/knowledge-graph-query-system.git
cd knowledge-graph-query-system
```

2. Install dependencies in requirement:

```bash
pip install -r requirements.txt
```

3. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Usage

The system offers several modes of operation:

### 1. Processing the Knowledge Graph

Process knowledge graph data before usage

```bash
python -m src.main process
```

This will read the raw JSON file from `data/raw/knowledge_graph.json` and process it into a format suitable for vectorization.

### 2. Building the Vector Database

After processing the knowledge graph, build the vector database:

```bash
python -m src.main build
```

This will embed the processed documents and store them in ChromaDB.


### 3. Web Interface

To start the web interface:

```bash
python -m src.main web
```

Example:
```bash
python -m src.main web --port 8080
```

### 4. All-in-One

To run all the steps (process, build, and start):

```bash
python -m src.main all
```

## Project Structure

```
knowledge-graph-query-system/
├── data/                        # Data storage
│   ├── raw/                     # Raw knowledge graph data
│   └── processed/               # Processed documents
├── src/                         # Source code
│   ├── main.py                  # Main entry point
│   ├── process_knowledge_graph.py # Knowledge graph processing
│   ├── vector_db.py             # ChromaDB vector database
│   ├── ollama_interface.py      # Ollama integration
│   ├── query_processor.py       # Query pipeline
│   ├── query_interface.py       # CLI query interface
│   └── web_server.py            # Web server 
├── web/                         # Web interface
│   ├── templates/               # HTML templates
│   └── static/                  # Static assets (CSS, JS)
│       ├── css/                 # CSS styles
│       └── js/                  # JavaScript files
├── chroma_db/                   # ChromaDB storage
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Example Knowledge Graph Structure

Works on knowledge graphs containing information about:
- Software products
- Issues
- Symptoms 
- Causes
- Solutions
- Diagnostic tests
- Log entries
- FAQs
- User feedback

## Configuration

- Vector DB persistence: Edit `KnowledgeGraphVectorDB` class in `vector_db.py`
- Ollama model: Change default in `OllamaInterface` class or use the `--model` flag
- Data paths: Modify paths in `process_knowledge_graph.py`

## Contributing


