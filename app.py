from pathlib import Path

from flask import Flask, request, send_from_directory

# npm run build puts the page in web/dist/.
web_build = Path(__file__).resolve().parent / "web" / "dist"
app = Flask(__name__, static_folder=str(web_build / "assets"), static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(web_build, "index.html")


@app.post("/api/website")
def receive_website():
    form_data = request.get_json(silent=True)
    website_url = form_data.get("website") if isinstance(form_data, dict) else None
    if not isinstance(website_url, str) or not website_url.strip():
        return {"error": "Enter a website URL."}, 400

    # Send the URL back to check that the form works.
    return {"website": website_url.strip()}
