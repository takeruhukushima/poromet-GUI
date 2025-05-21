#!/bin/bash

# Ensure vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r api/requirements.txt

# Deploy to Vercel
echo "Deploying to Vercel..."
vercel --prod

echo "Deployment complete!"
