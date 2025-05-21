import os
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Initialize FastAPI
app = FastAPI(
    title="Pore Analysis API",
    description="API for analyzing pore images",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/")
async def root():
    return {"status": "ok", "service": "pore-analysis-api"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Simple test endpoint
@app.get("/test")
async def test_endpoint():
    return {"message": "API is working!"}

# Analyze endpoint
@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    magnification: int = Query(300, gt=0),
    max_diam_nm: int = Query(80, gt=0),
    thresh_mag: float = Query(1.8, gt=0)
):
    # For now, return mock data
    return {
        "status": "success",
        "filename": file.filename,
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

# Create handler for Vercel
handler = Mangum(app, api_gateway_base_path="/api")

# Explicitly export the handler for Vercel
__all__ = ["handler"]
