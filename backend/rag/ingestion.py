from pathlib import Path
import pymupdf

from .chunking import split_text


def load_pdf(file_path: str) -> list[dict]:

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text()

        if not text.strip():
            continue

        pages.append({
            "text": text,
            "page": page_number + 1
        })

    document.close()

    return pages


def ingest_pdf(file_path: str) -> list[dict]:

    pages = load_pdf(file_path)

    chunks = []

    for page in pages:

        text = page["text"]

        page_chunks = split_text(text)

        for chunk_index, chunk in enumerate(page_chunks):

            chunks.append({
                "text": chunk,
                "metadata": {
                    "source": Path(file_path).name,
                    "page": page["page"],
                    "chunk": chunk_index
                }
            })

    return chunks