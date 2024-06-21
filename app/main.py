from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import Optional
import json
import logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Allow all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trailer synopsis, plot and title created using AI
trailers = open("synopses.json", "r")
trailers = json.load(trailers)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )

@app.get("/summary", response_class=HTMLResponse)
async def get_summary(id: str):
    logging.info(f"Received request for summary with id: {id}")
    summary = trailers.get(id, {}).get('synopsis', 'No synopsis available.')
    return f"""
    <div>
        <h2>Synopsis</h2>
        <p>{summary}</p>
        <button onclick="document.getElementById('modal').classList.remove('open')" class="mt-4 bg-gray-700 text-white rounded px-4 py-2">Close</button>
    </div>
    """

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
