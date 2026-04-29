import re

def format_output(raw_text: str) -> tuple[str, list[str]]:
    """
    Parse LLM output into answer + key_points list.
    Returns (answer_paragraph, key_points_list).
    """
    lines = raw_text.strip().split('\n')
    answer_lines = []
    key_points = []
    in_key_points = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("key points:") or lower.startswith("key findings:"):
            in_key_points = True
            continue
        if lower.startswith("citations:") or lower.startswith("disclaimer:"):
            in_key_points = False
        if in_key_points and (line.startswith("•") or line.startswith("-") or line.startswith("*")):
            key_points.append(line.lstrip("•-* "))
        elif not in_key_points:
            answer_lines.append(line)

    answer = " ".join(answer_lines).strip()
    # Enforce brevity — truncate to ~150 tokens worth of text
    words = answer.split()
    if len(words) > 120:
        answer = " ".join(words[:120]) + "…"

    return answer, key_points