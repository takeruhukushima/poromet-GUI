from fastapi import FastAPI
from mangum import Mangum

# Initialize FastAPI
app = FastAPI()

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Create handler for Vercel
handler = Mangum(app, lifespan="off")

# Export the handler for Vercel
__all__ = ["handler"]
