from flask import Blueprint, jsonify
from services.connection import fetchAll, fetchOne

bpUsers = Blueprint("users", __name__, url_prefix="/api")

@bpUsers.get("/health")
def health():
    return jsonify(ok=True)

@bpUsers.get("/users")                       # <- list users at /api/users
def listUsers():
    rows = fetchAll(
        "SELECT userId, username, displayName FROM users ORDER BY userId"
    )
    return jsonify(rows)

@bpUsers.get("/users/<username>")            # <- single user at /api/users/<username>
def getUserByUsername(username):
    row = fetchOne(
        "SELECT userId, username, displayName FROM users WHERE username=%s",
        (username,)
    )
    return (jsonify(row), 200) if row else (jsonify({}), 404)
