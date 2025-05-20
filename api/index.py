import os
import sys
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Set up path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Initialize FastAPI
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Import the analyzer only when needed (lazy loading)
analyzer = None
def get_analyzer():
    global analyzer
    if analyzer is None:
        try:
            from backend.app.analyzer import analyzer as analyzer_module
            analyzer = analyzer_module.analyzer
        except ImportError as e:
            print(f"Error importing analyzer: {e}")
            analyzer = None
    return analyzer

# Example endpoint that uses the analyzer
@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Get the analyzer
        analyzer = get_analyzer()
        if not analyzer:
            raise HTTPException(status_code=500, detail="Analyzer not available")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process the image (simplified example)
            # Replace this with your actual analysis logic
            result = {"message": "Analysis complete", "filename": file.filename}
            return JSONResponse(content=result)
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless functions
from mangum import Mangum
handler = Mangum(app)

# This is needed for Vercel to recognize the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
