from apscheduler.schedulers.background import BackgroundScheduler
from services.connection import db_cursor
from datetime import datetime
import pytz

scheduler = None

# Daily job no longer does streak logic
def resetDailyTasks():
    print(f"[{datetime.now()}] Daily maintenance run (no streak updates).")

def expireChallenges():
    with db_cursor(commit=True) as db:
        db.execute("""
            UPDATE challenges
            SET status = 'EXPIRED'
            WHERE status = 'PENDING'
              AND dueAt <= NOW()
        """)
    print(f"[{datetime.now()}] Expired old challenges.")

def startScheduler(tz_str="America/Chicago"):
    global scheduler

    if scheduler and scheduler.running:
        return scheduler

    tz = pytz.timezone(tz_str)
    scheduler = BackgroundScheduler(timezone=tz)

    # Daily job (no streak logic anymore)
    scheduler.add_job(
        resetDailyTasks,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_reset",
        replace_existing=True
    )

    scheduler.add_job(
        expireChallenges,
        trigger="cron",
        hour=0,
        minute=0,
        id="expire_challenges",
        replace_existing=True
    )

    scheduler.start()
    print(f"Scheduler started with timezone {tz_str}")
    return scheduler
