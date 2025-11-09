# --- STAGE 1: The Builder ---
# Use a stable, compatible Python version
FROM python:3.11.7-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install the system-level libraries that Pillow needs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create the virtual environment
RUN python -m venv .venv

# Copy requirements and install them
COPY requirements.txt ./
RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: The Final Image ---
# Use the same slim image
FROM python:3.11.7-slim

WORKDIR /app

# Copy only the built virtual environment from the builder
COPY --from=builder /app/.venv .venv/
# Copy all your app code
COPY . .

# Set the PATH to use the venv
ENV PATH="/app/.venv/bin:$PATH"

# This CMD is good, but Render's Start Command will override it.
# We set it to 10000 as a best practice, as this is Render's default port.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
```
