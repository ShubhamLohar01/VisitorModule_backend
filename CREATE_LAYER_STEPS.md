# Step-by-Step: Create Linux-Compatible Lambda Layer

## Prerequisites

1. ✅ Docker Desktop installed and running
2. ✅ `requirements.txt` file exists
3. ✅ `Dockerfile.layer` file exists

---

## Step 1: Check Docker is Running

1. Open Docker Desktop
2. Make sure it shows "Docker Desktop is running" (green icon)
3. If not running, click "Start" and wait

---

## Step 2: Run Build Script

1. Open PowerShell or Command Prompt
2. Navigate to backend folder:
   ```bash
   cd "E:\Visitor Module\backend"
   ```

3. Run the build script:
   ```bash
   .\build-layer-docker.bat
   ```

4. Wait for completion (5-10 minutes on first run)

---

## Step 3: Verify layer.zip Created

After the script completes, check:
- File `layer.zip` should be in `E:\Visitor Module\backend\`
- Size should be 50-150 MB (normal for Python dependencies)

---

## Step 4: Create Layer in AWS Console

1. **Go to AWS Lambda Console**
   - Search "Lambda" in AWS Console
   - Click "Lambda" service

2. **Go to Layers**
   - Click "Layers" in left sidebar
   - Click "Create layer" button

3. **Configure Layer**
   - **Name**: `visitor-management-dependencies`
   - **Description**: "Python dependencies for Visitor Management API (Linux-compatible)"
   - **Upload a .zip file**: Click "Upload" button
   - Browse and select `layer.zip` from your backend folder
   - **Compatible runtimes**: Select **"Python 3.11"**
   - Click **"Create"**

4. **Save Layer ARN**
   - After creation, copy the Layer ARN
   - Looks like: `arn:aws:lambda:ap-south-1:123456789:layer:visitor-management-dependencies:1`

---

## Step 5: Attach Layer to Lambda Function

1. **Go to Your Lambda Function**
   - Click "Functions" in left sidebar
   - Click on `visitor-management-api`

2. **Add Layer**
   - Scroll down to "Layers" section
   - Click "Add a layer"

3. **Select Layer**
   - Select "Custom layers"
   - In dropdown, select `visitor-management-dependencies`
   - **Version**: Select the latest (usually `1`)
   - Click "Add"

4. **Verify**
   - You should see the layer listed
   - Layer ARN should be visible

---

## Step 6: Test Lambda Function

1. Go to "Test" tab
2. Use test event:
   ```json
   {
     "httpMethod": "GET",
     "path": "/health",
     "headers": {},
     "body": null,
     "requestContext": {
       "requestId": "test-request-id"
     }
   }
   ```
3. Click "Test"
4. Should work now! ✅

---

## Troubleshooting

### Docker not running
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Start Docker Desktop
- Wait for green icon

### Build fails
- Check internet connection
- Verify `requirements.txt` exists
- Check Docker logs

### Layer too large
- Lambda Layers have 250 MB limit (unzipped)
- If exceeded, remove unnecessary packages from requirements.txt

### Still getting import errors
- Make sure layer is attached to function
- Check layer version is correct
- Verify Python 3.11 runtime

---

## Success Checklist

- ✅ Docker built layer successfully
- ✅ layer.zip created (50-150 MB)
- ✅ Layer created in AWS Console
- ✅ Layer attached to Lambda function
- ✅ Lambda test passes
- ✅ No import errors

Your Lambda function should now work correctly! 🎉
