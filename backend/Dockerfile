# Bookworm (Debian 12): Microsoft publishes msodbcsql18 for it.
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tesseract-ocr tesseract-ocr-ita \
    && curl -fsSL -o /tmp/packages-microsoft-prod.deb https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && rm /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Creates the database, schema and demo data on first start; no-op afterwards.
CMD ["sh", "-c", "python -m db.init_db && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
