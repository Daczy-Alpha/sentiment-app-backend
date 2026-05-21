from transformers import BertTokenizer, BertForSequenceClassification
from dotenv import load_dotenv
from database import DB_PATH
import os
import torch
import requests
import sqlite3
import datetime


MODEL_PATH = "/app/models/finbert"

tokenizer = None
model = None


def load_model():
    """
    Loads FinBERT from the local Docker image path.
    The model must be baked into the image at /app/models/finbert.
    """
    global tokenizer, model

    if tokenizer is not None and model is not None:
        return

    if not os.path.isdir(MODEL_PATH):
        raise RuntimeError(
            f"FinBERT model not found at {MODEL_PATH}. "
            "Rebuild the Docker image with FinBERT saved into /app/models/finbert."
        )

    tokenizer = BertTokenizer.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )

    model = BertForSequenceClassification.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )

    model.eval()


load_dotenv()

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
URL = "https://newsapi.org/v2/top-headlines"


def score_headline(text: str) -> dict:
    """
    Runs FinBERT inference on a financial headline and returns sentiment score.
    """
    load_model()

    token_ids = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    with torch.no_grad():
        output = model(**token_ids)

    logits = output.logits
    scores = torch.softmax(logits, dim=1).squeeze().tolist()

    labels = ["Positive", "Negative", "Neutral"]
    predicted_label = labels[scores.index(max(scores))]

    return {
        "label": predicted_label,
        "score": {
            "Positive": round(scores[0], 4),
            "Negative": round(scores[1], 4),
            "Neutral": round(scores[2], 4)
        }
    }


def fetch_headlines() -> list:
    """
    Fetches business headlines from NewsAPI.
    Returns an empty list instead of crashing if the API call fails.
    """
    if not NEWS_API_KEY:
        print("NEWS_API_KEY is missing.")
        return []

    params = {
        "category": "business",
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 50
    }

    try:
        response = requests.get(URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"NewsAPI fetch failed: {e}")
        return []

    articles_data = data.get("articles", [])

    clean_articles = []

    for article in articles_data:
        title = article.get("title")

        if not title or title == "N/A":
            continue

        clean_articles.append({
            "source": article.get("source", {}).get("name", "N/A"),
            "headline": title,
            "published_at": article.get("publishedAt", "N/A")
        })

    return clean_articles


def get_score_for_headlines() -> None:
    """
    Fetches headlines and prints sentiment scores.
    Useful for local/manual testing.
    """
    headlines = fetch_headlines()

    for article in headlines:
        result = score_headline(article["headline"])
        print(f"Headline: {article['headline']}")
        print(f"Score: {result['score']}")


def store_article(
    headline: str,
    source: str,
    label: str,
    positive: float,
    negative: float,
    neutral: float,
    published_at: str
) -> None:
    """
    Stores a scored article in SQLite.
    INSERT OR IGNORE prevents duplicate headlines from crashing the job.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO articles (
                headline,
                source,
                label,
                positive,
                negative,
                neutral,
                published_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            headline,
            source,
            label,
            positive,
            negative,
            neutral,
            published_at
        ))

        conn.commit()

    finally:
        conn.close()


def fetch_score_and_store() -> None:
    """
    Fetches headlines, scores them with FinBERT, and stores them in SQLite.
    Designed to be called safely by scheduler.py.
    """
    headlines = fetch_headlines()

    print(f"[{datetime.datetime.now()}] Fetched {len(headlines)} headlines")

    if not headlines:
        print(f"[{datetime.datetime.now()}] No headlines fetched. Skipping scoring.")
        return

    stored = 0

    for article in headlines:
        try:
            result = score_headline(article["headline"])

            store_article(
                headline=article["headline"],
                source=article["source"],
                label=result["label"],
                positive=result["score"]["Positive"],
                negative=result["score"]["Negative"],
                neutral=result["score"]["Neutral"],
                published_at=article["published_at"]
            )

            stored += 1

        except Exception as e:
            print(f"Failed to score/store article: {article.get('headline')}")
            print(f"Error: {e}")

    print(f"[{datetime.datetime.now()}] Stored/processed {stored} articles")


if __name__ == "__main__":
    fetch_score_and_store()