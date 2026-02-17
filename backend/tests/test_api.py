from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


@patch("backend.app.services.document.parse_file")
@patch("backend.app.services.embedding.embedding_service.encode")
@patch("backend.app.services.vectorstore.vector_store.upsert")
@patch("backend.app.services.vectorstore.vector_store.ensure_collection")
@patch("backend.app.services.vectorstore.vector_store.has_filename", return_value=False)
def test_index_endpoint(mock_has, mock_ensure, mock_upsert, mock_encode, mock_parse):
    mock_parse.return_value = "Test content"
    mock_encode.return_value = [[0.1] * 384]

    files = {"file": ("test.txt", b"Test content", "text/plain")}
    response = client.post("/index", files=files)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_ensure.assert_called_once()
    mock_upsert.assert_called_once()


@patch("backend.app.services.vectorstore.vector_store.ensure_collection")
@patch("backend.app.services.vectorstore.vector_store.has_filename", return_value=True)
def test_index_duplicate_skipped(mock_has, mock_ensure):
    files = {"file": ("test.txt", b"Test content", "text/plain")}
    response = client.post("/index", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["num_chunks"] == 0


@patch("backend.app.services.embedding.embedding_service.encode")
@patch("backend.app.services.vectorstore.vector_store.search")
@patch("backend.app.services.llm.llm_service.generate")
@patch("backend.app.services.vectorstore.vector_store.ensure_collection")
@patch("backend.app.services.database.create_thread", new_callable=AsyncMock)
@patch("backend.app.services.database.add_message", new_callable=AsyncMock)
@patch("backend.app.services.database.get_recent_history", new_callable=AsyncMock)
def test_chat_endpoint(
    mock_history,
    mock_add_msg,
    mock_create,
    mock_ensure,
    mock_generate,
    mock_search,
    mock_encode,
):
    mock_encode.return_value = [[0.1] * 384]
    mock_search.return_value = [
        {"text": "Context 1", "score": 0.9, "metadata": {"filename": "test.txt"}}
    ]
    mock_generate.return_value = "This is the answer."
    mock_create.return_value = {
        "id": "thread-123",
        "title": "Hello?",
        "created_at": "",
        "updated_at": "",
    }
    mock_add_msg.return_value = "msg-123"
    mock_history.return_value = []

    response = client.post("/chat", json={"query": "Hello?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is the answer."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["text"] == "Context 1"
    assert data["thread_id"] == "thread-123"
