FALLBACK_REFERENCES = {
    "medication_drug_inquiry": [
        "PubMed Search: https://pubmed.ncbi.nlm.nih.gov",
        "FDA Drug Database: https://www.fda.gov/drugs",
        "WHO Essential Medicines: https://www.who.int/medicines",
    ],
    "disease_condition_inquiry": [
        "PubMed Search: https://pubmed.ncbi.nlm.nih.gov",
        "WHO Disease Fact Sheets: https://www.who.int/news-room/fact-sheets",
        "CDC Health Topics: https://www.cdc.gov/az",
    ],
    "default": [
        "PubMed Search: https://pubmed.ncbi.nlm.nih.gov",
        "NICE Evidence Search: https://www.evidence.nhs.uk",
        "Cochrane Library: https://www.cochranelibrary.com",
    ],
}

def gate_check(confidence: str, chunks: list[dict], intent: str) -> dict:
    refs = FALLBACK_REFERENCES.get(intent, FALLBACK_REFERENCES["default"])

    if not chunks:
        return {
            "pass": False,
            "reason": "No relevant evidence found in trusted sources for this query.",
            "fallback_refs": refs,
        }

    if confidence == "low":
        return {
            "pass": False,
            "reason": "Low confidence in retrieved evidence. Insufficient high-quality data for this query.",
            "fallback_refs": refs,
        }

    return {"pass": True, "reason": "", "fallback_refs": []}