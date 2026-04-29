import asyncio
from dotenv import load_dotenv
load_dotenv()

from pipeline.retriever import get_collection, build_bm25_index, hybrid_retrieve

async def test():
    # Check document count
    col = get_collection()
    print(f"Documents in store: {col.count()}")

    # Build BM25 index
    build_bm25_index()
    print("BM25 index built")

    # Test retrieval
    chunks = await hybrid_retrieve(
        sub_queries=["dengue fever causes symptoms"],
        top_k=3
    )
    print(f"\nRetrieved {len(chunks)} chunks:")
    for c in chunks:
        print(f"  - {c['metadata']['title'][:50]} | score: {c['relevance_score']}")

asyncio.run(test())