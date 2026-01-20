# Complete Lambda Deployment Guide - S3 Method

## Overview
This guide shows how to deploy your complete FastAPI backend (code + dependencies) as a single Lambda deployment package via S3.

## Benefits of This Approach
- ✅ No layer size limitations (50MB limit bypassed)
- ✅ Everything bundled together (no separate layer management)
- ✅ Can handle large packages (up to 250MB unzipped)
- ✅ Simpler deployment process
- ✅ S3 upload handles large files automatically

## Step 1: Build Complete Deployment Package

Run the deployment package builder:

```bash
# Build the complete package with backend code + all dependencies
.\build-deployment-package.bat
```

This creates `visitor-backend-complete.zip` containing:
- Your FastAPI application (`app/` directory)
- Lambda handler (`lambda_handler.py`)
- All Python dependencies (mangum, fastapi, boto3, etc.)
- Configuration files

## Step 2: Upload to S3

### Option A: AWS Console Upload
1. Go to **S3 Console**
2. Select your bucket (or create one)
3. Click **Upload**
4. Select `visitor-backend-complete.zip`
5. Upload the file
6. Note the **S3 URL** (e.g., `s3://your-bucket/visitor-backend-complete.zip`)

### Option B: AWS CLI Upload
```bash
# Replace 'your-bucket-name' with your actual bucket
aws s3 cp visitor-backend-complete.zip s3://your-bucket-name/lambda-deployments/visitor-backend-complete.zip

# Get the object URL
aws s3 presign s3://your-bucket-name/lambda-deployments/visitor-backend-complete.zip
```

## Step 3: Create/Update Lambda Function from S3

### Option A: AWS Console (Recommended)

1. **Go to Lambda Console**
2. **Create Function** (or select existing function)
3. **Function Configuration:**
   - Function name: `visitor-management-api`
   - Runtime: `Python 3.11`
   - Architecture: `x86_64`

4. **Update Function Code:**
   - Code source: **Upload from S3**
   - S3 bucket: `your-bucket-name`
   - S3 key: `lambda-deployments/visitor-backend-complete.zip`

5. **Configure Handler:**
   - Handler: `lambda_handler.lambda_handler`

6. **Environment Variables** (if needed):
   - Add any required environment variables from your `.env` file

### Option B: AWS CLI Method

```bash
# Create new function
aws lambda create-function \
  --function-name visitor-management-api \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --code S3Bucket=your-bucket-name,S3Key=lambda-deployments/visitor-backend-complete.zip \
  --timeout 30 \
  --memory-size 512 \
  --architecture x86_64

# OR update existing function
aws lambda update-function-code \
  --function-name visitor-management-api \
  --s3-bucket your-bucket-name \
  --s3-key lambda-deployments/visitor-backend-complete.zip
```

## Step 4: Remove Old Layer (If Any)

If your function was using the old layer:

1. Go to **Lambda Console > Functions > visitor-management-api**
2. **Configuration > Layers**
3. **Remove** any old visitor-management-dependencies layers
4. **Save**

## Step 5: Test the Function

1. **Create Test Event:**
   ```json
   {
     "httpMethod": "GET",
     "path": "/api/visitors/stats",
     "headers": {
       "Authorization": "Bearer your-test-token"
     },
     "body": null
   }
   ```

2. **Run Test**
3. **Check Logs** - should see successful mangum import and FastAPI initialization

## Expected Results

✅ **Success Indicators:**
- No "mangum" import errors
- FastAPI app loads successfully
- API endpoints respond correctly
- CloudWatch logs show proper initialization

❌ **If Still Getting Import Errors:**
- Check handler name: `lambda_handler.lambda_handler`
- Verify Python runtime: `3.11`
- Check package contents with verification script

## Package Verification

To verify your package contains everything:

```bash
# Check package contents
python -c "
import zipfile
with zipfile.ZipFile('visitor-backend-complete.zip', 'r') as z:
    files = z.namelist()
    print('Key files check:')
    print('lambda_handler.py:', 'lambda_handler.py' in files)
    print('app/main.py:', 'app/main.py' in files)
    mangum_files = [f for f in files if 'mangum' in f]
    print(f'Mangum files: {len(mangum_files)} found')
    print('Package size:', len(z.infolist()), 'files')
"
```

## Deployment Size Optimization (If Needed)

If package is too large:

1. **Remove unnecessary packages** from `complete-lambda-requirements.txt`
2. **Exclude test files:**
   ```bash
   # Add to build script
   del deployment-package\*test*.py /s /q
   rmdir deployment-package\tests /s /q
   ```
3. **Remove development dependencies**
4. **Compress more efficiently**

## Troubleshooting

### Import Errors
- Ensure `PYTHONPATH` includes package root
- Check file permissions in deployment package
- Verify all dependencies are Linux-compatible

### Size Issues
- Lambda limit: 250MB unzipped, 50MB zipped
- Use S3 for packages > 50MB zipped
- Remove unnecessary files/dependencies

### Runtime Errors
- Check CloudWatch logs for detailed error messages
- Verify environment variables are set correctly
- Test locally first with same package structure

## Success Criteria

After deployment, your Lambda function should:
- ✅ Import mangum successfully
- ✅ Load FastAPI app without errors
- ✅ Handle API Gateway events
- ✅ Return proper HTTP responses
- ✅ No "module not found" errors in logs