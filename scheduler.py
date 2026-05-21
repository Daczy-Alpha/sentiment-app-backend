from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline import fetch_score_and_store
from database import init_db
import traceback
import datetime

def safe_fetch():
    try:
        fetch_score_and_store()
    except Exception:
        print("Scheduler job failed, but pod will continue running.")
        traceback.print_exc()

if __name__ == "__main__":
    init_db()

    scheduler = BlockingScheduler()

    scheduler.add_job(
        safe_fetch,
        "interval",
        minutes=60,
        next_run_time=datetime.datetime.now()
    )

    print("Scheduler started. First fetch will run immediately, then every 60 minutes.")
    scheduler.start()