from typing import List
import logfire

def _split_large_paragraph(paragraph: str, chunk_size: int) -> List[str]:
    """
    Split oversized paragraphs into fixed-size chunks.
    Technical documents often contain YAML, code blocks, tables,
    and command output where sentence-based splitting is unreliable.
    """
    if len(paragraph) <= chunk_size:
        return [paragraph]

    return [
        paragraph[i:i + chunk_size]
        for i in range(0, len(paragraph), chunk_size)
    ]

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 150) -> List[str]:
    """
    Paragraph-aware chunker with:
    - paragraph grouping
    - oversized paragraph splitting
    - overlapping chunks for improved retrieval
    """

    with logfire.span("✂️ Text Chunking", text_length=len(text)):
        if not text.strip():
            return []

        # Split into paragraphs first
        paragraphs = []

        for paragraph in text.split("\n\n"):
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            paragraphs.extend(
                _split_large_paragraph(paragraph, chunk_size)
            )

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:

            # Add paragraph if it fits
            if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
                current_chunk += paragraph + "\n\n"

            else:
                # Save previous chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Preserve overlap
                tail = current_chunk[-overlap:].strip()

                current_chunk = ""

                if tail:
                    current_chunk += tail + "\n\n"

                current_chunk += paragraph + "\n\n"

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        logfire.info(f"✅ Generated {len(chunks)} chunks")

        return chunks