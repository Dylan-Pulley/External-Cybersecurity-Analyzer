"""Flask entry point: serve the frontend and register the JSON API."""
from pathlib import Path
from flask import Flask, render_template
from app.routes import api


def create_app(test_config=None):
    root = Path(__file__).resolve().parent.parent
    app = Flask(__name__, template_folder=str(root / "templates"),
                static_folder=str(root / "static"))
    app.config["MAX_CONTENT_LENGTH"] = 4096
    if test_config:
        app.config.update(test_config)
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()
