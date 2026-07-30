FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY app ./app
RUN mkdir -p data

ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT} --workers 1"]
