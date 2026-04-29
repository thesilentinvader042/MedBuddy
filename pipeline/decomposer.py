import os
from groq import AsyncGroq
import json, re

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

DECOMPOSE_SYSTEM = """You are a medical search query specialist.
Break the user's question into 3–5 focused search sub-queries.
Add medical synonyms to improve retrieval.
Include age/demographic details if given.
Return ONLY valid JSON: {"sub_queries": ["q1", "q2", "q3"]}
No other text."""

async def decompose(query: str, entities: list[str], patient_age: int = None) -> list[str]:
    context = query
    if patient_age:
        context += f" (patient age: {patient_age})"

    response = await client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        max_tokens=200,
        temperature=0.2,
        messages=[
            {"role": "system", "content": DECOMPOSE_SYSTEM},
            {"role": "user",   "content": context},
        ],
    )
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        parsed = json.loads(match.group())
        return parsed.get("sub_queries", [query])
    return [query]