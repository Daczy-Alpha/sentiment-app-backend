from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline import fetch_score_and_store
from database import init_db

init_db()

scheduler = BlockingScheduler()

scheduler.add_job(fetch_score_and_store, 'interval', minutes=60)

if __name__ == "__main__":
    print("Scheduler started...")
    fetch_score_and_store()   # optional immediate first run
    scheduler.start()