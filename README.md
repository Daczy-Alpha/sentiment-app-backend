# MARKET PULSE

> A live financial news intelligence dashboard. An automated pipeline fetches top business headlines and an AI model scores their sentiment. A FastAPI backend then serves this data to a real-time visualization dashboard.

---

## What this is

Most financial dashboards rely on manual data entry or basic keyword matching. This project asks: what if we used state-of-the-art NLP to gauge the actual mood of the market in real-time?

A background scheduled worker acts as the "Data Pipeline" — fetching hourly business headlines from NewsAPI and passing them through FinBERT, a pre-trained Large Language Model specifically tuned for financial sentiment. The pipeline calculates whether the news is Positive (Bullish), Negative (Bearish), or Neutral (Mixed), and stores it in a database. A FastAPI backend then serves these aggregated trends via REST endpoints to a responsive, standalone HTML/JS dashboard using Chart.js.

This project was built to demonstrate full-stack AI integration: from raw API data ingestion and AI model inference in the background, through a production-style REST API, to frontend data visualization.

---

## Architecture
```
News API (Live Data)
      │
      ▼
Background Scheduler (APScheduler)
      │  Hourly fetching of headlines
      │
      ▼
AI Sentiment Pipeline
      │  Hugging Face Transformers (ProsusAI/finbert)
      │  Calculates Positive/Negative/Neutral probabilities
      │
      ▼
State Storage (SQLite)
      │
      ▼
FastAPI Backend (Data endpoints & Frontend serving)
      │  /articles/latest
      │  /sentiment/trend
      │
      ▼
Dashboard
      │  Vanilla JS + Chart.js
      │
      ▼
End User Views Market Trends
```

---

## Tech stack

| Layer | Technology |
|---|---|
| AI model | Hugging Face Transformers — ProsusAI/finbert |
| Task scheduling | APScheduler |
| API framework | FastAPI |
| Database | SQLite3 |
| HTTP client | Requests |
| Frontend visualization | Vanilla JS + Chart.js |

---

## AI Model Engine

| Metric | Details |
|---|---|
| Base architecture | BERT-base-uncased |
| Fine-tuning dataset | Financial PhraseBank |
| Task | Sequence Classification |

Key sentiment labels output by the pipeline: `Positive` (mapped to Bullish), `Negative` (mapped to Bearish), `Neutral` (mapped to Mixed).

---

## Project structure
```
MARKET-PULSE/
├── database.py          # SQLite database schema and initialization
├── main.py              # FastAPI app — endpoints, CORS, and HTML serving
├── pipeline.py          # NewsAPI fetching & FinBERT scoring logic
├── scheduler.py         # APScheduler worker (runs pipeline hourly)
├── market_pulse.html    # Frontend dashboard with Chart.js
├── .env                 # Environment variables (NewsAPI Key)
└── README.md
```

---

## Running the application

**Requirements**
```bash
pip install fastapi uvicorn transformers torch requests python-dotenv apscheduler nest-asyncio
```

**Initialize the database**
```bash
python database.py
```

**Start the background worker (Terminal 1)**
```bash
python scheduler.py
```

**Start the API server (Terminal 2)**
```bash
python main.py
```

**Sample API request**
```bash
GET http://localhost:8000/articles/latest
```

**Sample API response**
```json
[
  {
    "headline": "Tech stocks rally as inflation cools",
    "source": "Reuters",
    "label": "Positive",
    "published_at": "2023-10-25T14:30:00Z"
  },
  {
    "headline": "Housing market sees sudden dip in mortgage applications",
    "source": "Bloomberg",
    "label": "Negative",
    "published_at": "2023-10-25T13:15:00Z"
  }
]
```

---

## Setting up the data pipeline

The data fetching pipeline requires a valid API key to operate. To reproduce the live data feed:

1. Register for a free API key at NewsAPI.org
2. Create a `.env` file in the root directory
3. Add your key to the file: `NEWS_API_KEY=your_api_key_here`
4. Run `scheduler.py` to trigger the first fetch and score cycle.

---

## Known issues

These architectural constraints were identified during local testing and are documented here intentionally — they represent the next engineering iteration for cloud deployment:

- **Database locking** — because the worker (`scheduler.py`) and API (`main.py`) run as separate processes hitting the same SQLite file, simultaneous read/writes can occasionally trigger a "database is locked" exception.
- **Ephemeral cloud storage** — standard deployment to platforms like Heroku/Render will wipe the `financial_news.db` file on restart. Migration to PostgreSQL is required for production.
- **Cold start delays** — the first time the pipeline runs, downloading the FinBERT model weights from Hugging Face takes time depending on internet speed.

---

## Background

Built as a solo project to bridge the gap between machine learning models and tangible, user-facing web applications. The goal was to step away from Jupyter notebooks and build a system that runs autonomously, updating itself without human intervention. 

It demonstrates the ability to handle both the heavyweight background processing required by modern NLP models and the lightweight, rapid response times required by modern web APIs.

---

*Project status: Local v1.0 complete.