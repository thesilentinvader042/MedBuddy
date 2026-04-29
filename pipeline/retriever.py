import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from rank_bm25 import BM25Okapi
import json, os

# Trusted source whitelist
TRUSTED_SOURCES = {"PubMed", "WHO", "CDC", "NICE", "FDA", "Cochrane"}

_chroma_client = None
_collection = None
_bm25 = None
_bm25_docs = []    # list of (doc_text, metadata) for BM25

def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        ef = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"   # fast, 384-dim, runs on CPU
        )
        _chroma_client = chromadb.PersistentClient(path="./chroma_store")
        _collection = _chroma_client.get_or_create_collection(
            name="medical_docs",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection

def build_bm25_index():
    """Build BM25 index from all docs in Chroma. Call after loading docs."""
    global _bm25, _bm25_docs
    col = get_collection()
    all_docs = col.get(include=["documents", "metadatas"])
    if not all_docs["documents"]:
        _bm25 = None
        return
    _bm25_docs = list(zip(all_docs["documents"], all_docs["metadatas"]))
    tokenized = [doc.lower().split() for doc in all_docs["documents"]]
    _bm25 = BM25Okapi(tokenized)

def add_document(text: str, metadata: dict, doc_id: str):
    """Add a single document to the vector store."""
    col = get_collection()
    col.upsert(
        documents=[text],
        metadatas=[metadata],
        ids=[doc_id],
    )

async def hybrid_retrieve(sub_queries: list[str], top_k: int = 5) -> list[dict]:
    """
    Hybrid retrieval: vector search + BM25 → fused + deduplicated chunks.
    Returns list of chunk dicts with metadata.
    """
    col = get_collection()
    seen_ids = set()
    scored: dict[str, dict] = {}

    for query in sub_queries:
        # ── Vector search ────────────────────────────────────────────────
        vec_results = col.query(
            query_texts=[query],
            n_results=min(top_k, col.count() or 1),
            include=["documents", "metadatas", "distances"],
        )
        for doc, meta, dist in zip(
            vec_results["documents"][0],
            vec_results["metadatas"][0],
            vec_results["distances"][0],
        ):
            uid = meta.get("pmid_or_doi", doc[:40])
            if uid not in seen_ids:
                seen_ids.add(uid)
                vec_score = 1 - dist    # cosine: lower distance = higher score
                scored[uid] = {
                    "text": doc, "metadata": meta,
                    "vec_score": vec_score, "bm25_score": 0.0,
                }
            else:
                scored[uid]["vec_score"] = max(scored[uid]["vec_score"], 1 - dist)

        # ── BM25 search ──────────────────────────────────────────────────
        if _bm25 and _bm25_docs:
            bm25_scores = _bm25.get_scores(query.lower().split())
            top_indices = sorted(range(len(bm25_scores)),
                                  key=lambda i: bm25_scores[i], reverse=True)[:top_k]
            for idx in top_indices:
                doc, meta = _bm25_docs[idx]
                uid = meta.get("pmid_or_doi", doc[:40])
                norm_score = bm25_scores[idx] / (max(bm25_scores) + 1e-9)
                if uid in scored:
                    scored[uid]["bm25_score"] = max(scored[uid]["bm25_score"], norm_score)
                elif uid not in seen_ids:
                    seen_ids.add(uid)
                    scored[uid] = {
                        "text": doc, "metadata": meta,
                        "vec_score": 0.0, "bm25_score": norm_score,
                    }

    # ── Fusion score: 60% vector + 40% BM25 ────────────────────────────
    results = []
    for uid, item in scored.items():
        fused = 0.6 * item["vec_score"] + 0.4 * item["bm25_score"]
        item["relevance_score"] = round(fused, 4)
        # Whitelist filter
        if item["metadata"].get("source") in TRUSTED_SOURCES:
            results.append(item)

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:top_k]