from flask import Flask, jsonify
from flask_cors import CORS
import os

from routes.workouts import bpWorkouts
from routes.friendsRoutes import friendsBlueprint


def createApp():
    app = Flask(__name__)
    CORS(
        app,
        resources={
            r"/api/*": {
                # during development you can just use "*" to avoid origin issues
                "origins": [
                    "http://127.0.0.1:5500",
                    "http://localhost:5500",
                    # if you ever serve frontend from somewhere else, add it here
                ],
                "allow_headers": ["Content-Type", "X-Demo-User"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            }
        },
        supports_credentials=True,
    )

    @app.route("/api/health")
    def health():
        return jsonify({"ok": True})

    # ===== Register blueprints =====
    # Workouts endpoints live under /api/...
    app.register_blueprint(bpWorkouts, url_prefix="/api")

    # Friends endpoints live under /api/friends/...
    app.register_blueprint(friendsBlueprint, url_prefix="/api/friends")

    # ===== Global error handler (optional) =====
    @app.errorhandler(Exception)
    def handle_exception(e):
        # you can add logging here if you want
        return jsonify({"error": str(e)}), 500

    # ===== Background scheduler (weekly jobs etc.) =====
    try:
        from services.scheduler_service import startScheduler
        startScheduler(tz="America/Chicago")
    except Exception:
        # if scheduler fails we don't want the whole app to crash
        pass

    return app


app = createApp()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
