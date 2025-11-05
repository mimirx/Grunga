from datetime import datetime, timedelta
import pytz
from services.connection import fetchOne, execute

@bpChallenges.post("/")
def createChallenge():
    data = request.get_json(force=True)
    sender = int(data["senderUserId"])
    receiver = int(data["receiverUserId"])
    if sender == receiver:
        return jsonify({"error": "cannot challenge yourself"}), 400

    # prevent duplicate pending challenge today
    dup = fetchOne("""
        SELECT challengeId FROM challenges
        WHERE senderUserId=%s AND receiverUserId=%s
          AND status='PENDING'
          AND DATE(createdAt) = UTC_DATE()
    """, (sender, receiver))
    if dup:
        return jsonify({"error": "challenge already sent today"}), 409

    # compute default expiresAt = next midnight Chicago, store as UTC
    if data.get("expiresAt"):
        expiresAt = data["expiresAt"]
    else:
        tz = pytz.timezone("America/Chicago")
        now_ct = datetime.now(tz)
        next_midnight_ct = (now_ct + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        expiresAt = next_midnight_ct.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

    res = execute("""
        INSERT INTO challenges (senderUserId, receiverUserId, status, expiresAt)
        VALUES (%s, %s, 'PENDING', %s)
    """, (sender, receiver, expiresAt))
    return jsonify(res), 201
