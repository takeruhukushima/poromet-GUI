from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from Vercel!"}

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from API!"}
