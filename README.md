# RAG Chatbot System

A production-grade Retrieval-Augmented Generation (RAG) system built with:

- **Backend**: FastAPI
- **Vector DB**: Qdrant
- **LLM**: Qwen2.5-0.5B-Instruct
- **Frontend**: Streamlit
- **Infrastructure**: Docker Compose

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- `uv` (recommended for local python management)
- GPU (optional, but recommended for LLM)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repo-url>
   cd ml-ops-assignment
   ```

2. **Setup Environment**:

   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Run with Docker Compose**:

   ```bash
   docker compose up --build
   ```

   - **Qdrant**: `http://localhost:6333`
   - **Backend**: `http://localhost:8000`
   - **Frontend**: `http://localhost:8501`

### Usage

1. Open the Frontend at `http://localhost:8501`.
2. Upload a PDF or TXT file using the sidebar.
3. Click "Index Document".
4. Once indexed, type your question in the chat bar.

## 🛠 Development

### Backend

```bash
cd backend
# Install dependencies
uv sync
# Run app
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
# Install dependencies
uv sync
# Run app
uv run streamlit run app.py
```

### Testing

```bash
cd backend
uv run pytest
```
