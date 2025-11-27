from flask import Blueprint, jsonify
from services.points_service import recomputeTotalsForUser

bpStreaks = Blueprint("streaks", __name__, url_prefix="/api/streaks")

@bpStreaks.get("/<int:userId>")
def getStreak(userId):
    totals = recomputeTotalsForUser(userId)
    return jsonify({
        "streak": totals["streak"],
        "daily": totals["daily"],
        "weekly": totals["weekly"]
    })
