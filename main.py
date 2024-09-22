from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from web_scraper import get_website_text_content
from chat_request import send_openai_request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

class UrlRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join("static", "favicon.ico"))

@app.post("/crawl")
async def crawl(url_request: UrlRequest):
    url = url_request.url
    if not url:
        return JSONResponse(content={"error": "No URL provided"}, status_code=400)

    try:
        # Crawl the website
        content = get_website_text_content(url)

        # Generate description using 4o-mini model
        prompt = f"Provide a brief description of the following website content:\n\n{content[:1000]}..."
        description = send_openai_request(prompt)

        return JSONResponse(content={"description": description})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
