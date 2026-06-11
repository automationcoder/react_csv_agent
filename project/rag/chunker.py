from typing import List


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        chunks: List[str] = []

        start = 0
        step = self.chunk_size - self.chunk_overlap

        while start < len(clean_text):
            end = start + self.chunk_size
            chunk = clean_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += step

        return chunks