from flask import Blueprint, jsonify, request
from services.connection import fetchAll, fetchOne, execute
from mysql.connector.errors import ProgrammingError

bpUsers = Blueprint("users", __name__, url_prefix="/api")


def _err(message, status=400):
    return jsonify(dict(error=message)), status


# --- helpers ---------------------------------------------------------------

def _table_has_column(table: str, column: str) -> bool:
    """
    Return True if `table`.`column` exists in the current DB.
    This lets us run on older dev schemas without crashing.
    """
    row = fetchOne(
        """
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        LIMIT 1
        """,
        (table, column),
    )
    return bool(row)


def _users_select_fields():
    # Always safe columns:
    fields = ["userId", "username", "displayName"]
    # Optional (only include if present):
    if _table_has_column("users", "email"):
        fields.append("email")
    if _table_has_column("users", "createdAt"):
        fields.append("createdAt")
    return ", ".join(fields)


def _get_totals_from_pointsTotals(userId: int):
    # Try pointsTotals first (fast path)
    try:
        row = fetchOne(
            "SELECT dailyPoints, weeklyPoints, totalPoints FROM pointsTotals WHERE userId=%s",
            (userId,),
        )
        return row if row else None
    except ProgrammingError:
        # Table or columns missing -> fall back
        return None


def _get_totals_fallback_from_ledger(userId: int):
    # Chicago boundaries are already handled by the session time_zone.
    # Compute totals directly from pointsLedger.
    row = fetchOne(
        """
        SELECT
          COALESCE(SUM(points), 0)                                             AS totalPoints,
          COALESCE(SUM(CASE WHEN DATE(occurredAt) = CURRENT_DATE() THEN points END), 0) AS dailyPoints,
          COALESCE(SUM(
             CASE WHEN YEARWEEK(occurredAt, 1) = YEARWEEK(CURRENT_DATE(), 1)
             THEN points END
          ), 0) AS weeklyPoints
        FROM pointsLedger
        WHERE userId = %s
        """,
        (userId,)
    ) or {"dailyPoints": 0, "weeklyPoints": 0, "totalPoints": 0}

    # Ensure a row in pointsTotals if the table exists
    try:
        execute(
            """
            INSERT INTO pointsTotals (userId, dailyPoints, weeklyPoints, totalPoints)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              dailyPoints = VALUES(dailyPoints),
              weeklyPoints = VALUES(weeklyPoints),
              totalPoints = VALUES(totalPoints),
              updatedAt = NOW()
            """,
            (userId, row["dailyPoints"], row["weeklyPoints"], row["totalPoints"])
        )
    except ProgrammingError:
        # pointsTotals table not present on this dev DB; that's fine.
        pass

    return dict(
        dailyPoints=row["dailyPoints"],
        weeklyPoints=row["weeklyPoints"],
        totalPoints=row["totalPoints"],
    )


# --- routes ----------------------------------------------------------------

@bpUsers.get("/health")
def health():
    return jsonify(ok=True)


@bpUsers.get("/users")
def listOrSearchUsers():
    """
    GET /api/users
    Optional: ?q=substr  -> case-insensitive search on username/displayName
    """
    fields = _users_select_fields()
    q = (request.args.get("q") or "").strip()
    if q:
        like = f"%{q}%"
        rows = fetchAll(
            f"SELECT {fields} FROM users WHERE username LIKE %s OR displayName LIKE %s ORDER BY userId",
            (like, like),
        )
        return jsonify(rows)

    rows = fetchAll(f"SELECT {fields} FROM users ORDER BY userId")
    return jsonify(rows)


@bpUsers.get("/users/<string:username>")
def getUserByUsername(username: str):
    fields = _users_select_fields()
    row = fetchOne(
        f"SELECT {fields} FROM users WHERE username=%s",
        (username,),
    )
    return (jsonify(row), 200) if row else _err("User not found", 404)


@bpUsers.get("/users/<int:userId>")
def getUserById(userId: int):
    fields = _users_select_fields()
    row = fetchOne(
        f"SELECT {fields} FROM users WHERE userId=%s",
        (userId,),
    )
    return (jsonify(row), 200) if row else _err("User not found", 404)


