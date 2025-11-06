from apscheduler.schedulers.background import BackgroundScheduler
from services.connection import execute
from datetime import datetime
import pytz

scheduler = None


def resetDailyTasks():
    """Example scheduled job that would reset daily points or streaks."""
    print(f"[{datetime.now()}] Daily reset triggered.")
    # TODO: implement streak reset or daily points clear here
    # Example: execute("UPDATE streaks SET ...") once ready


def expireChallenges():
    """Expire challenges that reached their end time (Chicago time)."""
    res = execute("""
        UPDATE challenges
        SET status = 'EXPIRED'
        WHERE status = 'PENDING'
          AND expiresAt <= NOW()      -- NOW() uses America/Chicago
    """)
    print(f"[{datetime.now()}] Expired {res.get('rowCount')} challenge(s)")


def startScheduler(tz_str="America/Chicago"):
    """Start the background scheduler if not already running."""
    global scheduler
    if scheduler and scheduler.running:
        return scheduler  # Already running

    tz = pytz.timezone(tz_str)
    scheduler = BackgroundScheduler(timezone=tz)

    # Run both jobs at midnight Chicago time
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
    print(f"✅ APScheduler started (timezone: {tz_str})")
    return scheduler
