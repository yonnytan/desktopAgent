"""Flask routes for the backend application."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify, request

from services.bash_service import Bash


def register_routes(app: Flask, bash_service: BashService) -> None:
    """Register all API routes for the backend application."""

    router = Blueprint("commands", __name__, url_prefix="/commands")

    @router.route("/execute", methods=["POST"])
    def execute_command() -> tuple[dict, int] | tuple[dict, int, dict]:
        payload_data = request.get_json(silent=True) or {}

        try:
            payload = CommandRequest(**payload_data)
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        response: CommandResponse = bash_service.execute(payload)
        if response.error:
            return jsonify({"detail": response.error}), 400

        return jsonify(response.model_dump()), 200

    @router.route("/state", methods=["GET"])
    def get_state() -> tuple[dict, int] | tuple[dict, int, dict]:
        response: CommandResponse = bash_service.state()
        return jsonify(response.model_dump()), 200

    app.register_blueprint(router)
