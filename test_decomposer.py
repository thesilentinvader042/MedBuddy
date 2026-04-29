# save as test_decomposer.py in your project root
import asyncio
from dotenv import load_dotenv
load_dotenv()

from pipeline.decomposer import decompose

async def test():
    result = await decompose(
        query="what causes dengue fever?",
        entities=["causes", "dengue", "fever"],
        patient_age=35
    )
    print(result)

asyncio.run(test())