from fastapi import FastAPI

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

# Vercel will look for the 'app' instance by convention.
