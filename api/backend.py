# This is required for Vercel to properly import the app
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the FastAPI app after modifying the path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import os
import io
import tempfile
import json

# Initialize FastAPI
app = FastAPI(title="Pore Analysis API")

# Mock the analyzer for now
try:
    from app.analyzer import analyzer
except ImportError:
    print("Warning: Analyzer module not found. Running in mock mode.")
    analyzer = None

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "service": "pore-analysis-api"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Analyze endpoint
@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    magnification: int = Query(300, gt=0),
    max_diam_nm: int = Query(80, gt=0),
    thresh_mag: float = Query(1.8, gt=0)
):
    # For now, return mock data to test the API
    return {
        "status": "success",
        "filename": file.filename,
        "analysis": "This is a mock response. The API is working but running in mock mode.",
        "parameters": {
            "magnification": magnification,
            "max_diam_nm": max_diam_nm,
            "thresh_mag": thresh_mag
        },
        "results": {
            "average_diameter": 45.6,
            "mode_diameter": 42.1,
            "porosity": 0.65
        }
    }

# For Vercel
from mangum import Mangum
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
