
from pathlib import Path
import socket
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StrictBool


#Main application Test
import main
import json
from fastapi.responses import StreamingResponse

# npm run build puts the page in web/dist/.
web_build = Path(__file__).resolve().parent / "web" / "dist"
app = FastAPI()
app.mount("/assets", StaticFiles(directory=web_build / "assets"), name="assets")


# This is the data React sends when someone submits the form.
class WebsiteForm(BaseModel):
    website: str
    has_permission: StrictBool = False


@app.get("/")
def home():
    return FileResponse(web_build / "index.html")


@app.post("/api/website")
@app.post("/api/scan")
def receive_website(form: WebsiteForm):
    website_url = form.website.strip()
    if not website_url:
        raise HTTPException(status_code=400, detail="Enter a website URL.")

    if not form.has_permission:
        raise HTTPException(status_code=400, detail="Confirm you have permission to test this website.")

    try:
        if "://" not in website_url:  #!
            website_url = "https://" + website_url  #!
        target = urlsplit(website_url)
        if target.scheme not in ("http", "https") or not target.hostname or target.username or target.password:  #changed here for http target
            raise ValueError("Enter an HTTP/HTTPS URL without credentials.")  #and here too
        # Validate the port before handing the URL to the tools.
        target.port
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    def stream_results():
        try:
            for results in main.main(website_url):
                message = {
                    "website": website_url,
                    "results": {
                        results["scan"]: results["result"]
                    }
                }
                yield json.dumps(message) + "\n"
        except socket.gaierror:
            yield json.dumps({
                "website": website_url,
                "results": {
                    "error": "Could not resolve the website hostname."
                }
            }) + "\n"

    return StreamingResponse(stream_results(), media_type="application/x-ndjson")
