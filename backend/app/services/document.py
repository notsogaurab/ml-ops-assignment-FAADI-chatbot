from pypdf import PdfReader

from .. import config


def parse_file(file):
    if file.filename.endswith(".pdf"):
        try:
            reader = PdfReader(file.file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {e}")
    elif file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Only PDF and TXT are supported.")


def chunk_text(
    text, chunk_size=config.settings.CHUNK_SIZE, overlap=config.settings.CHUNK_OVERLAP
):
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunks.append(text[start:])
            break

        break_point = text.rfind(" ", start, end)
        if break_point == -1 or break_point < start:
            break_point = end

        chunks.append(text[start:break_point])
        start = break_point - overlap

        if start >= break_point:
            start = break_point

    return [c.strip() for c in chunks if c.strip()]
