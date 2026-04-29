EVIDENCE_RANK = {
    "guideline": 6,
    "meta-analysis": 5,
    "systematic review": 5,
    "RCT": 4,
    "cohort": 3,
    "case-control": 2,
    "review": 2,
    "case report": 1,
    "expert opinion": 1,
}

def validate_and_rerank(chunks: list[dict]) -> list[dict]:
    """
    Filter and rerank chunks:
    - Remove duplicates (by pmid/doi)
    - Score by evidence level × recency × relevance
    - Keep only high-signal evidence
    """
    from datetime import datetime
    current_year = datetime.now().year
    import math

    seen_ids = set()
    filtered = []

    for c in chunks:
        meta = c["metadata"]
        uid = meta.get("pmid_or_doi", meta.get("title", "")[:50])
        if uid in seen_ids:
            continue
        seen_ids.add(uid)

        level = meta.get("evidence_level", "review")
        level_score = EVIDENCE_RANK.get(level, 1)
        recency = max(0, 10 - (current_year - meta.get("year", 2010)))
        final = (level_score * 2 + recency * 0.5 + c["relevance_score"] * 3)

        filtered.append({**c, "final_score": round(final, 3)})

    filtered.sort(key=lambda x: x["final_score"], reverse=True)
    return filtered[:5]   # Keep top 5 high-quality chunks