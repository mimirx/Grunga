from flask import Blueprint, request, jsonify
from services.challenges_service import (
    create_challenge,
    list_challenges_for_user,
    accept_challenge,
    decline_challenge,
    complete_challenge,
)

bpChallenges = Blueprint("challenges", __name__)


@bpChallenges.route("/users/<int:user_id>/challenges", methods=["POST"])
def api_create_challenge(user_id):
    data = request.get_json(silent=True) or {}

    to_user_id = data.get("toUserId")
    kind = data.get("kind", "WORKOUT")
    target = data.get("target")

    if not to_user_id or target is None:
        return jsonify({"error": "toUserId and target are required"}), 400

    due_at = data.get("dueAt")

    challenge = create_challenge(
        from_user_id=user_id,
        to_user_id=to_user_id,
        kind=kind,
        target=target,
        due_at=due_at,
    )

    return jsonify(challenge), 201


@bpChallenges.route("/users/<int:user_id>/challenges", methods=["GET"])
def api_list_challenges(user_id):
    box = request.args.get("box", "incoming")
    rows = list_challenges_for_user(user_id, box=box)
    return jsonify(rows)


@bpChallenges.route("/challenges/<int:challenge_id>/accept", methods=["POST"])
def api_accept_challenge(challenge_id):
    data = request.get_json(silent=True) or {}
    acting_user_id = data.get("userId")
    if not acting_user_id:
        return jsonify({"error": "userId required"}), 400

    row, err = accept_challenge(challenge_id, acting_user_id)
    if err == "not-found":
        return jsonify({"error": "challenge not found"}), 404
    if err == "forbidden":
        return jsonify({"error": "only the recipient can accept"}), 403
    if err == "invalid-state":
        return jsonify({"error": "challenge cannot be accepted"}), 400

    return jsonify(row)


@bpChallenges.route("/challenges/<int:challenge_id>/decline", methods=["POST"])
def api_decline_challenge(challenge_id):
    data = request.get_json(silent=True) or {}
    acting_user_id = data.get("userId")
    if not acting_user_id:
        return jsonify({"error": "userId required"}), 400

    row, err = decline_challenge(challenge_id, acting_user_id)
    if err == "not-found":
        return jsonify({"error": "challenge not found"}), 404
    if err == "forbidden":
        return jsonify({"error": "only the recipient can decline"}), 403
    if err == "invalid-state":
        return jsonify({"error": "challenge cannot be declined"}), 400

    return jsonify(row)


@bpChallenges.route("/challenges/<int:challenge_id>/complete", methods=["POST"])
def api_complete_challenge(challenge_id):
    data = request.get_json(silent=True) or {}
    acting_user_id = data.get("userId")
    if not acting_user_id:
        return jsonify({"error": "userId required"}), 400

    row, err = complete_challenge(challenge_id, acting_user_id)
    if err == "not-found":
        return jsonify({"error": "challenge not found"}), 404
    if err == "invalid-state":
        return jsonify({"error": "challenge cannot be completed"}), 400

    return jsonify(row)
