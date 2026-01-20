# How to Upload Lambda Layer to S3

This guide shows you how to upload your `layer.zip` file to S3 so you can create a Lambda Layer.

---

## Method 1: Using AWS CLI (Recommended) ⭐

### Step 1: Check if AWS CLI is Installed

Open PowerShell and check:

```powershell
aws --version
```

If you see a version number, you're good to go. If not, install AWS CLI:
- Download from: https://aws.amazon.com/cli/
- Or use: `winget install Amazon.AWSCLI`

### Step 2: Configure AWS Credentials (if not already done)

```powershell
aws  
```

You'll be asked for:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key
- **Default region**: e.g., `ap-south-1` (Mumbai)
- **Default output format**: `json`

### Step 3: Create S3 Bucket (if you don't have one)

```powershell
# Create a bucket (bucket names must be globally unique)
aws s3 mb s3://lambda-layers-your-unique-name

# Example:
aws s3 mb s3://lambda-layers-visitor-module-2024
```

**Note:** Bucket names must be:
- 3-63 characters long
- Lowercase letters, numbers, and hyphens only
- Globally unique across all AWS accounts

### Step 4: Upload layer.zip to S3

```powershell
cd "E:\Visitor Module\backend"

# Upload the file
aws s3 cp layer.zip s3://your-bucket-name/layer.zip

# Example:
aws s3 cp layer.zip s3://lambda-layers-visitor-module-2024/layer.zip
```

You should see output like:
```
upload: ./layer.zip to s3://lambda-layers-visitor-module-2024/layer.zip
```

### Step 5: Get the S3 URL

The S3 URL format is:
```
s3://your-bucket-name/layer.zip
```

Example:
```
s3://lambda-layers-visitor-module-2024/layer.zip
```

---

## Method 2: Using AWS Console (Web Interface)

### Step 1: Go to S3 Console

1. Log in to AWS Console
2. Search for "S3" in the search bar
3. Click on "S3" service

### Step 2: Create a Bucket

1. Click **"Create bucket"** button
2. **Bucket name**: Enter a unique name (e.g., `lambda-layers-visitor-module-2024`)
3. **AWS Region**: Select your region (e.g., `ap-south-1`)
4. **Block Public Access**: Keep default settings (all blocked)
5. Click **"Create bucket"**

### Step 3: Upload layer.zip

1. Click on your bucket name
2. Click **"Upload"** button
3. Click **"Add files"** or drag and drop
4. Select `E:\Visitor Module\backend\layer.zip`
5. Click **"Upload"**
6. Wait for upload to complete

### Step 4: Get the S3 URL

1. Click on the uploaded `layer.zip` file
2. Copy the **"Object URL"** or note the path
3. The S3 URI format is: https://visitor-dependencies-bucket.s3.ap-south-1.amazonaws.com/layer.zip

---

## Method 3: Using PowerShell with AWS Tools

If you have AWS Tools for PowerShell installed:

```powershell
cd "E:\Visitor Module\backend"

# Upload to S3
Write-S3Object -BucketName "lambda-layers-your-bucket-name" -Key "layer.zip" -File "layer.zip" -Region "ap-south-1"
```

---

## After Uploading to S3

### Create Lambda Layer in AWS Console

1. **Go to Lambda Console**
   - Search for "Lambda" in AWS Console
   - Click on "Lambda" service

2. **Go to Layers**
   - In the left sidebar, click **"Layers"**
   - Click **"Create layer"** button

3. **Configure Layer**
   - **Name**: `visitor-management-dependencies` (or any name you prefer)
   - **Description**: "Python dependencies for Visitor Management API"
   - **Upload method**: Select **"Upload a file from Amazon S3"**
   - **S3 link URL**: Enter `s3://your-bucket-name/layer.zip`
   - **Compatible runtimes**: Select **"Python 3.11"**
   - Click **"Create"**

4. **Save Layer ARN**
   - After creation, copy the **Layer ARN**
   - Example: `arn:aws:lambda:ap-south-1:123456789012:layer:visitor-management-dependencies:1`
   - You'll need this to attach to your Lambda function

### Attach Layer to Lambda Function

1. **Go to your Lambda Function**
   - Click on **"Functions"** in left sidebar
   - Click on your function name (e.g., `visitor-management-api`)

2. **Add Layer**
   - Scroll down to **"Layers"** section
   - Click **"Add a layer"**

3. **Select Layer**
   - Select **"Custom layers"**
   - In dropdown, select your layer name
   - **Version**: Select the latest version (usually `1`)
   - Click **"Add"**

4. **Verify**
   - You should see the layer listed in the Layers section
   - The layer ARN should be visible

---

## Troubleshooting

### Error: "Access Denied"
**Solution:** Check your AWS credentials and IAM permissions. You need:
- `s3:PutObject` permission
- `s3:GetObject` permission

### Error: "Bucket name already exists"
**Solution:** Bucket names are globally unique. Try a different name:
```powershell
aws s3 mb s3://lambda-layers-yourname-$(Get-Date -Format "yyyyMMdd")
```

### Error: "Invalid S3 URL"
**Solution:** Make sure the URL format is correct:
- ✅ Correct: `s3://bucket-name/layer.zip`
- ❌ Wrong: `https://s3.amazonaws.com/bucket-name/layer.zip`
- ❌ Wrong: `s3://bucket-name/folder/layer.zip` (unless you uploaded to a folder)

### Check Upload Status

```powershell
# List files in bucket
aws s3 ls s3://your-bucket-name/

# Check file size
aws s3 ls s3://your-bucket-name/layer.zip
```

---

## Quick Reference

**S3 Upload Command:**
```powershell
aws s3 cp "E:\Visitor Module\backend\layer.zip" s3://your-bucket-name/layer.zip
```

**S3 URL Format:**
```
s3://bucket-name/layer.zip
```

**Layer Size Limits:**
- Direct upload: 50 MB (zipped)
- S3 upload: 250 MB (unzipped)
- Your layer: 67.91 MB (zipped) ✅ Under 250 MB limit

---

## Next Steps

1. ✅ Upload `layer.zip` to S3
2. ✅ Create Lambda Layer using S3 URL
3. ✅ Attach layer to your Lambda function
4. ✅ Test your Lambda function

Your Lambda will now have all dependencies! 🎉
