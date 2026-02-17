FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy everything needed for the build
COPY pyproject.toml README.md ./
COPY app/ app/

# Install dependencies (system-wide)
RUN uv pip install --system .

# Copy tests
COPY tests/ tests/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
