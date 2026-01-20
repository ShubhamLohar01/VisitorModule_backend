#!/bin/bash
# Script to create Lambda Layer in AWS CloudShell
# Copy and paste this entire script into CloudShell

echo "=========================================="
echo "Creating Lambda Layer for AWS Lambda"
echo "=========================================="
echo ""

# Create folder structure
echo "Step 1: Creating folder structure..."
mkdir -p lambda-layer/python/lib/python3.11/site-packages
cd lambda-layer

# Check if requirements.txt exists
if [ ! -f ../requirements.txt ]; then
    echo "ERROR: requirements.txt not found!"
    echo "Please upload requirements.txt to CloudShell first"
    echo "Actions menu -> Upload file -> Select requirements.txt"
    exit 1
fi

# Install dependencies
echo ""
echo "Step 2: Installing dependencies (this will take 5-10 minutes)..."
echo ""

pip3 install -r ../requirements.txt -t python/lib/python3.11/site-packages/

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Create ZIP file
echo ""
echo "Step 3: Creating ZIP file..."
cd python
zip -r ../../layer.zip .

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to create ZIP file"
    exit 1
fi

cd ../..

# Get file size
SIZE=$(ls -lh layer.zip | awk '{print $5}')

echo ""
echo "=========================================="
echo "Layer Created Successfully!"
echo "=========================================="
echo ""
echo "File: layer.zip"
echo "Size: $SIZE"
echo "Location: $(pwd)/layer.zip"
echo ""
echo "Next steps:"
echo "1. Download layer.zip:"
echo "   Actions menu -> Download file -> Enter: layer.zip"
echo ""
echo "2. Go to Lambda Console -> Layers"
echo "3. Create new layer"
echo "4. Upload layer.zip"
echo "5. Select Python 3.11"
echo "6. Attach to your Lambda function"
echo ""
echo "=========================================="
