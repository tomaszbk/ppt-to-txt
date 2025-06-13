FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-impress \
    libreoffice-common \
    fonts-dejavu \
    poppler-utils \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync

# Copy application code
COPY . .

# Run the application
CMD ["uv", "run", "main.py"]