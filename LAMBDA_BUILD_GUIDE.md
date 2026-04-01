# Lambda Deployment Package Builder (Linux Compatible)

This guide explains how to build a Lambda deployment package with proper Linux environment support for your Visitor Management System backend.

## Overview

AWS Lambda runs on Amazon Linux 2, so dependencies must be compiled for Linux even if you're building on Windows or macOS. This package includes two build methods:

1. **Docker Method** (Recommended) - Uses Docker to build in a Lambda-compatible Linux environment
2. **Pip Fallback Method** - Uses pip with platform targeting (less reliable)

## Prerequisites

### Required
- Python 3.11+
- pip

### Recommended (for Production)
- Docker Desktop (for Linux-compatible builds)

## Build Methods

### Method 1: Python Script (Recommended)

The Python script provides better cross-platform compatibility and detailed logging.

```bash
# Run the build script
python build_lambda_linux.py
```

**Advantages:**
- Works on Windows, macOS, and Linux
- Better error handling
- Detailed progress reporting
- Automatic Docker detection
- Cross-platform path handling

### Method 2: PowerShell Script

For Windows environments, you can use the PowerShell script.

```powershell
# Run from PowerShell
.\build-lambda-linux.ps1
```

**Advantages:**
- Native Windows integration
- PowerShell-specific features
- Windows terminal color support

## Build Process

Both scripts follow the same process:

1. **Validation** - Checks for required files (app/, lambda_handler.py, requirements.txt)
2. **Setup** - Creates temporary build directory
3. **Copy Code** - Copies application code to build directory
4. **Install Dependencies** - Installs Python packages for Linux
   - With Docker: Uses Amazon Linux 2 base image
   - Without Docker: Uses pip with manylinux platform target
5. **Cleanup** - Removes unnecessary files (__pycache__, tests, .pyc, etc.)
6. **Package** - Creates zip file for Lambda deployment

## Output

After successful build, you'll have:

```
lambda-deployment-linux.zip
```

This file contains:
- `lambda_handler.py` - Lambda entry point
- `app/` - Your FastAPI application
- All Python dependencies (Linux-compatible)

## Package Size Considerations

Lambda has deployment package size limits:

- **Direct Upload Limit**: 50 MB (compressed)
- **S3 Upload Limit**: 250 MB (compressed)
- **Uncompressed Limit**: 250 MB

### If Your Package Exceeds 50 MB

1. **Use S3 Upload**:
   ```bash
   # Upload to S3
   aws s3 cp lambda-deployment-linux.zip s3://your-bucket/lambda-deployment-linux.zip
   
   # Update Lambda from S3
   aws lambda update-function-code \
     --function-name your-function-name \
     --s3-bucket your-bucket \
     --s3-key lambda-deployment-linux.zip
   ```

2. **Use Lambda Layers**:
   Create a separate layer for dependencies:
   ```bash
   # Build layer (see LAYER_DEPLOYMENT_GUIDE.md)
   python build_lambda_layer.py
   
   # Then build application code only
   # (modify script to skip dependency installation)
   ```

### If Your Package Exceeds 250 MB

You **MUST** use Lambda Layers to separate dependencies from application code.

## Docker Build Details

When Docker is available, the build uses:

**Base Image**: `public.ecr.aws/lambda/python:3.11`
- This is the exact runtime environment Lambda uses
- Ensures 100% compatibility with Lambda execution environment
- Includes Amazon Linux 2 system libraries

**Build Process**:
1. Creates temporary Docker container
2. Installs all requirements in container
3. Extracts built packages
4. Cleans up container

## Without Docker

If Docker is not available, the script falls back to:

```bash
pip install -r requirements.txt \
  --target ./build \
  --platform manylinux2014_x86_64 \
  --only-binary=:all:
```

**Note**: This method has limitations:
- Some packages may not have pre-built Linux wheels
- Binary dependencies may not match Lambda environment exactly
- Not recommended for production deployments

## Deployment to Lambda

### Step 1: Upload Package

