import pytest
from datetime import datetime

from pipeline.validator import validate_and_rerank 

def test_validate_and_rerank():
    current_year = datetime.now().year
    
    mock_chunks = [
        # 1. High Evidence (Meta-analysis), Recent (this year), High Relevance
        {
            "metadata": {"pmid_or_doi": "1", "evidence_level": "meta-analysis", "year": current_year, "title": "A"},
            "relevance_score": 0.9,
        },
        # 2. Duplicate of ID "1" (Should be ignored)
        {
            "metadata": {"pmid_or_doi": "1", "evidence_level": "case report", "year": 2000, "title": "A-duplicate"},
            "relevance_score": 1.0,
        },
        # 3. Lower Evidence (Cohort), Older (10 years ago), High Relevance
        {
            "metadata": {"pmid_or_doi": "2", "evidence_level": "cohort", "year": current_year - 10, "title": "B"},
            "relevance_score": 0.9,
        },
        # 4. Guideline (Rank 6), Recent, but low relevance
        {
            "metadata": {"pmid_or_doi": "3", "evidence_level": "guideline", "year": current_year, "title": "C"},
            "relevance_score": 0.2,
        },
        # 5-8. Filler to test the top 5 limit
        {"metadata": {"pmid_or_doi": "4", "year": 2010}, "relevance_score": 0.1},
        {"metadata": {"pmid_or_doi": "5", "year": 2010}, "relevance_score": 0.1},
        {"metadata": {"pmid_or_doi": "6", "year": 2010}, "relevance_score": 0.1},
        {"metadata": {"pmid_or_doi": "7", "year": 2010}, "relevance_score": 0.1},
    ]

    result = validate_and_rerank(mock_chunks)

    # ASSERTIONS
    
    # 1. Check Truncation: Should only return top 5
    assert len(result) == 5

    # 2. Check Deduplication: ID "1" should only appear once
    ids = [c["metadata"]["pmid_or_doi"] for c in result]
    assert ids.count("1") == 1

    # 3. Check Ranking Logic: 
    # High evidence/recent/relevant (ID 1) should be first.
    # Level 5 * 2 = 10
    # Recency (10 - 0) * 0.5 = 5
    # Relevance 0.9 * 3 = 2.7
    # Total = 17.7
    assert result[0]["metadata"]["pmid_or_doi"] == "1"
    assert "final_score" in result[0]

def test_missing_metadata_defaults():
    # Test how the function handles missing keys
    incomplete_chunks = [
        {
            "metadata": {"title": "Missing Info Paper"}, # No pmid, no level, no year
            "relevance_score": 0.5
        }
    ]
    
    try:
        result = validate_and_rerank(incomplete_chunks)
        assert len(result) == 1
        # Default level "review" is rank 2. Default year 2010.
        # Score calculation: (2*2) + (recency*0.5) + (0.5*3)
        assert result[0]["final_score"] > 0
    except KeyError as e:
        pytest.fail(f"Function crashed on missing metadata: {e}")

if __name__ == "__main__":
    # If running without pytest cli
    pytest.main([__file__])