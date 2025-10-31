from flask import Blueprint, jsonify
from services.connection import fetchAll

bpBadges = Blueprint("badges", __name__, url_prefix="/api/badges")

@bpBadges.get("")
def listBadges():
    return jsonify(fetchAll("SELECT badgeId, code, name, description FROM badges"))
