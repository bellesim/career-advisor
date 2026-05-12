import re
import io

import httpx
import PyPDF2
import docx


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_jd_text(text: str) -> dict:
    return {"raw_text": text.strip()}


def parse_jd_file(content: bytes, ext: str) -> dict:
    try:
        if ext == "pdf":
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            raw_text = "\n".join(
                p.extract_text() or "" for p in reader.pages
            ).strip()
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(content))
            raw_text = "\n".join(
                p.text for p in doc.paragraphs if p.text.strip()
            ).strip()
        else:
            raw_text = ""
    except Exception:
        raw_text = ""
    return {"raw_text": raw_text}


def parse_jd_url(url: str) -> dict:
    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "html" in content_type:
            raw_text = _strip_html(resp.text)
        else:
            raw_text = resp.text.strip()
    except Exception as e:
        raw_text = f"Could not fetch URL: {e}"
    return {"raw_text": raw_text, "source_url": url}
