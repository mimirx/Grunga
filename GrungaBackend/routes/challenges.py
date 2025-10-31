from flask import Blueprint, request, jsonify
from services.connection import execute

bpChallenges = Blueprint("challenges", __name__, url_prefix="/api/challenges")

@bpChallenges.post("")
def createChallenge():
    data = request.get_json(force=True)
    res = execute("""
        INSERT INTO challenges (senderUserId, receiverUserId, expiresAt)
        VALUES (%s, %s, %s)
    """, (data["senderUserId"], data["receiverUserId"], data.get("expiresAt")))
    return jsonify(res), 201
