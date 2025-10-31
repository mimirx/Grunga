import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

from routes import createBlueprints
from services.scheduler_service import startScheduler

def createApp():
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    from config import DB_CONFIG
    print(f"[DB CONFIG] user={DB_CONFIG.get('user')} has_pass={bool(DB_CONFIG.get('password'))}")

    createBlueprints(app)
    startScheduler(os.getenv("TZ", "America/Chicago"))
    return app

app = createApp()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
