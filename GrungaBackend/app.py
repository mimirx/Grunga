from flask import Flask, jsonify
from flask_cors import CORS
import os

from routes.workouts import bpWorkouts 
from routes.friendsRoutes import friendsBlueprint

def createApp():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "X-Demo-User"])

    @app.route("/api/health")
    def health():
        return jsonify({"ok": True})

    # ✅ register blueprint correctly
    app.register_blueprint(bpWorkouts, url_prefix="/api")
    app.register_blueprint(friendsBlueprint, url_prefix="/api/friends")

    @app.errorhandler(Exception)
    def onError(e):
        return jsonify({"error": str(e)}), 500

    try:
        from services.scheduler_service import startScheduler
        startScheduler(tz="America/Chicago")
    except Exception:
        pass

    return app


app = createApp()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
