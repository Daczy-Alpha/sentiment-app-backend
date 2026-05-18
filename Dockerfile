FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download FinBERT model
RUN python -c "from transformers import BertTokenizer, BertForSequenceClassification; \
BertTokenizer.from_pretrained('ProsusAI/finbert'); \
BertForSequenceClassification.from_pretrained('ProsusAI/finbert')"

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]