from flask import Flask, jsonify
from flask_cors import CORS
import os

from routes.workouts import bpWorkouts 

def createApp():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

    @app.route("/api/health")
    def health():
        return jsonify({"ok": True})

    # ✅ register blueprint correctly
    app.register_blueprint(bpWorkouts, url_prefix="/api")

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
