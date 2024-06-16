from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json

app = FastAPI()

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


@app.get("/summary", response_class=HTMLResponse)
async def get_summary(id):
    summary = trailers[id]['synopsis']
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
