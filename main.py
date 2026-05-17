from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import DB_PATH, init_db
import sqlite3
import nest_asyncio
import uvicorn
import threading
import os

init_db()

app = FastAPI()



FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "backend running"}


@app.get("/articles/latest")
def get_latest_articles():
    """
    Retrieves the latest financial articles from the SQLite database.
    Args:
        None
    Returns:
        A list of dictionaries containing the headline, source, label, and published_at
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT headline, source, label, published_at FROM articles ORDER BY published_at DESC LIMIT 400")
    rows = cursor.fetchall()
    conn.close()
    return [
    {"headline": row[0], "source": row[1], "label": row[2], "published_at": row[3]}
    for row in rows
    ]


@app.get("/sentiment/trend")
def get_sentiment_trend():
  """
  Retrieves the sentiment trend data from the SQLite database.
  Args:
      None
  Returns:
      A list of dictionaries containing the hour_bucket, label, and count.

  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("""
  SELECT strftime('%Y-%m-%d', published_at) AS hour_bucket,
  label,
  COUNT(*) AS count
  FROM articles
  GROUP BY hour_bucket, label
  ORDER BY hour_bucket ASC
  """)
  rows = cursor.fetchall()
  conn.close()
  return [
    {"hour_bucket": row[0], "label": row[1], "count": row[2]}
    for row in rows
  ]

@app.get("/sentiment/mood")
def get_sentiment_mood():
    """
    Retrieves the sentiment mood distribution from the last 24 hours.
    Args:
        None
    Returns:
        A list of dictionaries containing the label and count.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT label, COUNT(*) as count 
    FROM articles 
    WHERE published_at >= datetime('now', '-24 hours')
    GROUP BY label
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {"label": row[0], "count": row[1]}
        for row in rows
    ]


nest_asyncio.apply()

def run_server():
    """
    Runs the FastAPI server.
    Args:
        None
    Returns:
        None
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_server()
