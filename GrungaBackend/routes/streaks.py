from flask import Blueprint, jsonify

bpStreaks = Blueprint("streaks", __name__, url_prefix="/api/streaks")

@bpStreaks.get("/ping")
def ping():
    return jsonify(ok=True)
