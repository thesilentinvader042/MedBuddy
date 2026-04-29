import sys, os
sys.path.append('..')

# Forces chroma_store to always be at project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.retriever import add_document, build_bm25_index

# ── Sample docs — replace with real PubMed abstract text ────────────────
DOCS = [
    {
        "id": "pmid-35738000",
        "text": "Cetirizine is a second-generation antihistamine used for allergic rhinitis and urticaria. "
                "In children aged 6 months to 5 years, cetirizine may cause sedation in approximately 14% of patients. "
                "Dose in children 2-5 years: 2.5mg once daily. Safety profile is favorable compared to first-generation antihistamines.",
        "metadata": {
            "source": "PubMed", "title": "Cetirizine in Pediatric Populations: Safety Review",
            "authors": "Smith J et al.", "year": 2022, "pmid_or_doi": "PMID:35738000",
            "url": "https://pubmed.ncbi.nlm.nih.gov/35738000",
            "evidence_level": "systematic review",
        }
    },
    {
        "id": "who-dengue-2023",
        "text": "Dengue fever diagnosis is confirmed by NS1 antigen test (days 1-5) or IgM/IgG serology (from day 5). "
                "No specific antiviral treatment exists. Management is supportive: oral rehydration, paracetamol for fever. "
                "Avoid NSAIDs and aspirin due to bleeding risk. WHO warning signs: abdominal pain, persistent vomiting, bleeding.",
        "metadata": {
            "source": "WHO", "title": "Dengue: Guidelines for Diagnosis, Treatment, Prevention and Control",
            "authors": "WHO", "year": 2023, "pmid_or_doi": "WHO/HTM/NTD/DEN/2009.1",
            "url": "https://www.who.int/publications/i/item/9789241547871",
            "evidence_level": "guideline",
        }
    },
    {
        "id": "pmid-36780000",
        "text": "Acute chest pain in adults: STEMI is diagnosed by ST elevation ≥1mm in ≥2 contiguous leads on ECG. "
                "Door-to-balloon time should be ≤90 minutes per ESC 2023 guidelines. "
                "Troponin I or T elevation confirms myocardial necrosis. Aspirin 300mg + P2Y12 inhibitor immediately.",
        "metadata": {
            "source": "PubMed", "title": "ESC Guidelines for STEMI Management 2023",
            "authors": "Byrne RA et al.", "year": 2023, "pmid_or_doi": "PMID:36780000",
            "url": "https://pubmed.ncbi.nlm.nih.gov/36780000",
            "evidence_level": "guideline",
        }
    },
    {
        "id": "cdc-hypertension-2023",
        "text": "Hypertension affects approximately 47% of adults in the United States. "
                "Target blood pressure <130/80 mmHg for most adults per ACC/AHA guidelines. "
                "Lifestyle modification: DASH diet, sodium restriction <2.3g/day, 150 min/week moderate exercise. "
                "First-line pharmacotherapy: thiazide diuretics, ACE inhibitors, ARBs, or calcium channel blockers.",
        "metadata": {
            "source": "CDC", "title": "Facts About Hypertension",
            "authors": "CDC", "year": 2023, "pmid_or_doi": "",
            "url": "https://www.cdc.gov/bloodpressure/facts.htm",
            "evidence_level": "guideline",
        }
    },
    {
        "id": "pmid-diabetes-2023",
        "text": "Type 2 diabetes management: HbA1c target <7% for most adults. First-line: metformin 500mg twice daily "
                "with meals, titrated to 2000mg/day. GLP-1 agonists reduce cardiovascular risk. "
                "SGLT2 inhibitors reduce heart failure hospitalizations. Annual screening: HbA1c, renal function, lipids, eye exam.",
        "metadata": {
            "source": "PubMed", "title": "ADA Standards of Medical Care in Diabetes 2023",
            "authors": "American Diabetes Association", "year": 2023, "pmid_or_doi": "PMID:36507600",
            "url": "https://pubmed.ncbi.nlm.nih.gov/36507600",
            "evidence_level": "guideline",
        }
    },
]

if __name__ == "__main__":
    print("Loading documents into ChromaDB...")
    for doc in DOCS:
        add_document(doc["text"], doc["metadata"], doc["id"])
        print(f"  ✅ Added: {doc['metadata']['title'][:50]}")

    build_bm25_index()
    print(f"\n✅ Done. {len(DOCS)} documents loaded.")
    print("Run the API: uvicorn main:app --reload")