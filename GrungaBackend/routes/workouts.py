from flask import Blueprint, jsonify, request
from services.connection import db_cursor as dbCursor
from services.points_service import recomputeTotalsForUser, weeklyHistogramForUser

bpWorkouts = Blueprint("bpWorkouts", __name__)

@bpWorkouts.get("/users/<string:username>")
def getUserByUsername(username):
    with dbCursor() as db:
        db.execute("SELECT userId, username, displayName FROM users WHERE username=%s", (username,))
        row = db.fetchOne()
    if not row:
        return jsonify({"error": "user not found"}), 404
    return jsonify(row)

@bpWorkouts.get("/users/<int:userId>/workouts")
def listWorkouts(userId):
    with dbCursor() as db:
        db.execute("""
            SELECT workoutId, workoutType, sets, reps, workoutDate
            FROM workouts
            WHERE userId=%s
            ORDER BY workoutDate DESC, workoutId DESC
        """, (userId,))
        rows = db.fetchAll() or []
    return jsonify(rows)

@bpWorkouts.post("/users/<int:userId>/workouts")
def createWorkout(userId):
    data = request.get_json(force=True) or {}
    workoutType = data.get("workoutType")
    sets = int(data.get("sets", 0))
    reps = int(data.get("reps", 0))
    workoutDate = data.get("workoutDate")
    if not workoutType or sets <= 0 or reps <= 0 or not workoutDate:
        return jsonify({"error": "invalid input"}), 400
    with dbCursor(commit=True) as db:
        db.execute("""
            INSERT INTO workouts (userId, workoutType, sets, reps, workoutDate)
            VALUES (%s,%s,%s,%s,%s)
        """, (userId, workoutType, sets, reps, workoutDate))
        wid = db.lastRowId()
    totals = recomputeTotalsForUser(userId)
    return jsonify({"ok": True, "workoutId": wid, "totals": totals}), 201

@bpWorkouts.patch("/users/<int:userId>/workouts/<int:workoutId>")
def updateWorkout(userId, workoutId):
    data = request.get_json(force=True) or {}
    workoutType = data.get("workoutType")
    sets = data.get("sets")
    reps = data.get("reps")
    workoutDate = data.get("workoutDate")
    fields = []
    vals = []
    if workoutType is not None:
        fields.append("workoutType=%s"); vals.append(workoutType)
    if sets is not None:
        sets = int(sets)
        if sets <= 0: return jsonify({"error":"invalid sets"}), 400
        fields.append("sets=%s"); vals.append(sets)
    if reps is not None:
        reps = int(reps)
        if reps <= 0: return jsonify({"error":"invalid reps"}), 400
        fields.append("reps=%s"); vals.append(reps)
    if workoutDate is not None:
        fields.append("workoutDate=%s"); vals.append(workoutDate)
    if not fields:
        return jsonify({"error":"no changes"}), 400
    vals.extend([userId, workoutId])
    with dbCursor(commit=True) as db:
        db.execute(f"UPDATE workouts SET {', '.join(fields)} WHERE userId=%s AND workoutId=%s", vals)
    totals = recomputeTotalsForUser(userId)
    return jsonify({"ok": True, "totals": totals})

@bpWorkouts.delete("/users/<int:userId>/workouts/<int:workoutId>")
def deleteWorkout(userId, workoutId):
    with dbCursor(commit=True) as db:
        db.execute("DELETE FROM workouts WHERE userId=%s AND workoutId=%s", (userId, workoutId))
    totals = recomputeTotalsForUser(userId)
    return jsonify({"ok": True, "totals": totals})

@bpWorkouts.get("/users/<int:userId>/points")
def getPoints(userId):
    totals = recomputeTotalsForUser(userId)
    hist = weeklyHistogramForUser(userId)
    return jsonify({
        "totalPoints": totals["total"],
        "weeklyPoints": totals["weekly"],
        "dailyPoints": totals["daily"],
        "streak": totals.get("streak", 0),
        "hist": hist
    })
