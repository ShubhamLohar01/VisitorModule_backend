# Lambda Layer Verification & Fix Guide

## Current Issue
Lambda function still shows "No module named 'mangum'" error after layer replacement.

## Step 1: Verify Current Function Configuration

1. **Go to AWS Lambda Console**
   - Navigate to your `visitor-management-api` function
   - Click on "Configuration" tab
   - Click on "Layers" in the left sidebar

2. **Check Current Layer**
   - Look for layer: `visitor-management-dependencies_v3`
   - Note the version number (should be latest)
   - If no layer attached or wrong version, this is the problem

## Step 2: Verify Layer Contents (Critical)

1. **Download Current Layer**
   - Go to Lambda > Layers in AWS Console
   - Find `visitor-management-dependencies_v3`
   - Click on latest version
   - Download the layer zip file

2. **Extract and Check for Mangum**
   ```
   Extract the zip file
   Look for: python/lib/python3.11/site-packages/mangum/
   ```

3. **If mangum is missing from layer:**
   - The layer upload failed or was incomplete
   - Need to re-upload our complete layer

## Step 3: Fix - Upload Our Complete Layer

Since our local layer (53MB) contains mangum, we need to upload it properly:

### Option A: S3 Upload Method (Recommended for large files)

1. **Upload to S3 first:**
   ```bash
   # Replace 'your-bucket-name' with actual bucket
   aws s3 cp "complete-visitor-dependencies.zip" s3://your-bucket-name/lambda-layers/
   ```

2. **Create layer from S3:**
   ```bash
   aws lambda publish-layer-version \
     --layer-name visitor-management-dependencies \
     --description "Complete visitor management dependencies with mangum" \
     --content S3Bucket=your-bucket-name,S3Key=lambda-layers/complete-visitor-dependencies.zip \
     --compatible-runtimes python3.11 \
     --compatible-architectures x86_64
   ```

### Option B: Console Upload (If file under 50MB)

1. Go to Lambda > Layers > Create layer
2. Name: `visitor-management-dependencies-complete`
3. Upload: `complete-visitor-dependencies.zip`
4. Runtime: Python 3.11
5. Architecture: x86_64

## Step 4: Attach New Layer to Function

1. **Go to your Lambda function**
2. **Configuration > Layers**
3. **Remove old layer** (if any)
4. **Add layer**:
   - Choose custom layers
   - Select: `visitor-management-dependencies-complete` (or whatever you named it)
   - Version: Latest (1)

## Step 5: Test

1. **Test the function**
2. **Check logs** - should not show mangum import error

## Troubleshooting

If still getting mangum error after following steps:

1. **Check handler path**: Should be `lambda_handler.lambda_handler`
2. **Verify file name**: Must be `lambda_handler.py`
3. **Check layer architecture**: Must be x86_64 (not arm64)
4. **Check Python version**: Layer and function must both use Python 3.11

## Quick Verification Command

To verify our local layer contains mangum:
```bash
cd "e:\Visitor Module\backend\lambda-build"
python -c "
import zipfile
with zipfile.ZipFile('complete-visitor-dependencies.zip', 'r') as z:
    files = z.namelist()
    mangum_files = [f for f in files if 'mangum' in f.lower()]
    print(f'Found {len(mangum_files)} mangum files in layer')
    for f in mangum_files[:10]:  # Show first 10
        print(f'  {f}')
"
```

This will confirm our layer contains mangum before uploading.