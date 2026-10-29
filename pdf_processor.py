
import pymupdf


def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    """Extract text from PDF pages and preserve page numbers."""

    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as pdf:

        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page": page_number,
                    "text": text
                })

    return pages
