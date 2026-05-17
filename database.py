import sqlite3

DB_PATH = "/app/data/financial_news.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            headline     TEXT UNIQUE,
            source       TEXT,
            label        TEXT,
            positive     REAL,
            negative     REAL,
            neutral      REAL,
            published_at TEXT
        )
    """)

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduler_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            triggered_at TEXT,
            fetched   INTEGER,
            stored    INTEGER
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialised.")