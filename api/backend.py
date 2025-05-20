import os
import sys
import io
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

# Initialize FastAPI
app = FastAPI(title="Pore Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
