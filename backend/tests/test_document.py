from backend.app.services.document import chunk_text


def test_chunk_text_simple():
    text = "Hello world this is a test"
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) > 0
    # "Hello worl" (10 chars)
    # "rl..." overlap


def test_chunk_text_empty():
    assert chunk_text("", 100, 10) == []


def test_chunk_text_overlap():
    text = "1234567890"
    # size 5, overlap 2
    # 0-5: "12345"
    # next start: 5 - 2 = 3. 3-8: "45678"
    # next start: 8 - 2 = 6. 6-11: "7890"
    chunks = chunk_text(text, 5, 2)
    assert chunks == ["12345", "45678", "7890"]
