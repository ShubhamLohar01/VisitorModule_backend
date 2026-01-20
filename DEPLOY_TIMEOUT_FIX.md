# Quick Deploy: Timeout Fix

This guide shows you the **fastest way** to deploy the timeout fixes.

---

## What Changed?

✅ Lambda timeout: `30s → 120s`  
✅ Lambda memory: `512MB → 1024MB`  
✅ S3 connect timeout: `5s → 10s`  
✅ S3 read timeout: `10s → 60s`  
✅ S3 retry attempts: `2 → 3`

---

## Option 1: AWS Console (Fastest - 5 minutes)

### Step 1: Update Lambda Timeout (2 minutes)

1. **Open Lambda Console**
   - Go to: https://console.aws.amazon.com/lambda
   - Sign in to AWS
   - Select region: **ap-south-1 (Mumbai)**

2. **Select Your Function**
   - Click on your function (e.g., `visitor-management-api-dev-api` or similar)

3. **Update Configuration**
   - Click **Configuration** tab
   - Click **General configuration** in left sidebar
   - Click **Edit** button
   
4. **Change Settings**
   - **Memory**: Change from `512 MB` to **`1024 MB`**
   - **Timeout**: Change from `30 seconds` or `1 min` to **`2 min 0 sec`**
   - Click **Save**

### Step 2: Update Lambda Code with S3 Fix (3 minutes)

You need to redeploy your Lambda code with the updated S3 service.

**Option A: Quick Re-upload (if you have ZIP)**

1. Go to your Lambda function in AWS Console
2. Click **Code** tab
3. Click **Upload from** dropdown → **`.zip file`**
4. Upload your updated deployment package
5. Click **Save**

**Option B: Build and Upload New Package**

1. Open PowerShell in your backend folder:
   ```powershell
   cd "E:\Visitor Module\backend"
   ```

2. Create deployment package:
   ```powershell
   # If you have build-deploy.ps1
   .\build-deploy.ps1
   
   # OR manually create zip
   Compress-Archive -Path app,lambda_handler.py -DestinationPath lambda-deployment.zip -Force
   ```

3. Upload to Lambda:
   - Go to Lambda Console
   - Click **Upload from** → **`.zip file`**
   - Select `lambda-deployment.zip`
   - Click **Save**

### ✅ Done!

Test your application. The timeout should be fixed.

---

## Option 2: Using Serverless Framework (Automated)

If you have Serverless Framework installed:

```powershell
cd "E:\Visitor Module\backend"

# Deploy to dev environment
serverless deploy --stage dev --verbose

# Or to production
serverless deploy --stage prod --verbose
```

This will automatically:
- Update Lambda timeout to 120s
- Update memory to 1024 MB
- Deploy new code with S3 fixes

---

## Option 3: Using AWS SAM (if using template.yaml)

```powershell
cd "E:\Visitor Module\backend"

# Build
sam build

# Deploy
sam deploy --guided
```

---

## Verification

After deployment, test the endpoint:

### Test 1: Check Lambda Configuration

1. Go to Lambda Console
2. Click **Configuration** → **General configuration**
3. Verify:
   - **Memory**: `1024 MB` ✅
   - **Timeout**: `2 min 0 sec` ✅

### Test 2: Submit a Visitor Form

1. Go to your frontend: `http://localhost:3000`
2. Fill out the visitor form
3. Take a selfie
4. Submit

**Expected:**
- ✅ Form submits successfully (no 504 error)
- ✅ Completion time: 10-20 seconds
- ⏱️ If still slow (20-30s): Consider VPC Endpoint for S3 (see below)

### Test 3: Check CloudWatch Logs

1. Go to Lambda Console → **Monitor** tab
2. Click **View logs in CloudWatch**
3. Check the latest log stream
4. Look for execution duration (should be under 30 seconds)

---

## Still Getting 504? Additional Fixes

### Fix 1: API Gateway Integration Timeout

⚠️ **API Gateway has a hard limit of 29 seconds.**

If your Lambda takes > 29 seconds, API Gateway will timeout regardless of Lambda timeout.

**Check in AWS Console:**

1. Go to **API Gateway Console**
2. Select your API
3. Click **Resources**
4. Click on any `ANY /{proxy+}` method
5. Click **Integration Request**
6. Check **Timeout** setting (should be between 50-29000 ms)

**If timeout is the issue:**
- Make the endpoint async (return immediately, process in background)
- Use SQS queue for image upload
- Implement polling mechanism on frontend

