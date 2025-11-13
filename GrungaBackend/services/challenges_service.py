from datetime import datetime
from services.connection import db_cursor


def row_to_dict(row):
    if not row:
        return None
    return {
        "challengeId": row["challengeId"],
        "createdAt": row["createdAt"].isoformat() if isinstance(row["createdAt"], datetime) else row["createdAt"],
        "fromUserId": row["fromUserId"],
        "toUserId": row["toUserId"],
        "kind": row["kind"],
        "target": row["target"],
        "progressFrom": row["progressFrom"],
        "progressTo": row["progressTo"],
        "status": row["status"],
        "dueAt": row["dueAt"].isoformat() if row["dueAt"] else None,
    }


def create_challenge(from_user_id, to_user_id, kind, target, due_at=None):
    sql = """
        INSERT INTO challenges (fromUserId, toUserId, kind, target, dueAt)
        VALUES (%s, %s, %s, %s, %s)
    """
    with db_cursor(commit=True) as cur:
        cur.execute(sql, (from_user_id, to_user_id, kind, target, due_at))
        challenge_id = cur.lastrowid

        cur.execute("SELECT * FROM challenges WHERE challengeId = %s", (challenge_id,))
        row = cur.fetchone()

    return row_to_dict(row)


def list_challenges_for_user(user_id, box="incoming"):
    if box == "incoming":
        where = "toUserId = %s AND status IN ('PENDING','ACTIVE')"
        params = (user_id,)
    elif box == "active":
        where = "(fromUserId = %s OR toUserId = %s) AND status = 'ACTIVE'"
        params = (user_id, user_id)
    elif box == "done":
        where = "(fromUserId = %s OR toUserId = %s) AND status = 'DONE'"
        params = (user_id, user_id)
    else:
        where = "(fromUserId = %s OR toUserId = %s)"
        params = (user_id, user_id)

    sql = f"""
        SELECT * FROM challenges
        WHERE {where}
        ORDER BY createdAt DESC
    """

    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [row_to_dict(r) for r in rows]


def _load_challenge(challenge_id):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM challenges WHERE challengeId = %s", (challenge_id,))
        row = cur.fetchone()
    return row


def set_status(challenge_id, status):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE challenges SET status = %s WHERE challengeId = %s",
            (status, challenge_id),
        )
        cur.execute("SELECT * FROM challenges WHERE challengeId = %s", (challenge_id,))
        row = cur.fetchone()
    return row_to_dict(row)


def accept_challenge(challenge_id, acting_user_id):
    row = _load_challenge(challenge_id)
    if not row:
        return None, "not-found"
    if row["toUserId"] != acting_user_id:
        return None, "forbidden"
    if row["status"] != "PENDING":
        return None, "invalid-state"
    return set_status(challenge_id, "ACTIVE"), None


def decline_challenge(challenge_id, acting_user_id):
    row = _load_challenge(challenge_id)
    if not row:
        return None, "not-found"
    if row["toUserId"] != acting_user_id:
        return None, "forbidden"
    if row["status"] != "PENDING":
        return None, "invalid-state"
    return set_status(challenge_id, "DECLINED"), None


def complete_challenge(challenge_id, acting_user_id):
    row = _load_challenge(challenge_id)
    if not row:
        return None, "not-found"
    if row["status"] not in ("ACTIVE", "PENDING"):
        return None, "invalid-state"
    # For now we allow either side to mark it done.
    return set_status(challenge_id, "DONE"), None
