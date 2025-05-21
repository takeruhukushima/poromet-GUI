import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "vercel-proxy"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Pore Analysis API"}

# For Vercel serverless functions
handler = Mangum(app, lifespan="off")

# Local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="0.0.0.0", port=3000, reload=True)

# Export the handler for Vercel
__all__ = ["handler"]
