# Pore Size Analyzer

A full-stack web application for analyzing pore sizes in SEM images using FastAPI (backend) and Next.js (frontend).

## Features

- Upload SEM images for analysis via drag-and-drop or file browser
- Configure analysis parameters:
  - Magnification
  - Maximum diameter
  - Threshold multiplier
- View comprehensive analysis results:
  - Average and mode pore diameters
  - Pore size distribution histogram
  - Thresholded image visualization
  - Colormap visualization
  - Raw histogram data in tabular format
- Download raw data for further analysis

## Tech Stack

- **Backend**: FastAPI, Python, porespy, scikit-image, matplotlib
- **Frontend**: Next.js, React, Tailwind CSS, shadcn/ui
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

## Runnning with local host

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

### another bush
s
npm install
npm run dev



### Running with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pore-size-analyzer.git
   cd pore-size-analyzer

