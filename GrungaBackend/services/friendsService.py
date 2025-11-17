from services.connection import db_cursor

def getUserByUsername(username):
    with db_cursor() as db:
        db.execute("""
            SELECT userId, username, displayName
            FROM users
            WHERE username = %s
        """, (username,))
        return db.fetchOne()

def searchUsers(query, excludeUserId):
    like = f"%{query}%"
    with db_cursor() as db:
        db.execute("""
            SELECT userId, username, displayName
            FROM users
            WHERE (username LIKE %s OR displayName LIKE %s)
              AND userId <> %s
            LIMIT 20
        """, (like, like, excludeUserId))
        return db.fetchAll()

def getFriendStatus(userId, otherUserId):
    if userId == otherUserId:
        return "self"

    low = min(userId, otherUserId)
    high = max(userId, otherUserId)

    with db_cursor() as db:
        db.execute("""
            SELECT userId, friendId, status
            FROM friends
            WHERE userId = %s AND friendId = %s
        """, (low, high))
        row = db.fetchOne()

    if not row:
        return None

    if row["status"] == "blocked":
        return "blocked"

    if row["status"] == "accepted":
        return "friends"

    if row["status"] == "pending":
        if row["userId"] == userId:
            return "outgoing_pending"
        else:
            return "incoming_pending"

    return None

def sendFriendRequest(fromUserId, toUserId):
    if fromUserId == toUserId:
        return {"ok": False, "error": "You cannot add yourself as a friend."}

    low = min(fromUserId, toUserId)
    high = max(fromUserId, toUserId)

    status = getFriendStatus(fromUserId, toUserId)
    if status == "friends":
        return {"ok": False, "error": "You are already friends."}
    if status == "outgoing_pending":
        return {"ok": False, "error": "Friend request already sent."}
    if status == "incoming_pending":
        return {"ok": False, "error": "This user already sent you a request."}
    if status == "blocked":
        return {"ok": False, "error": "Friendship is blocked."}

    with db_cursor(commit=True) as db:
        db.execute("""
            INSERT INTO friends (userId, friendId, status)
            VALUES (%s, %s, 'pending')
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        """, (low, high))

    return {"ok": True}

def respondToFriendRequest(currentUserId, otherUserId, accept):
    if currentUserId == otherUserId:
        return {"ok": False, "error": "Invalid request."}

    low = min(currentUserId, otherUserId)
    high = max(currentUserId, otherUserId)

    with db_cursor() as db:
        db.execute("""
            SELECT id, userId, friendId, status
            FROM friends
            WHERE userId = %s AND friendId = %s
        """, (low, high))
        row = db.fetchOne()

    if not row or row["status"] != "pending":
        return {"ok": False, "error": "No pending friend request found."}

    # (the odd permission check from your original code is kept as-is)
    if not ((row["userId"] == low and currentUserId == high) or
            (row["userId"] == low and currentUserId == low and otherUserId == high)):
        pass

    newStatus = "accepted" if accept else "blocked"

    with db_cursor(commit=True) as db:
        db.execute("""
            UPDATE friends
            SET status = %s
            WHERE id = %s
        """, (newStatus, row["id"]))

    return {"ok": True, "status": newStatus}

def getFriendsList(userId):
    with db_cursor() as db:
        db.execute("""
            SELECT f.userId, f.friendId, f.status,
                   u1.userId AS userAId, u1.username AS userAUsername, u1.displayName AS userADisplayName,
                   u2.userId AS userBId, u2.username AS userBUsername, u2.displayName AS userBDisplayName
            FROM friends f
            JOIN users u1 ON f.userId = u1.userId
            JOIN users u2 ON f.friendId = u2.userId
            WHERE f.status = 'accepted'
              AND (f.userId = %s OR f.friendId = %s)
        """, (userId, userId))
        rows = db.fetchAll()

    friends = []
    for row in rows:
        if row["userAId"] == userId:
            otherId = row["userBId"]
            otherUsername = row["userBUsername"]
            otherDisplayName = row["userBDisplayName"]
        else:
            otherId = row["userAId"]
            otherUsername = row["userAUsername"]
            otherDisplayName = row["userADisplayName"]

        friends.append({
            "userId": otherId,
            "username": otherUsername,
            "displayName": otherDisplayName
        })

    return friends

def getPendingRequests(userId):
    with db_cursor() as db:
        db.execute("""
            SELECT f.id, f.userId, f.friendId, f.status,
                   u1.username AS fromUsername, u1.displayName AS fromDisplayName,
                   u2.username AS toUsername,   u2.displayName AS toDisplayName
            FROM friends f
            JOIN users u1 ON f.userId = u1.userId
            JOIN users u2 ON f.friendId = u2.userId
            WHERE f.status = 'pending'
              AND (f.userId = %s OR f.friendId = %s)
        """, (userId, userId))
        rows = db.fetchAll()

    incoming = []
    outgoing = []

    for row in rows:
        if row["userId"] == userId:
            outgoing.append({
                "otherUserId": row["friendId"],
                "username": row["toUsername"],
                "displayName": row["toDisplayName"]
            })
        else:
            incoming.append({
                "otherUserId": row["userId"],
                "username": row["fromUsername"],
                "displayName": row["fromDisplayName"]
            })

    return {"incoming": incoming, "outgoing": outgoing}
