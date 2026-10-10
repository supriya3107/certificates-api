import re


def safe_filename(text: str, max_length: int = 60) -> str:
    cleaned = re.sub(r"[^\w\-]+", "_", text).strip("_")
    return cleaned[:max_length] or "certificate"