# ---- base image ----
FROM python:3.10-slim

# ---- install system deps that wheels a volte richiedono ----
RUN apt-get update && apt-get install -y build-essential libmagic-dev && rm -rf /var/lib/apt/lists/*

# ---- python deps ----
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- copy src & expose ----
COPY . .
ENV PORT=8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

