from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# npm run build puts the page in web/dist/.
web_build = Path(__file__).resolve().parent / "web" / "dist"
app = FastAPI()
app.mount("/assets", StaticFiles(directory=web_build / "assets"), name="assets")


# This is the data React sends when someone submits the form.
class WebsiteForm(BaseModel):
    website: str


@app.get("/")
def home():
    return FileResponse(web_build / "index.html")


@app.post("/api/website")
def receive_website(form: WebsiteForm):
    website_url = form.website.strip()
    if not website_url:
        raise HTTPException(status_code=400, detail="Enter a website URL.")

    # Send the URL back to check that the form works.
    return {"website": website_url}