### Fix 2: Add VPC Endpoint for S3 (Highly Recommended)

Your Lambda is in a VPC, which makes S3 access slow through NAT Gateway.

**Create VPC Endpoint (Free):**

1. Go to **VPC Console**: https://console.aws.amazon.com/vpc
2. Click **Endpoints** (left sidebar)
3. Click **Create Endpoint**
4. **Configuration:**
   - **Service category**: AWS services
   - **Service Name**: Search for `s3` → Select `com.amazonaws.ap-south-1.s3` (Gateway)
   - **VPC**: Select your Lambda's VPC
   - **Route tables**: Select all route tables
5. Click **Create endpoint**

**Result:** S3 upload speed will improve by 50-80% (from 10-20s to 3-5s)

### Fix 3: Compress Images on Frontend

Reduce image size before upload:

**Add to frontend** (`components/visitor-form.tsx`):

```typescript
const compressImage = async (base64Image: string): Promise<string> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d')!;
      
      // Resize to max 800x800
      let width = img.width;
      let height = img.height;
      const maxSize = 800;
      
      if (width > maxSize || height > maxSize) {
        if (width > height) {
          height = (height / width) * maxSize;
          width = maxSize;
        } else {
          width = (width / height) * maxSize;
          height = maxSize;
        }
      }
      
      canvas.width = width;
      canvas.height = height;
      ctx.drawImage(img, 0, 0, width, height);
      
      // Compress to 70% quality
      resolve(canvas.toDataURL('image/jpeg', 0.7));
    };
    img.src = base64Image;
  });
};

// Use before upload
const compressedImage = await compressImage(formData.selfie);
formDataToSend.append('image', compressedImage);
```

---

## Monitoring

### View Execution Duration

**CloudWatch Logs:**
```
START RequestId: xxx
2024-01-17 12:34:56 INFO Lambda invoked - Request ID: xxx
2024-01-17 12:35:01 INFO Successfully uploaded visitor image: visitors/20240117123456.jpg
2024-01-17 12:35:03 INFO Response status: 201
END RequestId: xxx
REPORT RequestId: xxx Duration: 7234.56 ms  Billed Duration: 7235 ms Memory Size: 1024 MB Max Memory Used: 245 MB
```

**Look for:**
- `Duration: X ms` - Should be < 30000 ms (30 seconds)
- `Max Memory Used` - Should be < 1024 MB

---

## Troubleshooting

### Error: "Task timed out after 120.00 seconds"

**Cause:** Lambda is still timing out even with 120s limit

**Solutions:**
1. Add VPC Endpoint for S3 (see above)
2. Check database connection latency
3. Disable SMS temporarily to isolate issue
4. Make endpoint async (process upload in background)

### Error: "Endpoint request timed out" (still 504)

**Cause:** API Gateway 29-second limit

**Solutions:**
1. Make endpoint async:
   ```python
   # Return immediately
   return {"status": "processing", "visitor_id": visitor.id}
   
   # Process in background lambda
   lambda_client.invoke(
       FunctionName='image-processor',
       InvocationType='Event',  # Async
       Payload=json.dumps({...})
   )
   ```

2. Use polling:
   ```typescript
   // Frontend polls for completion
   const checkStatus = async (visitorId: string) => {
       const response = await fetch(`/api/visitors/${visitorId}/status`);
       if (response.data.image_uploaded) {
           // Complete
       } else {
           // Poll again in 2 seconds
           setTimeout(() => checkStatus(visitorId), 2000);
       }
   };
   ```

### Error: "Unable to import module 'lambda_handler'"

**Cause:** Deployment package missing files

**Solution:**
```powershell
# Ensure all files are included
cd "E:\Visitor Module\backend"

# List what's being zipped
Get-ChildItem -Recurse

# Recreate zip with correct structure
Compress-Archive -Path app,lambda_handler.py,*.txt -DestinationPath deployment.zip -Force
```

---

## Summary

**Minimum Required Steps:**
1. ✅ Update Lambda timeout to 120s (AWS Console)
2. ✅ Update Lambda memory to 1024 MB (AWS Console)
3. ✅ Redeploy code with S3 timeout fixes

**Recommended Additional Steps:**
4. Create VPC Endpoint for S3 (huge performance boost)
5. Compress images on frontend (reduce upload time)
6. Enable CloudWatch Insights (better monitoring)

**Expected Result:**
- No more 504 errors
- Form submission completes in 10-20 seconds
- Reliable even with large images (3-5 MB)
