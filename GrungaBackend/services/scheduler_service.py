# GrungaBackend/services/scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

# Optional: Import functions you want to run nightly
# from services.streak_service import resetDailyPoints

scheduler = None

def resetDailyTasks():
    """Example scheduled job that would reset daily points or streaks."""
    print(f"[{datetime.now()}] Daily reset triggered.")
    # resetDailyPoints()  # Uncomment once implemented

def startScheduler(tz_str="America/Chicago"):
    """Start the background scheduler if not already running."""
    global scheduler
    if scheduler and scheduler.running:
        return scheduler  # Already running

    tz = pytz.timezone(tz_str)
    scheduler = BackgroundScheduler(timezone=tz)

    # Example: run resetDailyTasks every midnight
    scheduler.add_job(
        resetDailyTasks,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_reset",
        replace_existing=True
    )

    scheduler.start()
    print(f"✅ APScheduler started (timezone: {tz_str})")
    return scheduler
