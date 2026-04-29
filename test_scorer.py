# save as test_scores.py in project root
import asyncio
from dotenv import load_dotenv
load_dotenv()

from pipeline.retriever import get_collection, build_bm25_index, hybrid_retrieve

async def test():
    get_collection()
    build_bm25_index()

    chunks = await hybrid_retrieve(
        sub_queries=["dengue fever causes"],
        top_k=5
    )
    print(f"Total chunks retrieved: {len(chunks)}\n")
    for c in chunks:
        print(f"  Title:     {c['metadata']['title'][:50]}")
        print(f"  Source:    {c['metadata']['source']}")
        print(f"  Vec score: {c.get('vec_score', 'N/A')}")
        print(f"  BM25:      {c.get('bm25_score', 'N/A')}")
        print(f"  Relevance: {c.get('relevance_score', 'N/A')}")
        print()

asyncio.run(test())