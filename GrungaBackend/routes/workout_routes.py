from flask import Blueprint, request, jsonify
from database.connection import db_cursor

workout_bp = Blueprint("workout_bp", __name__)

@workout_bp.post("/api/workouts")
def add_workout():
    data = request.get_json(force=True)
    required = ["user_id", "workout_type", "sets", "reps", "points"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    with db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO workouts (user_id, workout_type, sets, reps, points) "
            "VALUES (%s, %s, %s, %s, %s)",
            (data["user_id"], data["workout_type"], data["sets"], data["reps"], data["points"])
        )

    recalc_points(data["user_id"])
    return jsonify({"message": "Workout added"})


def recalc_points(user_id: int):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT COALESCE(SUM(points),0) FROM workouts WHERE user_id=%s",
            (user_id,)
        )
        total = cur.fetchone()["COALESCE(SUM(points),0)"]

        cur.execute(
            "SELECT COALESCE(SUM(points),0) FROM workouts "
            "WHERE user_id=%s AND DATE(date_logged)=CURRENT_DATE()",
            (user_id,)
        )
        daily = cur.fetchone()["COALESCE(SUM(points),0)"]

        cur.execute(
            "SELECT COALESCE(SUM(points),0) FROM workouts "
            "WHERE user_id=%s AND YEARWEEK(date_logged, 3)=YEARWEEK(CURDATE(), 3)",
            (user_id,)
        )
        weekly = cur.fetchone()["COALESCE(SUM(points),0)"]

        cur.execute(
            "INSERT INTO points_totals (user_id,daily_points,weekly_points,total_points,last_update) "
            "VALUES (%s,%s,%s,%s,NOW()) "
            "ON DUPLICATE KEY UPDATE "
            "daily_points=VALUES(daily_points), "
            "weekly_points=VALUES(weekly_points), "
            "total_points=VALUES(total_points), "
            "last_update=VALUES(last_update)",
            (user_id, daily, weekly, total)
        )


@workout_bp.get("/api/points/<int:user_id>")
def get_points(user_id):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM points_totals WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
    if not row:
        row = {"user_id": user_id, "daily_points": 0, "weekly_points": 0, "total_points": 0}
    return jsonify(row)

@workout_bp.get("/api/workouts/<int:user_id>")
def list_workouts(user_id):
    limit = int(request.args.get("limit", 20))
    with db_cursor() as cur:
        cur.execute(
            "SELECT workout_id, workout_type, sets, reps, points, date_logged "
            "FROM workouts WHERE user_id=%s ORDER BY date_logged DESC LIMIT %s",
            (user_id, limit)
        )
        rows = cur.fetchall()
    return jsonify(rows)

@workout_bp.put("/api/workouts/<int:workout_id>")
def edit_workout(workout_id):
    data = request.get_json(force=True)
    allowed = {"workout_type", "sets", "reps", "points"}
    sets_clause = []
    vals = []
    for k, v in data.items():
        if k in allowed:
            sets_clause.append(f"{k}=%s")
            vals.append(v)
    if not sets_clause:
        return jsonify({"error": "No editable fields provided"}), 400

    with db_cursor(commit=True) as cur:
        cur.execute("SELECT user_id FROM workouts WHERE workout_id=%s", (workout_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Workout not found"}), 404
        user_id = row["user_id"]

        sql = f"UPDATE workouts SET {', '.join(sets_clause)} WHERE workout_id=%s"
        vals.append(workout_id)
        cur.execute(sql, tuple(vals))

    recalc_points(user_id)
    return jsonify({"message": "Workout updated"})

@workout_bp.delete("/api/workouts/<int:workout_id>")
def delete_workout(workout_id):
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT user_id FROM workouts WHERE workout_id=%s", (workout_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Workout not found"}), 404
        user_id = row["user_id"]

        cur.execute("DELETE FROM workouts WHERE workout_id=%s", (workout_id,))

    recalc_points(user_id)
    return jsonify({"message": "Workout deleted"})

