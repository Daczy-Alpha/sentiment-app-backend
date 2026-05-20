from transformers import BertTokenizer, BertForSequenceClassification
from dotenv import load_dotenv
import os
import torch
import requests
import sqlite3
import datetime
from database import DB_PATH

MODEL_PATH = "/app/models/finbert"

tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        tokenizer = BertTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        model = BertForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)


load_dotenv()
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
URL = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"





def score_headline(text: str) -> dict:
  """
  Runs FinBERT inference on a financial headline and returns the sentiment score.
  Args:
    text: A string representing a financial headline.
  Returns:
    A dictionary containing the sentiment label and score.
  """

  # Lazy-load model only when needed
  load_model()

  token_ID = tokenizer(
      text,
      return_tensors="pt",
      padding=True,
      truncation=True
  )
  with torch.no_grad():
    output = model(**token_ID)
  logits = output.logits
  score = torch.softmax(logits, dim=1).squeeze().tolist()
  labels = ["Positive", "Negative", "Neutral"]

  predicted_label = labels[score.index(max(score))]

  return {
      "label" : predicted_label,
      "score" : {
          "Positive" : round(score[0], 4),
          "Negative" : round(score[1], 4),
          "Neutral" : round(score[2], 4)
      }
  }


def fetch_headlines() -> list:
    if not NEWS_API_KEY:
        print("NEWS_API_KEY is missing.")
        return []

    try:
        response = requests.get(URL, timeout=20)
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
    Retrieves financial headlines from NewsAPI and scores them using FinBERT.
    Args:
        None
    Returns:
        None
    """
    for headlines in fetch_headlines():
        result = score_headline(headlines["headline"])
        print(f'Headline: {headlines["headline"]}')
        print(f"Score: {result['score']}")






def store_article(headline: str, source: str, label: str, positive: float, negative: float,neutral: float, published_at: str) -> None:
    """
    Stores a financial article in the SQLite database.
    Args:
        headline: A string representing the headline of the article.
        source: A string representing the source of the article.
        label: A string representing the sentiment label of the article.
        positive: A float representing the probability of the article being positive.
        negative: A float representing the probability of the article being negative.
        neutral: A float representing the probability of the article being neutral.
        published_at: A string representing the date and time the article was published.
    Returns:
        None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO articles (headline, source, label, positive, negative, neutral, published_at)
    VALUES (?, ?, ?, ?, ?, ?, ?) """, (headline, source, label, positive, negative, neutral, published_at))
    conn.commit()
    conn.close()
    
    

def fetch_score_and_store() -> None:
    """
    Retrieves financial headlines from NewsAPI and scores them using FinBERT,
    then stores the results in a SQLite database without scheduler logging.
    Args:
        None
    Returns:
        None
    """
    headlines = fetch_headlines()
    print(f"[{datetime.datetime.now()}] Fetched {len(headlines)} headlines")

    stored = 0
    for article in headlines:
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
    print(f"[{datetime.datetime.now()}] Stored {stored} articles")



if __name__ == "__main__":
    fetch_score_and_store()
