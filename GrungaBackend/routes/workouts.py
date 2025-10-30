from flask import Blueprint, request, jsonify
from services.connection import fetchAll, execute, fetchOne
from services.points_service import calcWorkoutPoints, writePoints, getTotals
from datetime import date

bpWorkouts = Blueprint("workouts", __name__, url_prefix="/api")

@bpWorkouts.get("/users/<int:userId>/workouts")
def listWorkouts(userId):
    rows = fetchAll(
        "SELECT workoutId, userId, workoutDate, workoutType, sets, reps, createdAt FROM workouts WHERE userId=%s ORDER BY workoutDate DESC, workoutId DESC",
        (userId,)
    )
    return jsonify(rows)

@bpWorkouts.post("/users/<int:userId>/workouts")
def createWorkout(userId):
    p = request.get_json(force=True)
    wDate = p.get("workoutDate")
    wType = p.get("workoutType")
    sets = int(p.get("sets"))
    reps = int(p.get("reps"))
    r = execute(
        "INSERT INTO workouts (userId, workoutDate, workoutType, sets, reps) VALUES (%s,%s,%s,%s,%s)",
        (userId, wDate, wType, sets, reps)
    )
    pts = calcWorkoutPoints(sets, reps)
    writePoints(userId, pts, "workout", r["lastRowId"])
    return jsonify(dict(workoutId=r["lastRowId"])), 201

@bpWorkouts.patch("/workouts/<int:workoutId>")
def updateWorkout(workoutId):
    p = request.get_json(force=True)
    sets = int(p.get("sets"))
    reps = int(p.get("reps"))
    execute("UPDATE workouts SET sets=%s, reps=%s WHERE workoutId=%s", (sets, reps, workoutId))
    row = fetchOne("SELECT userId FROM workouts WHERE workoutId=%s", (workoutId,))
    if row:
        pts = calcWorkoutPoints(sets, reps)
        writePoints(row["userId"], pts, "workoutEdit", workoutId)
    return jsonify(dict(ok=True))

@bpWorkouts.delete("/workouts/<int:workoutId>")
def deleteWorkout(workoutId):
    row = fetchOne("SELECT userId, sets, reps FROM workouts WHERE workoutId=%s", (workoutId,))
    execute("DELETE FROM workouts WHERE workoutId=%s", (workoutId,))
    if row:
        pts = calcWorkoutPoints(row["sets"], row["reps"])
        writePoints(row["userId"], 0, "workoutDelete", workoutId)
    return jsonify(dict(ok=True))

@bpWorkouts.get("/users/<int:userId>/points")
def getUserPoints(userId):
    return jsonify(getTotals(userId))
