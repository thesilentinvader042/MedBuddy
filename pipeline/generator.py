import os
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

INTENT_SCHEMAS = {
    "medication_drug_inquiry":    "Drug summary, Effects/side effects, Safety in children (if relevant), Contraindications, Key notes, Citations",
    "disease_condition_inquiry":  "Overview, Causes/risk factors, Symptoms, Diagnosis, Management, Citations",
    "symptoms_differential":      "Most likely diagnoses (ranked), Supporting features, Red flags, Recommended workup, Citations",
    "treatment_management":       "First-line treatment, Second-line options, Monitoring, Special populations, Citations",
    "test_procedure_inquiry":     "Purpose, When indicated, Normal ranges, Interpretation, Citations",
    "guideline_recommendation":   "Guideline source, Recommendation, Strength of evidence, Caveats, Citations",
    "general_information":        "Answer, Key points, Citations",
}

SYSTEM_PROMPT = """You are MedQA, a medical evidence synthesis assistant for healthcare professionals.

STRICT RULES:
1. ONLY use facts from the evidence provided. Never add information not in the context.
2. Cite EVERY fact with [Source · Year · PMID/DOI].
3. Never recommend specific drug doses — provide general information only.
4. Always end with the disclaimer.
5. If evidence is insufficient, say so clearly — do not fabricate an answer.
6. Use the schema matching the detected intent.
7. Respond in clear, structured plain text. Use section labels followed by a colon.

DISCLAIMER (include always at the end):
"For informational purposes only. Not a substitute for professional medical advice, diagnosis, or treatment."
"""

async def generate(
    query: str,
    compressed_context: str,
    intent: str,
    patient_info: str,
    evidence_chunks: list,
) -> str:
    schema = INTENT_SCHEMAS.get(intent, INTENT_SCHEMAS["general_information"])

    user_content = f"""Question: {query}

Patient context: {patient_info or 'Not provided'}

Evidence (source-bound facts only — do not use any knowledge outside this):
{compressed_context}

Output schema to follow: {schema}"""

    response = await client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        max_tokens=900,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ],
    )
    return response.choices[0].message.content