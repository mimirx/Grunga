from services.connection import db_cursor as dbCursor

# -----------------------------------------------------------
# Get badgeId from code
# -----------------------------------------------------------
def getBadgeId(code: str):
    with dbCursor() as db:
        db.execute("SELECT badgeId FROM badges WHERE code=%s", (code,))
        row = db.fetchOne()
        return row["badgeId"] if row else None


# -----------------------------------------------------------
# Check if user already unlocked badge
# -----------------------------------------------------------
def userHasBadge(userId: int, badgeId: int) -> bool:
    with dbCursor() as db:
        db.execute("""
            SELECT 1 FROM userBadges
            WHERE userId=%s AND badgeId=%s
        """, (userId, badgeId))
        return db.fetchOne() is not None


# -----------------------------------------------------------
# Unlock badge — safe, duplicate-proof
# -----------------------------------------------------------
def unlockBadge(userId: int, code: str):
    badgeId = getBadgeId(code)
    if not badgeId:
        print(f"[BADGE ERROR] Badge code '{code}' does not exist")
        return False

    if userHasBadge(userId, badgeId):
        return False  # already unlocked, do nothing

    with dbCursor(commit=True) as db:
        db.execute("""
            INSERT INTO userBadges (userId, badgeId)
            VALUES (%s, %s)
        """, (userId, badgeId))

    print(f"[BADGE] User {userId} unlocked {code}")
    return True
