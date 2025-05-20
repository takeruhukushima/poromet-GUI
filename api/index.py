import os
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://your-backend-url.com")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "vercel-proxy"}

# Proxy endpoint for analysis
@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Forward the file to the backend service
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{BACKEND_URL}/api/analyze",
                files=files,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
                
            return JSONResponse(content=response.json())
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless functions
from mangum import Mangum
handler = Mangum(app)

# Local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
