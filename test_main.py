# save as test_main.py in project root
import asyncio
from dotenv import load_dotenv
load_dotenv()

from models import QueryRequest
from main import run_pipeline

async def test():

    # Test 1 — disease in database
    print("=" * 55)
    print("TEST 1: Disease query (dengue — in database)")
    print("=" * 55)
    req = QueryRequest(query="what causes dengue fever?", age=35, sex="male")
    result = await run_pipeline(req)
    print(f"Intent:     {result.intent}")
    print(f"Confidence: {result.confidence}")
    print(f"Fallback:   {result.fallback}")
    print(f"Citations:  {len(result.citations)}")
    print(f"Answer:     {result.answer[:200]}...")
    print(f"Key points: {result.key_points[:2]}")

    # Test 2 — medication query
    print("\n" + "=" * 55)
    print("TEST 2: Medication query (cetirizine — in database)")
    print("=" * 55)
    req = QueryRequest(query="is cetirizine safe for children?", age=5, sex="male")
    result = await run_pipeline(req)
    print(f"Intent:     {result.intent}")
    print(f"Confidence: {result.confidence}")
    print(f"Fallback:   {result.fallback}")
    print(f"Citations:  {len(result.citations)}")
    print(f"Answer:     {result.answer[:200]}...")

    # Test 3 — query not in database (should trigger fallback gate)
    print("\n" + "=" * 55)
    print("TEST 3: Unknown query (not in database — expect fallback)")
    print("=" * 55)
    req = QueryRequest(query="what is the treatment for ebola?")
    result = await run_pipeline(req)
    print(f"Intent:     {result.intent}")
    print(f"Confidence: {result.confidence}")
    print(f"Fallback:   {result.fallback}")
    print(f"Reason:     {result.fallback_reason}")

asyncio.run(test())