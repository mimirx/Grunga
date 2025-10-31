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
    sets = int(p.get("sets"))
    reps = int(p.get("reps"))

    # get the workout so we also know its type and user
    row = fetchOne("SELECT userId, workoutType FROM workouts WHERE workoutId = %s", (workoutId,))
    if not row:
        return jsonify({"error": "Workout not found"}), 404

    execute(
        "UPDATE workouts SET sets = %s, reps = %s WHERE workoutId = %s",
        (sets, reps, workoutId)
    )

    # record an edit event (you can choose to add, subtract, or just log)
    pts = calcWorkoutPoints(row["workoutType"], sets, reps)
    writePoints(row["userId"], pts, "workoutEdit", workoutId)

    return jsonify({"ok": True, "newPointsFromEdit": pts})

@bpWorkouts.delete("/workouts/<int:workoutId>")
def deleteWorkout(workoutId):
    # read before deleting so we can log something meaningful
    row = fetchOne("SELECT userId, workoutType, sets, reps FROM workouts WHERE workoutId = %s", (workoutId,))
    execute("DELETE FROM workouts WHERE workoutId = %s", (workoutId,))

    if row:
        # Option A (simple log): write 0 points with reason
        writePoints(row["userId"], 0, "workoutDelete", workoutId)

        # Option B (undo points): uncomment next two lines instead of Option A
        # pts = -calcWorkoutPoints(row["workoutType"], row["sets"], row["reps"])
        # writePoints(row["userId"], pts, "workoutDelete", workoutId)

    return jsonify({"ok": True})

@bpWorkouts.get("/users/<int:userId>/points")
def getUserPoints(userId):
    return jsonify(getTotals(userId))
