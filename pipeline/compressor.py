import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
TOKEN_BUDGET = 200

def compress_context(chunks: list[dict]) -> str:
    """
    Extract key facts from top chunks, stay within TOKEN_BUDGET.
    Returns a compressed context string for the LLM prompt.
    """
    lines = []
    total_tokens = 0

    for chunk in chunks:
        meta = chunk["metadata"]
        source_tag = f"[{meta.get('source','?')} · {meta.get('year','?')} · {meta.get('pmid_or_doi','')}"
        text = chunk["text"].strip()

        # Trim text to first 2 sentences
        sentences = text.split('. ')
        summary = '. '.join(sentences[:2]).strip()
        if not summary.endswith('.'):
            summary += '.'

        line = f"• {summary} {source_tag}]"
        tokens = len(enc.encode(line))

        if total_tokens + tokens > TOKEN_BUDGET:
            break

        lines.append(line)
        total_tokens += tokens

    return "\n".join(lines)