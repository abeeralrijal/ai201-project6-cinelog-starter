"""
routes/watchlist.py — CineLog (feature/watchlist branch)

Endpoints for the watchlist feature.
"""

from uuid import UUID

from flask import Blueprint, jsonify, request
from services.watchlist_service import AlreadyInWatchlistError, add_to_watchlist, get_watchlist
from services.collection_service import FilmNotFoundError

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """GET /watchlist/<user_id> — Return the user's watchlist."""
    films = get_watchlist(user_id)
    return jsonify(films)


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id):
    """
    POST /watchlist/<user_id>/add

    Body: { "film_id": "<uuid>" }
    """
    data = request.get_json()
    if not isinstance(data, dict) or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

    film_id = data["film_id"]
    if not isinstance(film_id, str):
        return jsonify({"error": "film_id must be a UUID string"}), 400

    try:
        film_id = str(UUID(film_id))
    except ValueError:
        return jsonify({"error": "film_id must be a UUID string"}), 400

    try:
        entry = add_to_watchlist(user_id=user_id, film_id=film_id)
    except FilmNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except AlreadyInWatchlistError as error:
        return jsonify({"error": str(error)}), 409
    return jsonify(entry.to_dict()), 201
