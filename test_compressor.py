import tiktoken
import pytest

from pipeline.compressor import compress_context

def test_compress_context_logic():
    """Unit test for logic verification"""
    mock_chunks = [
        {
            "metadata": {"source": "PubMed", "year": 2023, "pmid_or_doi": "12345"},
            "text": "First sentence. Second sentence. Third sentence should be removed. Fourth too."
        },
        {
            "metadata": {"source": "Nature", "year": 2024, "pmid_or_doi": "67890"},
            "text": "This is a very long chunk designed to test the token budget. " * 20
        }
    ]

    result = compress_context(mock_chunks)
    
    # 1. Check sentence trimming (should only see first 2 sentences)
    assert "Third sentence" not in result
    assert "First sentence. Second sentence." in result

    # 2. Check metadata formatting
    assert "[PubMed · 2023 · 12345]" in result

    # 3. Check Token Budget (should be under 200)
    from tiktoken import get_encoding
    enc = get_encoding("cl100k_base")
    assert len(enc.encode(result)) <= 200

def run_demonstration():
    """Visual test to see the output in the console"""
    print("\n--- COMPRESSION TEST OUTPUT ---\n")
    
    test_chunks = [
        {
            "metadata": {"source": "NEJM", "year": 2023, "pmid_or_doi": "10.1056/123"},
            "text": "Aspirin was found to be effective. The study followed 500 patients over 10 years. This sentence should be deleted."
        },
        {
            "metadata": {"source": "Lancet", "year": 2022, "pmid_or_doi": "10.1016/456"},
            "text": "Metformin reduces risks. Data shows significant improvement. Another extra sentence."
        },
        {
            "metadata": {"source": "HeavyText", "year": 2024, "pmid_or_doi": "999"},
            "text": "This chunk is quite wordy. " * 15 # Will likely push over budget
        }
    ]

    compressed = compress_context(test_chunks)
    
    # Calculate tokens for display
    enc = tiktoken.get_encoding("cl100k_base")
    token_count = len(enc.encode(compressed))

    print(compressed)
    print("\n" + "="*30)
    print(f"TOTAL TOKENS: {token_count} / 200")
    print("="*30)

if __name__ == "__main__":
    # Run the visual demo first
    run_demonstration()
    
    # Then run the formal tests
    pytest.main([__file__])