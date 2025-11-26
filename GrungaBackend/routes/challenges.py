from flask import Blueprint, request, jsonify
from services.challenges_service import (
    create_challenge,
    get_challenges_for_user,
    accept_challenge,
    decline_challenge,
    complete_challenge,
)
from services.friendsService import getUserByUsername


challengesBlueprint = Blueprint("challenges", __name__, url_prefix="/api/challenges")


# -------------------------------------------------------------------
# Helper to get current user ID from header X-Demo-User
# -------------------------------------------------------------------
def getCurrentUserId():
    username = request.headers.get("X-Demo-User", None)
    if not username:
        return None

    user = getUserByUsername(username)
    if not user:
        return None

    return user["userId"]


# -------------------------------------------------------------------
# Send challenge
# POST /api/challenges/send
# Body: { toUserId, exerciseType, sets, reps }
# -------------------------------------------------------------------

@challengesBlueprint.post("/send")
def send_challenge_route():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"ok": False, "error": "User not found via header"}), 401

    data = request.get_json(force=True) or {}

    toUserId = data.get("toUserId")
    exerciseType = (data.get("exerciseType") or "").strip()
    sets = int(data.get("sets", 0))
    reps = int(data.get("reps", 0))

    if not toUserId:
        return jsonify({"ok": False, "error": "toUserId is required"}), 400
    if not exerciseType:
        return jsonify({"ok": False, "error": "exerciseType is required"}), 400

    result = create_challenge(userId, int(toUserId), exerciseType, sets, reps)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


# -------------------------------------------------------------------
# LIST challenges
# GET /api/challenges/incoming
# GET /api/challenges/active
# GET /api/challenges/completed
# -------------------------------------------------------------------

@challengesBlueprint.get("/incoming")
def list_incoming_route():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    rows = get_challenges_for_user(userId, "incoming")
    return jsonify(rows), 200


@challengesBlueprint.get("/active")
def list_active_route():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    rows = get_challenges_for_user(userId, "active")
    return jsonify(rows), 200


@challengesBlueprint.get("/completed")
def list_completed_route():
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"error": "User not found"}), 401

    rows = get_challenges_for_user(userId, "done")
    return jsonify(rows), 200


# -------------------------------------------------------------------
# ACCEPT challenge
# POST /api/challenges/<id>/accept
# -------------------------------------------------------------------

@challengesBlueprint.post("/<int:challengeId>/accept")
def accept_route(challengeId):
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"ok": False, "error": "User not found"}), 401

    result = accept_challenge(challengeId, userId)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


# -------------------------------------------------------------------
# DECLINE challenge
# POST /api/challenges/<id>/decline
# -------------------------------------------------------------------

@challengesBlueprint.post("/<int:challengeId>/decline")
def decline_route(challengeId):
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"ok": False, "error": "User not found"}), 401

    result = decline_challenge(challengeId, userId)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


# -------------------------------------------------------------------
# COMPLETE challenge
# POST /api/challenges/<id>/complete
# -------------------------------------------------------------------

@challengesBlueprint.post("/<int:challengeId>/complete")
def complete_route(challengeId):
    userId = getCurrentUserId()
    if not userId:
        return jsonify({"ok": False, "error": "User not found"}), 401

    result = complete_challenge(challengeId, userId)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status
