from datetime import datetime
from typing import Optional, Dict, Any

from .connection import fetchOne, execute
from .connection import Db

# Points rule (we can imorove/evolve it later)
def calcWorkoutPoints(workoutType: str, sets: int, reps: int) -> int:
    try:
        sets = int(sets)
        reps = int(reps)
    except ValueError:
        return 0
    if sets <= 0 or reps <= 0:
        return 0
    return sets * reps


def writePoints(userId: int, points: int, reason: str, refId: Optional[str] = None) -> Dict[str, Any]:
    with Db() as db:
        # 1) ledger insert
        db.execute(
            "INSERT INTO pointsLedger (userId, points, reason, refId) VALUES (%s, %s, %s, %s)",
            (userId, points, reason, refId)
        )
        last_id = db.lastRowId()

        # 2) ensure totals row
        db.execute(
            """
            INSERT INTO pointsTotals (userId)
            SELECT %s FROM DUAL
            WHERE NOT EXISTS (SELECT 1 FROM pointsTotals WHERE userId = %s)
            """,
            (userId, userId)
        )

        # 3) recompute cached totals (see Fix #2 below for Chicago time correctness)
        db.execute(
            """
            UPDATE pointsTotals t
            JOIN (
              SELECT
                userId,
                COALESCE(SUM(points), 0) AS totalPoints,
                COALESCE(SUM(CASE WHEN DATE(occurredAt) = CURRENT_DATE() THEN points END), 0) AS dailyPoints,
                COALESCE(SUM(
                  CASE WHEN YEARWEEK(occurredAt, 1) = YEARWEEK(CURRENT_DATE(), 1) THEN points END
                ), 0) AS weeklyPoints
              FROM pointsLedger
              WHERE userId = %s
              GROUP BY userId
            ) s ON s.userId = t.userId
            SET t.totalPoints  = s.totalPoints,
                t.dailyPoints  = s.dailyPoints,
                t.weeklyPoints = s.weeklyPoints,
                t.updatedAt    = NOW()
            """,
            (userId,)
        )

        return {"lastRowId": last_id, "rowCount": 1}


# Read the cached totals (compute if missing)
def getTotals(userId: int) -> Dict[str, int]:
    row = fetchOne(
        "SELECT dailyPoints, weeklyPoints, totalPoints FROM pointsTotals WHERE userId = %s",
        (userId,)
    )
    if row:
        return row  # {'dailyPoints': ..., 'weeklyPoints': ..., 'totalPoints': ...}

    # No cached row yet
    totals = fetchOne(
        """
        SELECT
          COALESCE(SUM(points), 0) AS totalPoints,
          COALESCE(SUM(CASE WHEN DATE(occurredAt) = CURRENT_DATE() THEN points END), 0) AS dailyPoints,
          COALESCE(SUM(
            CASE WHEN YEARWEEK(occurredAt, 1) = YEARWEEK(CURRENT_DATE(), 1) THEN points END
          ), 0) AS weeklyPoints
        FROM pointsLedger
        WHERE userId = %s
        """,
        (userId,)
    ) or {"totalPoints": 0, "dailyPoints": 0, "weeklyPoints": 0}

    execute(
        """
        INSERT INTO pointsTotals (userId, dailyPoints, weeklyPoints, totalPoints)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          dailyPoints = VALUES(dailyPoints),
          weeklyPoints = VALUES(weeklyPoints),
          totalPoints = VALUES(totalPoints),
          updatedAt = NOW()
        """,
        (userId, totals["dailyPoints"], totals["weeklyPoints"], totals["totalPoints"])
    )
    return totals
