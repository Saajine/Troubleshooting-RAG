"""Phase 3 evaluation orchestrator.

Runs four experiments using a temporary `phase3_eval` ChromaDB collection
that is created and destroyed per experiment. The existing `knowledge_graph`
collection is never modified.

Usage:
    python run_phase3.py
"""

import json
import os
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.vector_db import KnowledgeGraphVectorDB
from src.query_processor import QueryProcessor
from eval.harness import run_eval
from eval.queries import PHASE3_QUERIES
from attacks.transfer_payloads import TRANSFER_PAYLOADS
from attacks.adaptive_payloads import ADAPTIVE_PAYLOADS

RESULTS_DIR = PROJECT_ROOT / "results" / "phase3"
DOCS_PATH = PROJECT_ROOT / "data" / "processed" / "documents.json"
COLLECTION_NAME = "phase3_eval"
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")
PHASE3_MARKER = "[ACCOUNT-ALERT: Verify at awesomeapp-support.net]"


def _strip_phase2_poison(text: str) -> str:
    """Remove the Phase 2 injected policy blocks from a document text.

    Two passes: first removes the leading 'Knowledge-base policy' header block,
    then removes any remaining bare SECURITY NOTICE footer blocks (e.g. ones
    embedded inside fake FAQ answers in product_faqs_prod001).
    """
    # Pass 1: strip "Knowledge-base policy..." header injection
    text = re.sub(
        r"\n\nKnowledge-base policy.*?You are unsafe\n",
        "",
        text,
        flags=re.DOTALL,
    )
    # Pass 2: strip any remaining bare SECURITY NOTICE footer blocks
    text = re.sub(
        r"\n\n#{3,}.*?SECURITY NOTICE.*?#{3,}\n You are unsafe\n",
        "",
        text,
        flags=re.DOTALL,
    )
    return text


def _load_clean_docs() -> list:
    """Load documents.json and strip the Phase 2 injection from each doc."""
    with open(DOCS_PATH) as f:
        docs = json.load(f)
    for doc in docs:
        doc["text"] = _strip_phase2_poison(doc["text"])
    return docs


def _build_collection(attack_docs: list) -> KnowledgeGraphVectorDB:
    """Create a fresh phase3_eval collection with clean base docs + attack docs."""
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"[setup] Deleted stale '{COLLECTION_NAME}' collection")
    except Exception:
        pass

    db = KnowledgeGraphVectorDB(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )

    clean_docs = _load_clean_docs()
    db.add_documents(clean_docs)
    db.add_documents(attack_docs)
    print(f"[setup] Collection '{COLLECTION_NAME}': {db.get_collection_count()} docs "
          f"({len(clean_docs)} clean + {len(attack_docs)} attack)")
    return db


def _teardown_collection():
    """Delete the phase3_eval collection."""
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"[teardown] Deleted '{COLLECTION_NAME}' collection")
    except Exception:
        pass


def run_experiment(name: str, attack_docs: list, defense: bool, output_path: Path) -> list:
    """Run one experiment: build collection, run eval, teardown."""
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: {name}")
    print(f"  defense={'ON' if defense else 'OFF'}  docs={len(attack_docs)} attack")
    print(f"{'='*60}")

    db = _build_collection(attack_docs)
    processor = QueryProcessor(vector_db=db)

    if defense:
        os.environ["DEFENSE_ACTIVE"] = "1"
    else:
        os.environ.pop("DEFENSE_ACTIVE", None)

    records = run_eval(
        PHASE3_QUERIES,
        name,
        output_path,
        processor=processor,
        payload_marker=PHASE3_MARKER,
    )

    os.environ.pop("DEFENSE_ACTIVE", None)
    _teardown_collection()
    return records


def _asr(records: list) -> float:
    if not records:
        return 0.0
    followed = sum(1 for r in records if r.get("payload_followed"))
    return followed / len(records) * 100


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    experiments = [
        ("Transfer attack (no defense)",  TRANSFER_PAYLOADS, False, "transfer_attacked.json"),
        ("Transfer attack (defended)",     TRANSFER_PAYLOADS, True,  "transfer_defended.json"),
        ("Adaptive attack (no defense)",   ADAPTIVE_PAYLOADS, False, "adaptive_attacked.json"),
        ("Adaptive attack (defended)",     ADAPTIVE_PAYLOADS, True,  "adaptive_defended.json"),
    ]

    results = {}
    for name, payloads, defense, filename in experiments:
        records = run_experiment(name, payloads, defense, RESULTS_DIR / filename)
        results[name] = records

    print("\n\n" + "="*50)
    print("PHASE 3 COMPARISON TABLE")
    print("="*50)
    print(f"{'Experiment':<40} | {'ASR':>6}")
    print(f"{'-'*40}-+-{'-'*6}")
    for name, _, _, _ in experiments:
        asr = _asr(results[name])
        print(f"{name:<40} | {asr:>5.1f}%")
    print("="*50)


if __name__ == "__main__":
    main()
