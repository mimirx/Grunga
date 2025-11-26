from datetime import datetime, timedelta
import pytz
from services.connection import db_cursor
from services.points_service import recomputeTotalsForUser
from services.connection import execute

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def now_chicago():
    """Return current datetime in America/Chicago timezone."""
    tz = pytz.timezone("America/Chicago")
    return datetime.now(tz)


def today_due_at():
    """
    Returns today's expiration time: 23:59:59 Chicago time.
    """
    tz = pytz.timezone("America/Chicago")
    now = datetime.now(tz)
    due = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return due


def calculate_points(sets: int, reps: int) -> int:
    """
    Same formula used in workouts.
    """
    return int(sets) * int(reps)


# -------------------------------------------------------------------
# CREATE CHALLENGE
# -------------------------------------------------------------------

def create_challenge(fromUserId, toUserId, exerciseType, sets, reps):
    if fromUserId == toUserId:
        return {"ok": False, "error": "You cannot challenge yourself."}

    if sets <= 0 or reps <= 0:
        return {"ok": False, "error": "Sets and reps must be positive numbers."}

    pts = calculate_points(sets, reps)
    dueAt = today_due_at()

    with db_cursor(commit=True) as db:
        db.execute("""
            INSERT INTO challenges (
                fromUserId, toUserId, exerciseType, sets, reps, points, status, createdAt, dueAt
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', NOW(), %s)
        """, (fromUserId, toUserId, exerciseType, sets, reps, pts, dueAt))

    return {"ok": True, "points": pts}


# -------------------------------------------------------------------
# GET CHALLENGES FOR USER
# -------------------------------------------------------------------

def get_challenges_for_user(userId, box):
    """
    box = 'incoming' | 'active' | 'done'
    """

    with db_cursor() as db:
        if box == "incoming":
            db.execute("""
                SELECT *
                FROM challenges
                WHERE toUserId = %s
                  AND status = 'PENDING'
                ORDER BY createdAt DESC
            """, (userId,))
        elif box == "active":
            db.execute("""
                SELECT *
                FROM challenges
                WHERE (fromUserId = %s OR toUserId = %s)
                  AND status = 'ACTIVE'
                ORDER BY createdAt DESC
            """, (userId, userId))
        elif box == "done":
            db.execute("""
                SELECT *
                FROM challenges
                WHERE (fromUserId = %s OR toUserId = %s)
                  AND status = 'COMPLETED'
                ORDER BY createdAt DESC
            """, (userId, userId))
        else:
            return []

        return db.fetchAll() or []


# -------------------------------------------------------------------
# ACCEPT / DECLINE
# -------------------------------------------------------------------

def accept_challenge(challengeId, userId):
    with db_cursor() as db:
        db.execute("SELECT toUserId, status FROM challenges WHERE challengeId=%s", (challengeId,))
        row = db.fetchOne()

    if not row:
        return {"ok": False, "error": "Challenge not found."}

    if row["toUserId"] != userId:
        return {"ok": False, "error": "You cannot accept this challenge."}

    if row["status"] != "PENDING":
        return {"ok": False, "error": "Challenge is not pending."}

    with db_cursor(commit=True) as db:
        db.execute("""
            UPDATE challenges
            SET status = 'ACTIVE'
            WHERE challengeId = %s
        """, (challengeId,))

    return {"ok": True}


def decline_challenge(challengeId, userId):
    with db_cursor() as db:
        db.execute("SELECT toUserId, status FROM challenges WHERE challengeId=%s", (challengeId,))
        row = db.fetchOne()

    if not row:
        return {"ok": False, "error": "Challenge not found."}

    if row["toUserId"] != userId:
        return {"ok": False, "error": "You cannot decline this challenge."}

    if row["status"] != "PENDING":
        return {"ok": False, "error": "Challenge is not pending."}

    with db_cursor(commit=True) as db:
        db.execute("""
            UPDATE challenges
            SET status = 'DECLINED'
            WHERE challengeId=%s
        """, (challengeId,))

    return {"ok": True}


# -------------------------------------------------------------------
# COMPLETE CHALLENGE
# -------------------------------------------------------------------

def complete_challenge(challengeId, userId):
    """
    Completer gets x2 points, sender gets x1.
    """
    with db_cursor() as db:
        db.execute("""
            SELECT fromUserId, toUserId, points, status
            FROM challenges
            WHERE challengeId=%s
        """, (challengeId,))
        row = db.fetchOne()

    if not row:
        return {"ok": False, "error": "Challenge not found."}

    if row["status"] != "ACTIVE":
        return {"ok": False, "error": "Challenge is not active."}

    fromId = row["fromUserId"]
    toId = row["toUserId"]
    pts = int(row["points"])

    # Only receiver can complete
    if userId != toId:
        return {"ok": False, "error": "Only the receiver can complete this challenge."}

    completer_points = pts * 2
    sender_points = pts * 1

    with db_cursor(commit=True) as db:
        db.execute("""
            INSERT INTO pointsLedger (userId, points, reason, refId)
            VALUES (%s, %s, 'challenge_complete', %s)
        """, (toId, completer_points, str(challengeId)))

        db.execute("""
            INSERT INTO pointsLedger (userId, points, reason, refId)
            VALUES (%s, %s, 'challenge_reward_sender', %s)
        """, (fromId, sender_points, str(challengeId)))

        db.execute("""
            UPDATE challenges
            SET status = 'COMPLETED'
            WHERE challengeId=%s
        """, (challengeId,))

    # Recompute totals so UI updates instantly
    recomputeTotalsForUser(toId)
    recomputeTotalsForUser(fromId)

    return {"ok": True, "message": "Challenge completed."}