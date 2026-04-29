# save as test_binder.py in project root
import asyncio
from dotenv import load_dotenv
load_dotenv()

from pipeline.binder import bind_evidence

def test():
    # Simulate validated chunks coming from validator.py
    sample_chunks = [
        {
            "text": "Dengue fever is caused by the dengue virus transmitted by Aedes aegypti mosquitoes. Four serotypes exist.",
            "metadata": {
                "source": "WHO",
                "title": "Dengue: Guidelines for Diagnosis, Treatment, Prevention and Control",
                "authors": "WHO",
                "year": 2023,
                "pmid_or_doi": "WHO/HTM/NTD/DEN/2009.1",
                "url": "https://www.who.int/publications/i/item/9789241547871",
                "evidence_level": "guideline",
            },
            "relevance_score": 0.91,
            "final_score": 8.2,
        },
        {
            "text": "Cetirizine is a second-generation antihistamine. It may cause sedation in approximately 14% of children.",
            "metadata": {
                "source": "PubMed",
                "title": "Cetirizine in Pediatric Populations: Safety Review",
                "authors": "Smith J et al.",
                "year": 2022,
                "pmid_or_doi": "PMID:35738000",
                "url": "https://pubmed.ncbi.nlm.nih.gov/35738000",
                "evidence_level": "systematic review",
            },
            "relevance_score": 0.74,
            "final_score": 6.1,
        },
    ]

    bound = bind_evidence(sample_chunks)

    print(f"Bound {len(bound)} evidence chunks:\n")
    for e in bound:
        print(f"  Source:         {e.source}")
        print(f"  Title:          {e.title}")
        print(f"  Authors:        {e.authors}")
        print(f"  Year:           {e.year}")
        print(f"  PMID/DOI:       {e.pmid_or_doi}")
        print(f"  URL:            {e.url}")
        print(f"  Evidence level: {e.evidence_level}")
        print(f"  Excerpt:        {e.excerpt}")
        print(f"  Relevance:      {e.relevance_score}")
        print()

test()