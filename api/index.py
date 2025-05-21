from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

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

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "pore-analysis-api"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Pore Analysis API"}

# Create handler for Vercel
handler = Mangum(app, lifespan="off")

# Export the handler for Vercel
__all__ = ["handler"]
