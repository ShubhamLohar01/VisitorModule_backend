# Fix: Missing Dependencies Error in Lambda

## Problem
```
Runtime.ImportModuleError: Unable to import module 'lambda_handler': No module named 'mangum'
```

## Solution: Create Lambda Layer with Dependencies

Your ZIP file doesn't include Python packages. We need to create a Lambda Layer with all dependencies.

---

## Option 1: Create Layer Manually in AWS Console (Easier)

### Step 1: Prepare Dependencies Locally

1. **Open PowerShell or Command Prompt**
2. **Navigate to your backend folder:**
   ```bash
   cd "E:\Visitor Module\backend"
   ```

3. **Create a folder for the layer:**
   ```bash
   mkdir lambda-layer
   cd lambda-layer
   mkdir python
   cd python
   ```

4. **Install all dependencies into this folder:**
   ```bash
   pip install -r ..\..\requirements.txt -t .
   ```

   **Note**: This will take a few minutes and download all packages.

5. **Go back to lambda-layer folder:**
   ```bash
   cd ..
   ```

6. **Create a ZIP file of the python folder:**
   ```bash
   # In PowerShell:
   Compress-Archive -Path python -DestinationPath layer.zip -Force
   ```

   Or manually:
   - Right-click on `python` folder
   - Select "Send to" → "Compressed (zipped) folder"
   - Rename it to `layer.zip`

### Step 2: Upload Layer to AWS

1. **Go to AWS Lambda Console**
   - Search for "Lambda" in AWS Console
   - Click on "Lambda" service

2. **Go to Layers**
   - In left sidebar, click **"Layers"**
   - Click **"Create layer"** button

3. **Configure Layer**
   - **Name**: `visitor-management-dependencies`
   - **Description**: "Python dependencies for Visitor Management API"
   - **Upload a .zip file**: Click "Upload" and select your `layer.zip` file
   - **Compatible runtimes**: Select **"Python 3.11"** (and Python 3.10 if you want)
   - Click **"Create"**

4. **Save Layer ARN**
   - After creation, copy the **Layer ARN** arn:aws:lambda:ap-south-1:548830423226:layer:visitor-management-dependencies:1
   - You'll need this in the next step

### Step 3: Attach Layer to Lambda Function

1. **Go to your Lambda Function**
   - Click on **"Functions"** in left sidebar
   - Click on `visitor-management-api`

2. **Add Layer**
   - Scroll down to **"Layers"** section
   - Click **"Add a layer"**

3. **Select Layer**
   - Select **"Custom layers"**
   - In dropdown, select `visitor-management-dependencies`
   - **Version**: Select the latest version (usually `1`)
   - Click **"Add"**

4. **Verify**
   - You should see the layer listed in the Layers section
   - The layer ARN should be visible

### Step 4: Test Again

1. Go to **"Test"** tab
2. Use the same test event
3. Click **"Test"**
4. Should work now! ✅

---

## Option 2: Use AWS CLI (If you prefer)

If you have AWS CLI configured, you can use these commands:

```bash
# 1. Create layer ZIP (after installing dependencies as in Option 1)
cd lambda-layer
Compress-Archive -Path python -DestinationPath layer.zip -Force

# 2. Create layer in AWS
aws lambda publish-layer-version \
  --layer-name visitor-management-dependencies \
  --description "Python dependencies for Visitor Management API" \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.11 \
  --region ap-south-1

# 3. Get Layer ARN from output, then attach to function
aws lambda update-function-configuration \
  --function-name visitor-management-api \
  --layers arn:aws:lambda:ap-south-1:YOUR_ACCOUNT:layer:visitor-management-dependencies:1 \
  --region ap-south-1
```

---

## Quick Fix Summary

**What you need to do:**

1. ✅ Install dependencies locally into a `python` folder
2. ✅ ZIP that folder
3. ✅ Create Lambda Layer in AWS Console
4. ✅ Upload the ZIP
5. ✅ Attach layer to your Lambda function
6. ✅ Test again

**Time required:** ~10-15 minutes

**File size:** The layer ZIP will be large (50-100 MB), but that's normal for Python dependencies.

---

## Troubleshooting

### Issue: "Layer size exceeds limit"
**Solution**: Lambda Layers have a 250 MB limit (unzipped). If you exceed this:
- Remove unnecessary packages
- Use Lambda Container Image instead (more complex)

### Issue: "Module still not found after adding layer"
**Solution**:
- Make sure layer is attached to function
- Check layer has correct Python version (3.11)
- Verify the `python` folder structure is correct in ZIP

### Issue: "pip install fails"
**Solution**:
- Make sure you're using Python 3.11
- Try: `python -m pip install -r requirements.txt -t .`
- Check internet connection

---

## Folder Structure Should Be:

```
lambda-layer/
  └── python/
      └── [all installed packages]
          ├── mangum/
          ├── fastapi/
          ├── sqlalchemy/
          └── ... (all other packages)
```

Then ZIP the `python` folder (not the `lambda-layer` folder).

---

## After Fixing

Once the layer is attached and working:
- ✅ Lambda function will have access to all dependencies
- ✅ Your handler will be able to import `mangum`, `fastapi`, etc.
- ✅ API Gateway will work correctly
- ✅ You can test all endpoints

**Next step**: After fixing this, continue with API Gateway setup from the main guide!
