from flask import Blueprint, request, jsonify
from services.friendsService import (
    getUserByUsername,
    searchUsers,
    sendFriendRequest,
    respondToFriendRequest,
    getFriendsList,
    getPendingRequests,
    removeFriend,
    getFriendStatus,
)
from services.points_service import recomputeTotalsForUser, weeklyHistogramForUser
from services.connection import db_cursor

friendsBlueprint = Blueprint("friends", __name__)

def getCurrentUserId():
    username = request.headers.get("X-Demo-User", "demo1")
    user = getUserByUsername(username)
    if not user:
        return None
    return user["userId"]

@friendsBlueprint.route("/users/search")
def searchUsersRoute():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    users = searchUsers(query, userId)
    return jsonify(users)

@friendsBlueprint.route("/", methods=["GET"])
def listFriendsRoute():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    friends = getFriendsList(userId)
    pending = getPendingRequests(userId)

    return jsonify({
        "friends": friends,
        "incoming": pending["incoming"],
        "outgoing": pending["outgoing"]
    })

@friendsBlueprint.route("/requests", methods=["POST"])
def sendFriendRequestRoute():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    data = request.get_json() or {}
    friendId = data.get("friendId")

    if not friendId:
        return jsonify({"ok": False, "error": "friendId is required."}), 400

    result = sendFriendRequest(userId, int(friendId))
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@friendsBlueprint.route("/requests/respond", methods=["POST"])
def respondFriendRequestRoute():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    data = request.get_json() or {}
    otherUserId = data.get("otherUserId")
    action = data.get("action")

    if not otherUserId or action not in ("accept", "decline"):
        return jsonify({"ok": False, "error": "Invalid request."}), 400

    accept = (action == "accept")
    result = respondToFriendRequest(userId, int(otherUserId), accept)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@friendsBlueprint.route("/remove/<int:otherUserId>", methods=["DELETE"])
def removeFriendRoute(otherUserId):
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    result = removeFriend(userId, otherUserId)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

# NEW: friend profile stats for a specific friend
@friendsBlueprint.route("/profile/<int:friendId>", methods=["GET"])
def friendProfileRoute(friendId):
    """
    Returns points, streak, total workouts, and weekly histogram
    for the given friendId, as long as the current user is that
    user or they are friends.
    """
    currentUserId = getCurrentUserId()
    if not currentUserId:
        return jsonify({"error": "User not found"}), 401

    # Optional safety: only allow viewing your own stats or friends' stats
    status = getFriendStatus(currentUserId, friendId)
    if currentUserId != friendId and status != "friends":
        return jsonify({"error": "You can only view stats for friends."}), 403

    # Recompute totals for this friend (workouts + challenges, etc.)
    totals = recomputeTotalsForUser(friendId)

    # Count total workouts for this friend
    with db_cursor() as db:
        db.execute("SELECT COUNT(*) AS cnt FROM workouts WHERE userId=%s", (friendId,))
        row = db.fetchOne() or {}
    total_workouts = int(row.get("cnt", 0))

    # Weekly histogram (7 days)
    histogram = weeklyHistogramForUser(friendId)

    return jsonify({
        "points": {
            "total": totals["total"],
            "weekly": totals["weekly"],
            "daily": totals["daily"],
            "streak": totals["streak"],
        },
        "boss": totals["boss"],
        "totalWorkouts": total_workouts,
        "weeklyHistogram": histogram,
    })
