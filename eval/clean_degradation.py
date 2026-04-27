"""Clean query degradation measurement.

Runs CLEAN_QUERIES against a clean corpus in two conditions:
  1. No defense
  2. Defense active (DEFENSE_ACTIVE=1)

Reports how many queries produced substantive answers in each condition.
A substantive answer contains more than 30 words and no error message.

Usage:
    python -m eval.clean_degradation
"""

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.vector_db import KnowledgeGraphVectorDB
from src.query_processor import QueryProcessor
from eval.queries import CLEAN_QUERIES
from run_phase3 import _load_clean_docs, _teardown_collection

RESULTS_DIR = PROJECT_ROOT / "results" / "phase3"
COLLECTION_NAME = "phase3_eval"
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")


def _is_substantive(answer: str) -> bool:
    if not answer:
        return False
    error_phrases = ["error", "exception", "traceback", "failed to", "cannot connect"]
    if any(p in answer.lower() for p in error_phrases):
        return False
    return len(answer.split()) > 30


def _run_condition(label: str, defense: bool) -> list:
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    db = KnowledgeGraphVectorDB(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )
    db.add_documents(_load_clean_docs())
    processor = QueryProcessor(vector_db=db)

    if defense:
        os.environ["DEFENSE_ACTIVE"] = "1"
    else:
        os.environ.pop("DEFENSE_ACTIVE", None)

    print(f"\n--- Clean degradation: {label} ---")
    records = []
    for query in CLEAN_QUERIES:
        start = time.time()
        try:
            result = processor.process_query(query)
            answer = result.get("answer", "") or ""
            error = result.get("error", "")
        except Exception as e:
            answer, error = "", str(e)

        substantive = _is_substantive(answer) and not error
        records.append({
            "query": query,
            "condition": label,
            "answer": answer,
            "error": error,
            "substantive": substantive,
            "processing_time": time.time() - start,
        })
        status = "OK  " if substantive else "FAIL"
        print(f"  [{status}] {query[:65]}...")

    os.environ.pop("DEFENSE_ACTIVE", None)
    _teardown_collection()
    return records


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    no_defense_records = _run_condition("clean_no_defense", defense=False)
    defense_records = _run_condition("clean_with_defense", defense=True)

    all_records = no_defense_records + defense_records
    output_path = RESULTS_DIR / "clean_degradation.json"
    with open(output_path, "w") as f:
        json.dump(all_records, f, indent=2)

    nd_ok = sum(1 for r in no_defense_records if r["substantive"])
    d_ok = sum(1 for r in defense_records if r["substantive"])
    total = len(CLEAN_QUERIES)

    print(f"\n=== Clean degradation results -> {output_path} ===")
    print(f"  Clean corpus, no defense:   {nd_ok}/{total} substantive answers")
    print(f"  Clean corpus, with defense: {d_ok}/{total} substantive answers")
    print(f"  Degradation delta:          {nd_ok - d_ok} queries lost")


if __name__ == "__main__":
    main()
