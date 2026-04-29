# save as test_intent.py in your project root
import asyncio
from dotenv import load_dotenv
load_dotenv()

from pipeline.intent import classify_intent

async def test():
    result = await classify_intent("what causes dengue fever?")
    print(result)

asyncio.run(test())