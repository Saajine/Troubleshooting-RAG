"""Sanitizer hook that filters adversarial chunks from ChromaDB retrieval results.

Loads the trained DistilBERT classifier and scores each retrieved document.
Scores at paragraph level — if ANY paragraph in a document scores above
the threshold, the entire document is flagged and removed.
"""

import logging

from defense.classifier import load_classifier, score_chunk

logger = logging.getLogger(__name__)


def _max_paragraph_score(text, model, tokenizer):
    """Score each paragraph in a document and return the max adversarial score."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= 10]
    if not paragraphs:
        return score_chunk(text, model, tokenizer)
    scores = [score_chunk(p, model, tokenizer) for p in paragraphs]
    return max(scores)


def filter_retrieved(results, model_path="defense/model", threshold=0.5):
    """Score and filter retrieved ChromaDB results at paragraph granularity.

    Args:
        results: ChromaDB query result dict with nested lists:
                 {'ids': [[...]], 'documents': [[...]], 'metadatas': [[...]], 'distances': [[...]]}
        model_path: path to saved classifier
        threshold: adversarial probability above which a doc is dropped

    Returns:
        (filtered_results, flagged_ids)
    """
    model, tokenizer = load_classifier(model_path)

    documents = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]

    flagged_ids = []
    keep_indices = []

    for i, (doc_text, doc_id) in enumerate(zip(documents, ids)):
        adv_score = _max_paragraph_score(doc_text, model, tokenizer)
        if adv_score >= threshold:
            flagged_ids.append(doc_id)
            logger.info(f"[Defense] Flagged doc {doc_id} (max_para_score={adv_score:.3f})")
        else:
            keep_indices.append(i)

    filtered = {
        "ids": [[ids[i] for i in keep_indices]],
        "documents": [[documents[i] for i in keep_indices]],
        "metadatas": [[results.get("metadatas", [[]])[0][i] for i in keep_indices]],
        "distances": [[results.get("distances", [[]])[0][i] for i in keep_indices]],
    }

    if "query_time" in results:
        filtered["query_time"] = results["query_time"]

    return filtered, flagged_ids
