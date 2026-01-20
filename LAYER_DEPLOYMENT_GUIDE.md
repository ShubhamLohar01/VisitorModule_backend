# Lambda Layer Deployment Guide

## Issue Fixed
✅ **Fixed Mangum compatibility issue**: Updated from `mangum==0.18.1` to `mangum==0.20.0`
✅ **Removed unsupported parameter**: Removed `log_level` from Mangum initialization
✅ **Version consistency**: Aligned all dependencies between layer and package requirements

## Layer File
Your dependencies layer has been created: `build\visitor-management-dependencies.zip`

## Deployment Steps

### Option 1: AWS Console
1. Open AWS Lambda Console
2. Navigate to "Layers" in the left sidebar
3. Click "Create layer"
4. **Layer configuration**:
   - Name: `visitor-management-dependencies`
   - Description: `Dependencies for Visitor Management System`
   - Upload: Choose `build\visitor-management-dependencies.zip`
   - Compatible runtimes: `Python 3.11`
   - Compatible architectures: `x86_64`
5. Click "Create"
6. **Copy the Layer ARN** that appears after creation

### Option 2: AWS CLI
```bash
# Deploy layer
aws lambda publish-layer-version \
    --layer-name visitor-management-dependencies \
    --description "Dependencies for Visitor Management System" \
    --zip-file fileb://build/visitor-management-dependencies.zip \
    --compatible-runtimes python3.11 \
    --compatible-architectures x86_64

# Note the LayerVersionArn from the response
```

### Option 3: Use the Deploy Script
Run the automated deployment script:
```cmd
.\deploy-layer.bat
```

## Update Your Lambda Function

### Add Layer to Function
1. Open your Lambda function in AWS Console
2. Go to "Configuration" → "Layers"
3. Click "Add a layer"
4. Select "Custom layers"
5. Choose your layer: `visitor-management-dependencies`
6. Select the latest version
7. Click "Add"

### Alternative: AWS CLI
```bash
# Update function configuration to include layer
aws lambda update-function-configuration \
    --function-name your-function-name \
    --layers arn:aws:lambda:region:account:layer:visitor-management-dependencies:version
```

## Package Your Lambda Function Code

Since dependencies are now in the layer, your deployment package should be minimal:

```cmd
# Create deployment package (code only)
.\build-package.bat
```

This will create `build\visitor-management-package.zip` with only your application code.

## Deploy Function Code

Upload the code package to your Lambda function:

```bash
aws lambda update-function-code \
    --function-name your-function-name \
    --zip-file fileb://build/visitor-management-package.zip
```

## Testing

After deployment:
1. Test your Lambda function using the AWS Console test feature
2. Check CloudWatch logs for any remaining issues
3. Verify the health endpoint responds correctly

## Key Changes Made

### lambda_handler.py
- Removed `log_level="info"` parameter from Mangum initialization
- This parameter is not supported in Mangum 0.20.0 and earlier versions

### layer-requirements.txt  
- Updated `mangum==0.20.0` (was 0.18.1)
- Updated `starlette==0.49.3` (was 0.50.0) for consistency
- All other dependencies remain the same

## Troubleshooting

### If you still get errors:
1. **Check Layer ARN**: Ensure the layer is properly attached to your function
2. **Check Python Version**: Verify both layer and function use Python 3.11
3. **Check Imports**: Verify all imports in your code match the dependencies in the layer
4. **Check Logs**: Look at CloudWatch logs for detailed error information

### Common Issues:
- **ModuleNotFoundError**: Layer not attached or package in wrong directory structure
- **Version Conflicts**: Mixed dependency versions between layer and package
- **Path Issues**: Ensure layer follows correct directory structure (`python/lib/python3.11/site-packages/`)

## Next Steps

1. Deploy the layer using one of the methods above
2. Update your Lambda function to use the layer
3. Deploy your application code (without dependencies)
4. Test the function
5. Monitor CloudWatch logs for any issues

The `log_level` error should now be resolved, and your Lambda function should work correctly with the updated dependencies.