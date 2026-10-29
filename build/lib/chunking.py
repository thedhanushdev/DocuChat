
def split_into_chunks(
    pages: list[dict],
    chunk_size: int = 180,
    overlap: int = 30
) -> list[dict]:
    """Split text into overlapping chunks."""

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0.")

    chunks = []
    chunk_id = 1

    for page in pages:
        words = page["text"].split()
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            text = " ".join(words[start:end])

            if text.strip():
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page["page"],
                    "text": text
                })
                chunk_id += 1

            if end == len(words):
                break

            start = end - overlap

    return chunks
