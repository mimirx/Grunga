from apscheduler.schedulers.background import BackgroundScheduler
from services.points_service import recomputeTotalsForUser
from services.connection import db_cursor
from services.connection import execute
from datetime import datetime, timedelta
import pytz

# This will later hold the actual scheduler instance
scheduler = None


def resetDailyTasks():
    tz = pytz.timezone("America/Chicago")
    now = datetime.now(tz)
    today = now.date()

    print(f"[{now}] Running daily streak check for {today}")

    # get all users
    with db_cursor() as db:
        db.execute("SELECT userId FROM users")
        users = db.fetchAll() or []

    for u in users:
        uid = u["userId"]

        # recompute totals to get daily points
        totals = recomputeTotalsForUser(uid)
        daily = totals["daily"]

        # record daily points
        from services.points_service import recordDailyPoints
        recordDailyPoints(uid, daily, today)

        # update streak
        with db_cursor(commit=True) as db2:
            db2.execute("SELECT streak FROM pointsTotals WHERE userId=%s", (uid,))
            row = db2.fetchOne()
            streak = row["streak"] if row else 0

            if daily >= 100:
                streak += 1
            else:
                streak = 0

            db2.execute("UPDATE pointsTotals SET streak=%s WHERE userId=%s", (streak, uid))

    print("Daily streak check complete.")


def expireChallenges():
    """Expire challenges whose time is up."""
    res = execute("""
        UPDATE challenges
        SET status = 'EXPIRED'
        WHERE status = 'PENDING'
        AND expiresAt <= NOW()
    """)
    print(f"[{datetime.now()}] Expired {res.get('rowCount')} challenge(s)")


def startScheduler(tz_str="America/Chicago"):
    """Initialize and start the APScheduler instance."""
    global scheduler

    if scheduler and scheduler.running:
        return scheduler  # already running

    tz = pytz.timezone(tz_str)
    scheduler = BackgroundScheduler(timezone=tz)

    # Daily streak job
    scheduler.add_job(
        resetDailyTasks,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_reset",
        replace_existing=True
    )

    # Expire challenges job
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
