FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/models/finbert /app/data

RUN python -c "from transformers import BertTokenizer, BertForSequenceClassification; \
BertTokenizer.from_pretrained('ProsusAI/finbert').save_pretrained('/app/models/finbert'); \
BertForSequenceClassification.from_pretrained('ProsusAI/finbert').save_pretrained('/app/models/finbert')"

ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]