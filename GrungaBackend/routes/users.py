from flask import Blueprint, jsonify, request
from services.connection import fetchAll, fetchOne, execute

bpUsers = Blueprint("users", __name__, url_prefix="/api")


def _err(message, status=400):
    return jsonify(dict(error=message)), status


@bpUsers.get("/health")
def health():
    return jsonify(ok=True)


@bpUsers.get("/users")
def listOrSearchUsers():
    """
    GET /api/users
    Optional: ?q=substr  -> case-insensitive search on username/displayName
    """
    q = (request.args.get("q") or "").strip()
    if q:
        like = f"%{q}%"
        rows = fetchAll(
            "SELECT userId, username, displayName, email "
            "FROM users "
            "WHERE username LIKE %s OR displayName LIKE %s "
            "ORDER BY userId",
            (like, like),
        )
        return jsonify(rows)

    rows = fetchAll(
        "SELECT userId, username, displayName, email "
        "FROM users ORDER BY userId"
    )
    return jsonify(rows)


@bpUsers.get("/users/<string:username>")
def getUserByUsername(username: str):
    """
    GET /api/users/<username>
    """
    row = fetchOne(
        "SELECT userId, username, displayName, email, createdAt "
        "FROM users WHERE username=%s",
        (username,),
    )
    return (jsonify(row), 200) if row else _err("User not found", 404)


@bpUsers.get("/users/<int:userId>")
def getUserById(userId: int):
    """
    GET /api/users/<int:userId>
    """
    row = fetchOne(
        "SELECT userId, username, displayName, email, createdAt "
        "FROM users WHERE userId=%s",
        (userId,),
    )
    return (jsonify(row), 200) if row else _err("User not found", 404)


@bpUsers.post("/users")
def createUser():
    """
    POST /api/users
    Body: { "username": "...", "displayName": "...", "email": "..." }
    """
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip()
    displayName = (data.get("displayName") or "User").strip()
    email = (data.get("email") or "").strip() or None

    if not username:
        return _err("username is required")

    exists = fetchOne("SELECT userId FROM users WHERE username=%s", (username,))
    if exists:
        return _err("username already exists", 409)

    res = execute(
        "INSERT INTO users (username, displayName, email) VALUES (%s,%s,%s)",
        (username, displayName, email),
    )
    newId = res["lastRowId"]

    # ensure a totals row exists
    execute("INSERT IGNORE INTO pointsTotals (userId) VALUES (%s)", (newId,))

    row = fetchOne(
        "SELECT userId, username, displayName, email, createdAt "
        "FROM users WHERE userId=%s",
        (newId,),
    )
    return jsonify(row), 201


@bpUsers.patch("/users/<int:userId>")
def updateUser(userId: int):
    """
    PATCH /api/users/<userId>
    Body can include { "displayName": "...", "email": "..." }
    """
    data = request.get_json(force=True) or {}
    displayName = data.get("displayName", None)
    email = data.get("email", None)

    if displayName is None and email is None:
        return _err("Provide displayName and/or email to update")

    sets = []
    params = []
    if displayName is not None:
        sets.append("displayName=%s")
        params.append(displayName.strip())
    if email is not None:
        sets.append("email=%s")
        params.append((email or "").strip() or None)
    params.append(userId)

    execute(f"UPDATE users SET {', '.join(sets)} WHERE userId=%s", tuple(params))

    row = fetchOne(
        "SELECT userId, username, displayName, email, createdAt "
        "FROM users WHERE userId=%s",
        (userId,),
    )
    return (jsonify(row), 200) if row else _err("User not found", 404)


@bpUsers.get("/users/<int:userId>/points")
def getPoints(userId: int):
    """
    GET /api/users/<userId>/points
    Keeps your original shape. Falls back to zeros if row missing.
    """
    row = fetchOne(
        "SELECT dailyPoints, weeklyPoints, totalPoints FROM pointsTotals WHERE userId=%s",
        (userId,),
    )
    if not row:
        # ensure a row exists so frontend doesn't break later
        execute("INSERT IGNORE INTO pointsTotals (userId) VALUES (%s)", (userId,))
        row = dict(dailyPoints=0, weeklyPoints=0, totalPoints=0)
    return jsonify(row or {"dailyPoints": 0, "weeklyPoints": 0, "totalPoints": 0})



@bpUsers.get("/users/<int:userId>/totals")
def getUserTotals(userId: int):
    """
    GET /api/users/<userId>/totals
    Same values but with keys {daily, weekly, total} (nice for dashboards).
    """
    row = fetchOne(
        "SELECT userId, dailyPoints AS daily, weeklyPoints AS weekly, "
        "totalPoints AS total, updatedAt "
        "FROM pointsTotals WHERE userId=%s",
        (userId,),
    )
    if not row:
        execute("INSERT IGNORE INTO pointsTotals (userId) VALUES (%s)", (userId,))
        row = fetchOne(
            "SELECT userId, dailyPoints AS daily, weeklyPoints AS weekly, "
            "totalPoints AS total, updatedAt "
            "FROM pointsTotals WHERE userId=%s",
            (userId,),
        )
    return jsonify(row)


@bpUsers.get("/users/<int:userId>/friends")
def listFriends(userId: int):
    """
    GET /api/users/<userId>/friends
    Returns all friend user profiles for a given user.
    """
    rows = fetchAll(
        "SELECT u.userId, u.username, u.displayName, u.email "
        "FROM friends f "
        "JOIN users u "
        "  ON (u.userId = CASE WHEN f.userId = %s THEN f.friendUserId ELSE f.userId END) "
        "WHERE f.userId = %s OR f.friendUserId = %s "
        "ORDER BY u.userId",
        (userId, userId, userId),
    )
    return jsonify(rows)
