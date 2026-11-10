from pathlib import Path

from flask import Flask, request, send_from_directory

app = Flask(__name__, static_folder="dist/assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(Path(app.root_path) / "dist", "index.html")


@app.post("/api/website")
def receive_website():
    data = request.get_json(silent=True)
    website = data.get("website") if isinstance(data, dict) else None
    if not isinstance(website, str) or not website.strip():
        return {"error": "Enter a website URL."}, 400

    return {"website": website.strip()}
