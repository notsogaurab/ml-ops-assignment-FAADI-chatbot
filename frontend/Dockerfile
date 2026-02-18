FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy everything needed for the build
COPY pyproject.toml README.md app.py ./

# Install dependencies (system-wide)
# Install PyTorch CPU version first
RUN uv pip install --system torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu

# Then install the rest
RUN uv pip install --system .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
