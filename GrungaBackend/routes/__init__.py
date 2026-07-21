# GrungaBackend/routes/__init__.py
from .users import bpUsers
from .workouts import bpWorkouts
from .badges import bpBadges
from .streaks import bpStreaks

def createBlueprints(app):
    app.register_blueprint(bpUsers)
    app.register_blueprint(bpWorkouts)
    app.register_blueprint(bpBadges)
    app.register_blueprint(bpStreaks)
