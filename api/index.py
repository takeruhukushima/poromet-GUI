import os
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from analyze import router as analyze_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router, prefix="/api")

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://your-backend-url.com")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "vercel-proxy"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Pore Analysis API"}

# For Vercel serverless functions
from mangum import Mangum
handler = Mangum(app, lifespan="off")

# Local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="0.0.0.0", port=3000, reload=True)
