from flask import Blueprint, request, jsonify
from services.friendsService import (
    getUserByUsername,
    searchUsers,
    sendFriendRequest,
    respondToFriendRequest,
    getFriendsList,
    getPendingRequests,
    removeFriend,
)

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
