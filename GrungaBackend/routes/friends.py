# GrungaBackend/routes/friends.py
from flask import Blueprint, jsonify, request
from services.connection import fetchAll, execute

bpFriends = Blueprint("friends", __name__, url_prefix="/api/friends")

@bpFriends.get("/<int:userId>")
def listFriends(userId):
    rows = fetchAll("""
        SELECT u.userId, u.username, u.displayName
        FROM friends f
        JOIN users u ON u.userId = IF(f.userId=%s, f.friendUserId, f.userId)
        WHERE f.userId = %s OR f.friendUserId = %s
        ORDER BY u.displayName
    """, (userId, userId, userId))
    return jsonify(rows)

@bpFriends.post("")
def addFriend():
    data = request.get_json(force=True)
    userId = int(data["userId"])
    friendId = int(data["friendUserId"])
    res = execute("""
        INSERT INTO friends (userId, friendUserId) VALUES (%s, %s)
    """, (userId, friendId))
    return jsonify(res), 201
