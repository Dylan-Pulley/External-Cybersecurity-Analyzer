from pathlib import Path

from flask import Flask, request, send_from_directory

app = Flask(__name__, static_folder="dist/assets", static_url_path="/assets")


@app.get("/")
def home():
    # The React build puts the homepage in dist/.
    return send_from_directory(Path(app.root_path) / "dist", "index.html")


@app.post("/api/website")
def receive_website():
    form_data = request.get_json(silent=True)
    website_url = form_data.get("website") if isinstance(form_data, dict) else None
    if not isinstance(website_url, str) or not website_url.strip():
        return {"error": "Enter a website URL."}, 400

    # Send the URL back so we can see that the form reached Flask.
    return {"website": website_url.strip()}