**Option A: Direct Upload (if < 50 MB)**
```bash
aws lambda update-function-code \
  --function-name visitor-management-api \
  --zip-file fileb://lambda-deployment-linux.zip
```

**Option B: S3 Upload (if 50-250 MB)**
```bash
# Upload to S3
aws s3 cp lambda-deployment-linux.zip s3://your-bucket/

# Update Lambda
aws lambda update-function-code \
  --function-name visitor-management-api \
  --s3-bucket your-bucket \
  --s3-key lambda-deployment-linux.zip
```

### Step 2: Configure Lambda Function

```bash
aws lambda update-function-configuration \
  --function-name visitor-management-api \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    DATABASE_URL=your-database-url,
    SECRET_KEY=your-secret-key,
    ENVIRONMENT=production,
    AWS_S3_BUCKET=your-bucket-name
  }"
```

### Step 3: Test Deployment

```bash
# Test health endpoint
aws lambda invoke \
  --function-name visitor-management-api \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json

# View response
cat response.json
```

## Environment Variables

Ensure these environment variables are set in Lambda:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `ENVIRONMENT` | Set to "production" | Yes |
| `AWS_S3_BUCKET` | S3 bucket for file uploads | Yes |
| `AWS_REGION` | AWS region | No (auto-detected) |
| `CORS_ORIGINS` | Allowed CORS origins | No |

## Troubleshooting

### Build Fails: Docker Not Found

**Solution**: Install Docker Desktop
- Windows: https://www.docker.com/products/docker-desktop
- macOS: https://www.docker.com/products/docker-desktop
- Linux: Use your package manager

### Build Fails: Permission Denied

**Windows PowerShell**:
```powershell
# Run as Administrator or adjust execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS**:
```bash
chmod +x build_lambda_linux.py
```

### Package Too Large

**Solution 1**: Use Lambda Layers
```bash
# See LAYER_DEPLOYMENT_GUIDE.md for instructions
```

**Solution 2**: Optimize dependencies
```bash
# Use minimal requirements
pip install -r requirements-minimal.txt
```

### Import Errors in Lambda

**Cause**: Dependencies not compiled for Linux

**Solution**: Use Docker method for guaranteed compatibility
```bash
python build_lambda_linux.py
# Ensure Docker is running
```

## File Structure

After build, your package contains:

```
lambda-deployment-linux.zip
├── lambda_handler.py          # Lambda entry point
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── ...
│   ├── routers/
│   │   ├── visitor.py
│   │   ├── approver.py
│   │   ├── appointment.py
│   │   └── ...
│   ├── models/
│   ├── schemas/
│   └── services/
├── fastapi/                   # Dependencies
├── starlette/
├── uvicorn/
├── mangum/                    # ASGI adapter for Lambda
├── boto3/
├── sqlalchemy/
├── psycopg2/
└── ...                        # Other dependencies
```

## Performance Optimization

### Cold Start Optimization

1. **Reduce Package Size**: Remove unnecessary dependencies
2. **Use Provisioned Concurrency**: Keep instances warm
3. **Optimize Imports**: Import only what's needed

### Runtime Optimization

1. **Connection Pooling**: Reuse database connections
2. **Environment Variables**: Pre-load configuration
3. **Async Operations**: Use async/await for I/O operations

## Related Documentation

- [LAMBDA_DEPLOYMENT_GUIDE.md](./LAMBDA_DEPLOYMENT_GUIDE.md) - Detailed deployment guide
- [LAYER_DEPLOYMENT_GUIDE.md](./LAYER_DEPLOYMENT_GUIDE.md) - Creating Lambda layers
- [AWS_CONSOLE_SETUP_GUIDE.md](./AWS_CONSOLE_SETUP_GUIDE.md) - Manual setup via AWS Console

## Support

For issues or questions:
1. Check build logs for specific error messages
2. Verify Docker is running (if using Docker method)
3. Ensure all required files exist in backend directory
4. Check AWS Lambda limits and quotas

## Version History

- **v1.0** - Initial release with Docker support
- **v1.1** - Added pip fallback method
- **v1.2** - Improved cleanup and size optimization
