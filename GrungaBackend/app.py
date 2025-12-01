from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys
from routes.challenges import challengesBlueprint
from routes.workouts import bpWorkouts
from routes.friendsRoutes import friendsBlueprint
from routes.users import bpUsers
from routes.badges import bpBadges


def createApp():
    app = Flask(__name__)

    # FIXED: Global CORS, supports credentials, no broken regex
    CORS(app, supports_credentials=True)

    @app.route("/api/health")
    def health():
        return jsonify({"ok": True})

    # Blueprints
    app.register_blueprint(bpWorkouts, url_prefix="/api")
    app.register_blueprint(bpUsers, url_prefix="/api/users")
    app.register_blueprint(friendsBlueprint, url_prefix="/api/friends")
    app.register_blueprint(challengesBlueprint, url_prefix="/api/challenges")
    app.register_blueprint(bpBadges, url_prefix="/api/badges")

    return app



app = createApp()


if __name__ == "__main__":
    # IMPORTANT: Only run scheduler in MAIN process, NOT in reloader!
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        try:
            from services.scheduler_service import startScheduler
            print("Starting DAILY scheduler...")
            startScheduler("America/Chicago")
        except Exception as e:
            print("Scheduler failed:", e)

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
