# Quick Guide: Create Layer Using AWS CloudShell

## Step-by-Step Instructions

### Step 1: Open CloudShell

1. Log in to AWS Console: https://console.aws.amazon.com
2. Click the **CloudShell icon** (terminal icon) in the top navigation bar
3. Wait for CloudShell to open (first time: 1-2 minutes)

### Step 2: Upload requirements.txt

1. In CloudShell, click **"Actions"** menu (☰ icon, top right)
2. Select **"Upload file"**
3. Browse to: `E:\Visitor Module\backend\requirements.txt`
4. Click **"Upload"**
5. Wait for upload to complete

### Step 3: Run Build Commands

Copy and paste these commands one by one into CloudShell:

```bash
# Create folder structure
mkdir -p lambda-layer/python/lib/python3.11/site-packages
cd lambda-layer

# Install all dependencies (takes 5-10 minutes)
pip3 install -r ../requirements.txt -t python/lib/python3.11/site-packages/

# Create ZIP file
cd python
zip -r ../../layer.zip .
cd ../..

# Check file size
ls -lh layer.zip
```

**Or use the automated script:**

1. In CloudShell, create a new file:
   ```bash
   nano create-layer.sh
   ```

2. Copy the entire contents of `create-layer-cloudshell.sh` and paste into nano
3. Press `Ctrl+X`, then `Y`, then `Enter` to save
4. Run the script:
   ```bash
   chmod +x create-layer.sh
   ./create-layer.sh
   ```

### Step 4: Download layer.zip

1. In CloudShell, click **"Actions"** menu (☰ icon)
2. Select **"Download file"**
3. Enter: `layer.zip`
4. Click **"Download"**
5. Save it to: `E:\Visitor Module\backend\`

### Step 5: Create Layer in AWS Lambda

1. Go to **Lambda Console** → **Layers**
2. Click **"Create layer"**
3. **Name**: `visitor-management-dependencies`
4. **Upload**: Select the downloaded `layer.zip`
5. **Compatible runtimes**: Select **Python 3.11**
6. Click **"Create"**

### Step 6: Attach to Lambda Function

1. Go to your Lambda function: `visitor-management-api`
2. Scroll to **"Layers"** section
3. Click **"Add a layer"**
4. Select **"Custom layers"**
5. Choose `visitor-management-dependencies`
6. **Version**: Select `1` (or latest)
7. Click **"Add"**

### Step 7: Test

1. Go to **"Test"** tab
2. Use test event:
   ```json
   {
     "httpMethod": "GET",
     "path": "/health",
     "headers": {},
     "body": null
   }
   ```
3. Click **"Test"**
4. Should work! ✅

---

## Troubleshooting

### CloudShell won't open
- Try refreshing the page
- Check browser console for errors
- Try a different browser

### Upload fails
- Make sure file is less than 1GB
- Check file name is correct
- Try uploading again

### pip install fails
- Check internet connection
- Try: `pip3 install --upgrade pip` first
- Check requirements.txt syntax

### ZIP file too large
- Lambda Layers limit: 250 MB (unzipped)
- If exceeded, remove unnecessary packages from requirements.txt

---

## That's It!

Your Lambda function now has all dependencies and should work correctly! 🎉
