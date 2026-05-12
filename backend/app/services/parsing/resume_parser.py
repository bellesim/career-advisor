import io

import PyPDF2
import docx


def extract_text_from_pdf(content: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(content))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages).strip()


def extract_text_from_docx(content: bytes) -> str:
    doc = docx.Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()


def parse_resume(content: bytes, ext: str) -> dict:
    try:
        if ext == "pdf":
            raw_text = extract_text_from_pdf(content)
        elif ext == "docx":
            raw_text = extract_text_from_docx(content)
        else:
            raw_text = ""
    except Exception:
        raw_text = ""
    return {"raw_text": raw_text}
