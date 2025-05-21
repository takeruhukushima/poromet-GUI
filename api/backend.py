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

# Initialize FastAPI
app = FastAPI(title="Pore Analysis API")

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
    try:
        # Import analyzer
        try:
            from app.analyzer import analyzer
            from app.main import app as main_app
        except ImportError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to import analyzer: {str(e)}. Python path: {sys.path}"
            )
        
        # Create a temporary file
        temp_dir = Path(tempfile.mkdtemp())
        temp_file_path = temp_dir / file.filename
        
        try:
            # Save uploaded file
            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Call the analyzer
            img = analyzer.analyze_image(
                str(temp_file_path),
                magnification=magnification,
                max_diam_nm=max_diam_nm,
                thresh_mag=thresh_mag
            )
            
            # Process results (adjust based on your analyzer's return type)
            return {
                "status": "success",
                "filename": file.filename,
                "analysis": "Analysis results here"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
            
        finally:
            # Clean up
            try:
                temp_file_path.unlink()
                temp_dir.rmdir()
            except Exception as e:
                print(f"Warning: Failed to clean up temp files: {e}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel
from mangum import Mangum
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
