import re


def normalize_text(text: str) -> str:
    """Lowercase and remove punctuation, collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # remove non-word characters, keep spaces
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
