"""HTTP input/output only. TLS collection lives in tls_check.py."""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import HTTPException
from app import tls_check

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/health")
def health():
    return jsonify(ok=True)


@api.post("/scan")
def scan():
    if not request.is_json:
        return jsonify(error="Send a JSON body with a url field."), 415
    body = request.get_json()
    if not isinstance(body, dict) or not isinstance(body.get("url"), str):
        return jsonify(error="Provide a website in the url field."), 400
    try:
        result = tls_check.check(body["url"])
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(result)


@api.errorhandler(HTTPException)
def http_error(exc):
    return jsonify(error=exc.description), exc.code
