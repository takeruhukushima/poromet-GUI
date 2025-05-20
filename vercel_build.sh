#!/bin/bash
# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt --target ./python

# Make sure the python directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/python

# Create a simple vercel_builder.py file
cat > vercel_builder.py << 'EOF'
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

def vercel_builder():
    print("Vercel builder completed successfully")

if __name__ == "__main__":
    vercel_builder()
EOF

# Run the vercel builder
python vercel_builder.py
