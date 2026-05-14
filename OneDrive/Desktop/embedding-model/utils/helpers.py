def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def score_to_percentage(score: float) -> str:
    return f"{score * 100:.1f}%"


def get_score_color(score: float) -> str:
    if score >= 0.6:
        return "green"
    elif score >= 0.35:
        return "orange"
    else:
        return "red"