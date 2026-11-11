from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StrictBool

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
def receive_website(form: WebsiteForm):
    website_url = form.website.strip()
    if not website_url:
        raise HTTPException(status_code=400, detail="Enter a website URL.")

    if not form.has_permission:
        raise HTTPException(status_code=400, detail="Confirm you have permission to test this website.")

    # Send the URL back to check that the form works.
    return {"website": website_url}
