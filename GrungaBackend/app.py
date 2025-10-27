from flask import Flask
from flask_cors import CORS
from routes.workout_routes import workout_bp

app = Flask(__name__)
CORS(app)

@app.get("/")
def home():
    return "Grunga backend is running!"

app.register_blueprint(workout_bp)

if __name__ == "__main__":
    app.run(debug=True)
