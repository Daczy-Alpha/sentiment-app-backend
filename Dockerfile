FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/models/finbert && \
    python -c "from transformers import BertTokenizer, BertForSequenceClassification; \
tokenizer = BertTokenizer.from_pretrained('ProsusAI/finbert'); \
model = BertForSequenceClassification.from_pretrained('ProsusAI/finbert'); \
tokenizer.save_pretrained('/app/models/finbert'); \
model.save_pretrained('/app/models/finbert')"

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]