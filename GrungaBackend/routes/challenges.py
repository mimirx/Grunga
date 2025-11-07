# at top (ensure these are present)
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import pytz
from services.connection import fetchOne, execute

bpChallenges = Blueprint("challenges", __name__, url_prefix="/api/challenges")

@bpChallenges.post("/")
def createChallenge():
    data = request.get_json(force=True)
    sender = int(data["senderUserId"])
    receiver = int(data["receiverUserId"])
    if sender == receiver:
        return jsonify({"error": "cannot challenge yourself"}), 400

    # ✅ Chicago-local “today” for duplicate prevention
    dup = fetchOne("""
        SELECT challengeId FROM challenges
        WHERE senderUserId=%s AND receiverUserId=%s
          AND status='PENDING'
          AND DATE(createdAt) = CURRENT_DATE()   -- CHICAGO, because connection sets time_zone
    """, (sender, receiver))
    if dup:
        return jsonify({"error": "challenge already sent today"}), 409

    # ✅ expiresAt = next Chicago midnight, stored/compared as CHICAGO (NOW() in DB is Chicago too)
    if data.get("expiresAt"):
        expiresAt = data["expiresAt"]
    else:
        tz = pytz.timezone("America/Chicago")
        now_ct = datetime.now(tz)
        next_midnight_ct = (now_ct + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        expiresAt = next_midnight_ct.strftime("%Y-%m-%d %H:%M:%S")  # no UTC conversion

    res = execute("""
        INSERT INTO challenges (senderUserId, receiverUserId, status, expiresAt)
        VALUES (%s, %s, 'PENDING', %s)
    """, (sender, receiver, expiresAt))
    return jsonify(res), 201
