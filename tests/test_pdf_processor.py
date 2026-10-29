
import fitz
from pdf_processor import extract_pdf_pages, split_into_chunks


# Create a small sample PDF for testing
doc = fitz.open()
page = doc.new_page()
page.insert_text(
    (72, 72),
    "DocuChat extracts text from PDF documents."
)
pdf_bytes = doc.tobytes()
doc.close()

pages = extract_pdf_pages(pdf_bytes)
chunks = split_into_chunks(pages)

assert len(pages) == 1
assert pages[0]["page"] == 1
assert "DocuChat" in pages[0]["text"]
assert len(chunks) == 1

print("PDF processor tests passed!")
