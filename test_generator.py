import asyncio
from dotenv import load_dotenv
load_dotenv()

from pipeline.generator import generate

async def test():
    # Test 1 — disease inquiry
    print("=" * 50)
    print("TEST 1: Disease condition inquiry")
    print("=" * 50)
    result = await generate(
        query="what causes dengue fever?",
        compressed_context="""• Dengue fever is caused by the dengue virus (DENV), transmitted by Aedes aegypti mosquitoes. [WHO · 2023 · WHO/HTM/NTD]
- Four serotypes exist (DENV-1 to DENV-4). Infection with one serotype provides lifelong immunity to that type only. [PubMed · 2022 · PMID:35738000]
- Warning signs include abdominal pain, persistent vomiting, bleeding, and rapid breathing. [WHO · 2023 · WHO/HTM/NTD]""",
        intent="disease_condition_inquiry",
        patient_info="Age: 35, Sex: male",
        evidence_chunks=[]
    )
    print(result)

    # Test 2 — medication inquiry
    print("\n" + "=" * 50)
    print("TEST 2: Medication inquiry")
    print("=" * 50)
    result = await generate(
        query="is cetirizine safe for 5 year old boys?",
        compressed_context="""• Cetirizine is a second-generation antihistamine used for allergic rhinitis and urticaria. [PubMed · 2022 · PMID:35738000]
- In children aged 2-5 years, cetirizine may cause sedation in approximately 14% of patients. [PubMed · 2022 · PMID:35738000]
- Safety profile is favorable compared to first-generation antihistamines. [PubMed · 2022 · PMID:35738000]""",
        intent="medication_drug_inquiry",
        patient_info="Age: 5, Sex: male",
        evidence_chunks=[]
    )
    print(result)

    # Test 3 — empty context (should trigger insufficient evidence response)
    print("\n" + "=" * 50)
    print("TEST 3: Empty context (no evidence)")
    print("=" * 50)
    result = await generate(
        query="what is the cure for cancer?",
        compressed_context="No evidence retrieved.",
        intent="treatment_management",
        patient_info="Not provided",
        evidence_chunks=[]
    )
    print(result)

asyncio.run(test())