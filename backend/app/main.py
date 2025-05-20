from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from pathlib import Path
from .analyzer import analyzer
import skimage.io
from skimage.filters import threshold_otsu
import numpy as np

app = FastAPI(title="Pore Size Analyzer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
OUTPUT_DIR = Path("output_data")
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/results", StaticFiles(directory=str(OUTPUT_DIR)), name="results")

@app.post("/analyze")
async def analyze_pore_size(
    file: UploadFile = File(...),
    magnification: int = 300,
    max_diam_nm: int = 80,
    thresh_mag: float = 1.80
):
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_DIR / timestamp
    output_dir.mkdir(exist_ok=True)
    try:
        # Save uploaded file temporarily
        temp_file = output_dir / "input_image.jpg"
        try:
            with temp_file.open("wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Verify file is an image
            try:
                from PIL import Image
                Image.open(str(temp_file))
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image file: {str(e)}"
                )

            # Analyze the image
            try:
                # Read image
                img = skimage.io.imread(str(temp_file), as_gray=True)
                
                # Analyze
                results, mask, im_thick = analyzer.analyze_image(
                    str(temp_file),
                    magnification=magnification,
                    max_diam_nm=max_diam_nm,
                    thresh_mag=thresh_mag
                )

                # Get pixel size from results
                try:
                    # Try to get pixel size from image info
                    px_per_nm = float(results['image_info']['pixel_size'].split()[0])
                except (KeyError, ValueError):
                    # Fallback to default pixel size
                    px_per_nm = 0.303  # Default for 300x magnification

                # Save results
                analyzer.save_results(
                    Path(output_dir),
                    results,
                    mask,
                    im_thick
                )

            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Analysis failed: {str(e)}"
                )

            # Prepare response
            response = {
                "status": "success",
                "results": results,
                "output_directory": str(output_dir)
            }
            
            # Debug prints
            print("\nDebug Response:")
            print(f"Average Diameter: {results['statistics']['average_diameter']}")
            print(f"Mode Diameter: {results['statistics']['mode_diameter']}")
            
            return JSONResponse(content=response)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results/{timestamp}/{filename:path}")
async def get_result_file(timestamp: str, filename: str):
    result_dir = OUTPUT_DIR / timestamp
    if not result_dir.exists():
        raise HTTPException(status_code=404, detail="Results not found")
    
    file_path = result_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)