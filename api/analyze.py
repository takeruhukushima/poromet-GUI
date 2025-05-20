import os
import httpx
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://your-backend-url.com")

@router.post("/analyze")
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
                
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