@bpUsers.post("/users")
def createUser():
    """
    POST /api/users
    Body: { "username": "...", "displayName": "...", "email": "..." }  # email optional, ignored if column missing
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

    # Build INSERT depending on which columns exist
    if _table_has_column("users", "email"):
        res = execute(
            "INSERT INTO users (username, displayName, email) VALUES (%s,%s,%s)",
            (username, displayName, email),
        )
    else:
        res = execute(
            "INSERT INTO users (username, displayName) VALUES (%s,%s)",
            (username, displayName),
        )
    newId = res["lastRowId"]

    # ensure a totals row if table exists
    try:
        execute("INSERT IGNORE INTO pointsTotals (userId) VALUES (%s)", (newId,))
    except ProgrammingError:
        pass

    # Return safe fields only
    fields = _users_select_fields()
    row = fetchOne(f"SELECT {fields} FROM users WHERE userId=%s", (newId,))
    return jsonify(row), 201


@bpUsers.patch("/users/<int:userId>")
def updateUser(userId: int):
    """
    PATCH /api/users/<userId>
    Body can include { "displayName": "...", "email": "..." } (email ignored if column missing)
    """
    data = request.get_json(force=True) or {}
    displayName = data.get("displayName", None)
    email = data.get("email", None)

    sets = []
    params = []
    if displayName is not None:
        sets.append("displayName=%s")
        params.append(displayName.strip())

    if email is not None and _table_has_column("users", "email"):
        sets.append("email=%s")
        params.append((email or "").strip() or None)

    if not sets:
        return _err("Provide fields to update")

    params.append(userId)
    execute(f"UPDATE users SET {', '.join(sets)} WHERE userId=%s", tuple(params))

    fields = _users_select_fields()
    row = fetchOne(f"SELECT {fields} FROM users WHERE userId=%s", (userId,))
    return (jsonify(row), 200) if row else _err("User not found", 404)


@bpUsers.get("/users/<int:userId>/points")
def getPoints(userId: int):
    """
    GET /api/users/<userId>/points
    Returns {dailyPoints, weeklyPoints, totalPoints, streak}.
    Falls back to computing from pointsLedger if pointsTotals is missing/empty.
    """
    # 1) Get daily/weekly/total points the same way as before
    row = _get_totals_from_pointsTotals(userId)
    if not row:
        row = _get_totals_fallback_from_ledger(userId)

    # Ensure we have a dict with defaults
    row = row or {"dailyPoints": 0, "weeklyPoints": 0, "totalPoints": 0}

    # 2) Get streak from pointsTotals (default 0 if anything is missing)
    streak = 0
    try:
        # Only try if the column exists (keeps old dev DBs safe)
        if _table_has_column("pointsTotals", "streak"):
            srow = fetchOne(
                "SELECT streak FROM pointsTotals WHERE userId=%s",
                (userId,),
            )
            if srow and srow.get("streak") is not None:
                streak = int(srow["streak"])
    except ProgrammingError:
        # If the table/column is missing on some DB, just leave streak = 0
        pass

    # 3) Return combined result INCLUDING streak
    return jsonify({
        "dailyPoints": row.get("dailyPoints", 0),
        "weeklyPoints": row.get("weeklyPoints", 0),
        "totalPoints": row.get("totalPoints", 0),
        "streak": streak,
    })



@bpUsers.get("/users/<int:userId>/totals")
def getUserTotals(userId: int):
    """
    GET /api/users/<userId>/totals
    Returns {daily, weekly, total}.
    """
    pts = _get_totals_from_pointsTotals(userId)
    if not pts:
        pts = _get_totals_fallback_from_ledger(userId)

    return jsonify({
        "userId": userId,
        "daily": pts.get("dailyPoints", 0),
        "weekly": pts.get("weeklyPoints", 0),
        "total": pts.get("totalPoints", 0),
    })


@bpUsers.get("/users/<int:userId>/friends")
def listFriends(userId: int):
    """
    GET /api/users/<userId>/friends
    Returns all friend profiles for a given user.
    Only selects columns that definitely exist.
    """
    # Only select safe columns from users table
    rows = fetchAll(
        """
        SELECT u.userId, u.username, u.displayName
        FROM friends f
        JOIN users u
          ON (u.userId = CASE WHEN f.userId = %s THEN f.friendUserId ELSE f.userId END)
        WHERE f.userId = %s OR f.friendUserId = %s
        ORDER BY u.userId
        """,
        (userId, userId, userId),
    )
    return jsonify(rows)
