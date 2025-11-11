from datetime import datetime, timedelta
import pytz
from collections import defaultdict
from services.connection import db_cursor as dbCursor

BOSS_MAX_HP = 1000          # total HP each week
DAMAGE_PER_POINT = 1        # 1 weekly point = 1 damage

def nowCt():
    tz = pytz.timezone("America/Chicago")
    return datetime.now(tz)

def weekStartCt(dt):
    s = dt - timedelta(days=dt.weekday())
    return s.replace(hour=0, minute=0, second=0, microsecond=0)

def pointsForRow(sets, reps, workoutType):
    return int(sets) * int(reps)

def recomputeTotalsForUser(userId: int) -> dict:
    now = nowCt()
    ws = weekStartCt(now)
    we = ws + timedelta(days=7)
    today = now.date()
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
    # boss HP derived from weekly points
    boss = bossFromWeekly(weekly)
    return {"total": total, "weekly": weekly, "daily": daily, "streak": 0, "boss": boss}

def bossFromWeekly(weekly_points: int) -> dict:
    max_hp = int(BOSS_MAX_HP)
    dmg = weekly_points * DAMAGE_PER_POINT
    hp = max(0, max_hp - dmg)
    progress = 1 - (hp / max_hp) if max_hp > 0 else 0
    return {"maxHp": max_hp, "hp": hp, "progress": round(progress, 4)}

def weeklyHistogramForUser(userId: int) -> list:
    now = nowCt()
    ws = weekStartCt(now)
    we = ws + timedelta(days=7)
    with dbCursor() as db:
        db.execute("""
            SELECT sets, reps, workoutType, workoutDate
            FROM workouts
            WHERE userId=%s AND workoutDate >= %s AND workoutDate < %s
        """, (userId, ws.date(), we.date()))
        rows = db.fetchAll() or []
    byDay = defaultdict(int)
    for r in rows:
        d = r["workoutDate"]
        if isinstance(d, datetime):
            d = d.date()
        pts = pointsForRow(r["sets"], r["reps"], r["workoutType"])
        byDay[d] += pts
    bins = []
    for i in range(7):
        day = (ws + timedelta(days=i)).date()
        bins.append(int(byDay.get(day, 0)))
    return bins
