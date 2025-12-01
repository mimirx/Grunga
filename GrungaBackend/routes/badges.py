from flask import Blueprint, jsonify
from services.connection import db_cursor as dbCursor

bpBadges = Blueprint("badges", __name__, url_prefix="/api/badges")

@bpBadges.get("/")
def listBadges():
    with dbCursor() as db:
        db.execute("SELECT badgeId, code, name, description FROM badges")
        rows = db.fetchAll() or []
    return jsonify(rows)

# NEW ROUTE: Get unlocked badges for a user
@bpBadges.get("/user/<int:userId>")
def listUserBadges(userId):
    with dbCursor() as db:
        db.execute("""
            SELECT b.badgeId, b.code, b.name, b.description, ub.unlockedAt
            FROM badges b
            LEFT JOIN userBadges ub
                ON ub.badgeId = b.badgeId AND ub.userId = %s
            ORDER BY b.badgeId
        """, (userId,))
        rows = db.fetchAll() or []

    # Convert to locked/unlocked structure
    result = []
    for r in rows:
        result.append({
            "badgeId": r["badgeId"],
            "code": r["code"],
            "name": r["name"],
            "description": r["description"],
            "unlocked": r["unlockedAt"] is not None
        })

    return jsonify(result)
