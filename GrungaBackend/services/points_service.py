from datetime import datetime, timedelta
import pytz
from collections import defaultdict
from services.connection import db_cursor as dbCursor

BOSS_MAX_HP = 500
DAMAGE_PER_POINT = 1


def nowCt():
    tz = pytz.timezone("America/Chicago")
    return datetime.now(tz)


def weekStartCt(dt):
    s = dt - timedelta(days=dt.weekday())
    return s.replace(hour=0, minute=0, second=0, microsecond=0)


def getBossAssetForWeek(dt: datetime) -> str:
    """
    Determines the boss image asset based on the current week.
    """
    week_number = dt.isocalendar()[1]
    
    if week_number % 2 == 0:
        return "week-boss.png"
    else:
        return "week-boss2.png"


def pointsForRow(sets, reps, workoutType):
    return int(sets) * int(reps)


def recomputeTotalsForUser(userId: int) -> dict:
    now = nowCt()
    ws = weekStartCt(now)
    we = ws + timedelta(days=7)
    today = now.date()

    # ================= WORKOUT POINTS =================
    with dbCursor() as db:
        db.execute("""
            SELECT sets, reps, workoutType, workoutDate
            FROM workouts
            WHERE userId=%s
        """, (userId,))
        rows = db.fetchAll() or []

    total = 0
    weekly = 0
    daily = 0

    for r in rows:
        pts = pointsForRow(r["sets"], r["reps"], r["workoutType"])
        total += pts

        d = r["workoutDate"]
        if isinstance(d, datetime):
            d = d.date()

        if ws.date() <= d < we.date():
            weekly += pts
        if d == today:
            daily += pts

    # ================= CHALLENGE POINTS =================
    with dbCursor() as db:
        db.execute("""
            SELECT points, occurredAt
            FROM pointsLedger
            WHERE userId=%s
            AND reason IN ('challenge_complete', 'challenge_reward_sender')
        """, (userId,))
        challenge_rows = db.fetchAll() or []

    for c in challenge_rows:
        pts = int(c["points"])
        total += pts
        ts = c["occurredAt"].date()

        if ws.date() <= ts < we.date():
            weekly += pts
        if ts == today:
            daily += pts

    # ================= BOSS =================
    boss = bossFromWeekly(weekly, now)

    # ================= STREAK LOGIC =================
    with dbCursor() as db:
        db.execute("""
            SELECT streak, updatedAt
            FROM pointsTotals
            WHERE userId=%s
        """, (userId,))
        row = db.fetchOne()

    prev_streak = row["streak"] if row else 0
    last_update = row["updatedAt"].date() if row else None

    didAnythingToday = daily > 0
    yesterday = today - timedelta(days=1)

    streak = prev_streak

    # Only update streak once per day
    if didAnythingToday and last_update != today:
        if last_update == yesterday:
            streak = prev_streak + 1    # continue streak
        else:
            streak = 1                  # start new streak

    # ================= SAVE =================
    with dbCursor(commit=True) as db:
        db.execute("""
            UPDATE pointsTotals
            SET dailyPoints=%s,
                weeklyPoints=%s,
                totalPoints=%s,
                streak=%s,
                updatedAt=NOW()
            WHERE userId=%s
        """, (daily, weekly, total, streak, userId))

    return {
        "total": total,
        "weekly": weekly,
        "daily": daily,
        "streak": streak,
        "boss": boss
    }


def bossFromWeekly(weekly_points: int, now: datetime) -> dict:
    asset = getBossAssetForWeek(now)

    max_hp = int(BOSS_MAX_HP)
    dmg = weekly_points * DAMAGE_PER_POINT
    hp = max(0, max_hp - dmg)
    progress = 1 - (hp / max_hp) if max_hp > 0 else 0
    
    return {
        "maxHp": max_hp, 
        "hp": hp, 
        "progress": round(progress, 4),
        "asset": asset
    }


def weeklyHistogramForUser(userId: int) -> list:
    now = nowCt()
    ws = weekStartCt(now)
    we = ws + timedelta(days=7)

    # --------- WORKOUT POINTS ---------
    with dbCursor() as db:
        db.execute("""
            SELECT sets, reps, workoutType, workoutDate
            FROM workouts
            WHERE userId=%s AND workoutDate >= %s AND workoutDate < %s
        """, (userId, ws.date(), we.date()))
        workout_rows = db.fetchAll() or []

    byDay = defaultdict(int)

    for r in workout_rows:
        d = r["workoutDate"]
        if isinstance(d, datetime):
            d = d.date()

        pts = pointsForRow(r["sets"], r["reps"], r["workoutType"])
        byDay[d] += pts

    # --------- CHALLENGE POINTS ---------
    with dbCursor() as db:
        db.execute("""
            SELECT points, occurredAt
            FROM pointsLedger
            WHERE userId=%s 
              AND reason IN ('challenge_complete', 'challenge_reward_sender')
              AND occurredAt >= %s AND occurredAt < %s
        """, (userId, ws, we))
        challenge_rows = db.fetchAll() or []

    for c in challenge_rows:
        ts = c["occurredAt"]
        if isinstance(ts, datetime):
            d = ts.date()
        else:
            d = ts

        pts = int(c["points"])
        byDay[d] += pts

    # --------- GENERATE 7-DAY BIN LIST ---------
    bins = []
    for i in range(7):
        day = (ws + timedelta(days=i)).date()
        bins.append(int(byDay.get(day, 0)))

    return bins