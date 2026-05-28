from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
 
load_dotenv()
 
app = FastAPI()
 
templates = Jinja2Templates(directory="src/templates")
 
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "backend_url": os.getenv("BACKEND_URL", "http://127.0.0.1:8001")
        }
    )