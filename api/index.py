import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from pathlib import Path
import skimage.io

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")

# Import the analyzer after setting up the path
from app.analyzer import analyzer
from app.main import app as fastapi_app

# Configure CORS for Vercel deployment
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For Vercel serverless functions
from mangum import Mangum
handler = Mangum(fastapi_app)

# This is needed for Vercel to recognize the app
app = fastapi_app

# Mount static files for results
OUTPUT_DIR = Path("/tmp/output_data")  # Using /tmp for ephemeral storage in Vercel
OUTPUT_DIR.mkdir(exist_ok=True)
app.mount("/results", StaticFiles(directory=str(OUTPUT_DIR)), name="results")
