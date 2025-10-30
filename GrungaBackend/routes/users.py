from flask import Blueprint, jsonify
from services.connection import fetchOne

bpUsers = Blueprint("users", __name__, url_prefix="/api")

@bpUsers.get("/health")
def health():
    return jsonify(ok=True)

@bpUsers.get("/users/<string:username>")
def getUserByUsername(username):
    u = fetchOne("SELECT userId, username, displayName FROM users WHERE username=%s", (username,))
    if not u:
        return jsonify(error="not found"), 404
    return jsonify(u)
