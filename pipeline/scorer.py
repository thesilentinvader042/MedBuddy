def score_confidence(
    chunks: list[dict],
    intent_confidence: float,
    answer: str,
) -> str:
    from datetime import datetime
    current_year = datetime.now().year

    # ── Hard rules first ─────────────────────────────────────────────
    if not chunks:
        return "low"

    # ── Evidence quality ──────────────────────────────────────────────
    level_map = {
        "guideline": 1.0, "meta-analysis": 0.95,
        "systematic review": 0.9, "RCT": 0.8,
        "cohort": 0.6, "review": 0.5,
        "case-control": 0.4, "case report": 0.3,
        "expert opinion": 0.2,
    }
    quality_scores = [
        level_map.get(c["metadata"].get("evidence_level", ""), 0.2)
        for c in chunks
    ]
    avg_quality = sum(quality_scores) / len(quality_scores)

    # ── Source authority ──────────────────────────────────────────────
    trusted = {"PubMed", "WHO", "CDC", "NICE", "FDA", "Cochrane"}
    source_score = sum(
        1 for c in chunks
        if c["metadata"].get("source") in trusted
    ) / len(chunks)

    # ── Recency ───────────────────────────────────────────────────────
    recency_scores = [
        max(0, 1 - (current_year - c["metadata"].get("year", 2010)) / 10)
        for c in chunks
    ]
    avg_recency = sum(recency_scores) / len(recency_scores)

    # ── Relevance — use raw score with NO hard cutoff ─────────────────
    # ChromaDB cosine scores for small DBs typically range 0.05–0.45
    # Do NOT apply a hard cutoff — just use it as a weighted factor
    avg_relevance = sum(
        c.get("relevance_score", 0) for c in chunks
    ) / len(chunks)

    # Normalize relevance to 0–1 range assuming max realistic score ~0.5
    # This prevents small DBs from always returning low confidence
    normalized_relevance = min(1.0, avg_relevance / 0.4)

    # ── Answer completeness ───────────────────────────────────────────
    completeness = min(1.0, len(answer.split()) / 80)

    # ── Final score ───────────────────────────────────────────────────
    total = (
        avg_quality          * 0.40 +
        source_score         * 0.25 +
        avg_recency          * 0.15 +
        intent_confidence    * 0.10 +
        normalized_relevance * 0.05 +
        completeness         * 0.05
    )

    print(f"[Scorer] quality={avg_quality:.2f} source={source_score:.2f} "
          f"recency={avg_recency:.2f} relevance={avg_relevance:.3f} "
          f"norm_relevance={normalized_relevance:.2f} total={total:.2f}")

    if total >= 0.65:
        return "high"
    elif total >= 0.40:
        return "medium"
    return "low"