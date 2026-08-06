"""
Parses true_data (all files) into tagged chunks.
Reuses parse_text, parse_html, parse_office, parse_pdf and chunk_text from the main app.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.loaders.text import parse_text
from app.ingestion.loaders.html import parse_html
from app.ingestion.loaders.office import parse_office
from app.ingestion.loaders.pdf import parse_pdf
from app.ingestion.chunking.splitter import chunk_text

TRUE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATA", "true_data")


def parse_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".docx":
            return parse_office(file_path)
        elif ext == ".pptx":
            return parse_office(file_path)
        elif ext in (".txt", ".md"):
            return parse_text(file_path)
        elif ext in (".html", ".htm"):
            return parse_html(file_path)
        elif ext in (".pdf"):
            return parse_pdf(file_path)
    except Exception:
        pass
    return ""


def load_all_chunks() -> list[dict]:
    """
    Returns all chunks tagged with source filename and whether they are noise.
    Used by the eval pipeline to understand what context the RAG system draws from.
    """
    results = []

    for fname in sorted(os.listdir(TRUE_DATA_DIR)):
        fpath = os.path.join(TRUE_DATA_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        text = parse_file(fpath)
        if text:
            for chunk in chunk_text(text):
                results.append({"text": chunk, "source": fname, "is_noise": False})

    return results