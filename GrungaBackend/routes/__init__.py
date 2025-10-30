from .users import bpUsers
from .workouts import bpWorkouts
from .friends import bpFriends
from .challenges import bpChallenges
from .badges import bpBadges

def createBlueprints(app):
    app.register_blueprint(bpUsers)
    app.register_blueprint(bpWorkouts)
    app.register_blueprint(bpFriends)
    app.register_blueprint(bpChallenges)
    app.register_blueprint(bpBadges)
