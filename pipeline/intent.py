import os
from groq import AsyncGroq
import json, re

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

INTENT_SYSTEM = """You are a medical query classifier.
Classify the given query into exactly ONE of these intents:
general_information, disease_condition_inquiry, symptoms_differential,
treatment_management, medication_drug_inquiry, test_procedure_inquiry,
guideline_recommendation, other

Respond ONLY with valid JSON:
{"intent": "<one of the above>", "confidence": <0.0 to 1.0>}
No other text."""

async def classify_intent(normalized_query: str) -> dict:
    response = await client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        max_tokens=80,
        temperature=0.0,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM},
            {"role": "user",   "content": normalized_query},
        ],
    )
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"intent": "general_information", "confidence": 0.5}