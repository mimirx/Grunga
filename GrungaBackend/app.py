import os
from flask import Flask
from dotenv import load_dotenv
from routes import createBlueprints
from services.scheduler_service import startScheduler

def createApp():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    createBlueprints(app)
    startScheduler(os.getenv("TZ", "America/Chicago"))
    return app

app = createApp()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
