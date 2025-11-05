from flask import Blueprint, request, jsonify
from datetime import date

from services.connection import fetchAll, execute, fetchOne
from services.points_service import calcWorkoutPoints, writePoints, getTotals

bpWorkouts = Blueprint("workouts", __name__, url_prefix="/api")

@bpWorkouts.get("/users/<int:userId>/workouts")
def listWorkouts(userId):
    rows = fetchAll(
        """
        SELECT workoutId, userId, workoutDate, workoutType, sets, reps, createdAt
        FROM workouts
        WHERE userId = %s
        ORDER BY workoutDate DESC, workoutId DESC
        """,
        (userId,)
    )
    return jsonify(rows)

@bpWorkouts.post("/users/<int:userId>/workouts")
def createWorkout(userId):
    p = request.get_json(force=True)
    wDate = p.get("workoutDate") or date.today().isoformat()
    wType = p.get("workoutType")
    sets = int(p.get("sets"))
    reps = int(p.get("reps"))

    r = execute(
        """
        INSERT INTO workouts (userId, workoutDate, workoutType, sets, reps)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (userId, wDate, wType, sets, reps)
    )

    # ✅ pass the type, sets, reps (matches points_service)
    pts = calcWorkoutPoints(wType, sets, reps)
    writePoints(userId, pts, "workout", r["lastRowId"])

    return jsonify({"workoutId": r["lastRowId"], "addedPoints": pts}), 201

@bpWorkouts.patch("/workouts/<int:workoutId>")
def updateWorkout(workoutId):
    p = request.get_json(force=True)
    newSets = int(p.get("sets"))
    newReps = int(p.get("reps"))

    # fetch old so we can compute delta
    row = fetchOne("""
        SELECT userId, workoutType, sets AS oldSets, reps AS oldReps
        FROM workouts WHERE workoutId = %s
    """, (workoutId,))
    if not row:
        return jsonify({"error": "Workout not found"}), 404

    execute("UPDATE workouts SET sets=%s, reps=%s WHERE workoutId=%s",
            (newSets, newReps, workoutId))

    oldPts = calcWorkoutPoints(row["workoutType"], row["oldSets"], row["oldReps"])
    newPts = calcWorkoutPoints(row["workoutType"], newSets, newReps)
    delta = newPts - oldPts

    if delta != 0:
        writePoints(row["userId"], delta, "workoutEdit", workoutId)

    return jsonify({"ok": True, "pointsDelta": delta})

@bpWorkouts.delete("/workouts/<int:workoutId>")
def deleteWorkout(workoutId):
    row = fetchOne("""
        SELECT userId, workoutType, sets, reps
        FROM workouts WHERE workoutId=%s
    """, (workoutId,))

    execute("DELETE FROM workouts WHERE workoutId=%s", (workoutId,))

    if row:
        pts = -calcWorkoutPoints(row["workoutType"], row["sets"], row["reps"])
        writePoints(row["userId"], pts, "workoutDelete", workoutId)

    return jsonify({"ok": True})

@bpWorkouts.get("/users/<int:userId>/points")
def getUserPoints(userId):
    return jsonify(getTotals(userId))
