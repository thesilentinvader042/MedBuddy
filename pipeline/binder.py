from models import EvidenceChunk

def bind_evidence(chunks: list[dict]) -> list[EvidenceChunk]:
    """
    Attach source metadata to each fact — the anti-hallucination core.
    Every fact reaching the LLM must carry: source, PMID/DOI, year, evidence_level.
    """
    bound = []
    for c in chunks:
        m = c["metadata"]
        bound.append(EvidenceChunk(
            source=m.get("source", "Unknown"),
            title=m.get("title", "Untitled"),
            authors=m.get("authors", ""),
            year=m.get("year", 0),
            pmid_or_doi=m.get("pmid_or_doi"),
            url=m.get("url", ""),
            evidence_level=m.get("evidence_level", "review"),
            excerpt=c["text"][:120].rstrip() + "…",   # paraphrased excerpt
            relevance_score=round(c.get("relevance_score", 0), 3),
        ))
    return bound