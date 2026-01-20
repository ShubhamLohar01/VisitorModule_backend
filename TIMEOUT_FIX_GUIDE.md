# 504 Timeout Error - Diagnosis & Fix Guide

## Error Overview
```
API request failed with status 504: {"message": "Endpoint request timed out"}
```

This error occurs when your Lambda function takes longer than the configured timeout to respond.

---

## Root Causes Identified

### 1. **Lambda Timeout Configuration**
- **Previous:** 30 seconds (serverless.yml), 60 seconds (template.yaml)
- **Issue:** Not enough time for:
  - Database operations (2-5 sec)
  - S3 image upload (5-20 sec for large images)
  - SMS sending (2-5 sec)
  - Approver lookup queries (1-3 sec)
  
### 2. **S3 Upload Bottleneck**
- **Previous S3 Timeouts:**
  - `connect_timeout: 5 seconds`
  - `read_timeout: 10 seconds`
- **Issue:** Too aggressive for:
  - Large selfie images (2-5 MB)
  - VPC NAT Gateway latency
  - Network variations

### 3. **VPC Configuration Impact**
Your Lambda runs in a VPC, which adds latency:
- ✅ **Good:** Fast database access (same VPC)
- ⚠️ **Slow:** S3 access requires NAT Gateway or VPC Endpoint
- ⚠️ **Slow:** External API calls (SMS)

---

## Fixes Applied

### Fix 1: Increased Lambda Timeout

**File: `serverless.yml`**
```yaml
provider:
  timeout: 120  # Increased from 30 to 120 seconds
  memorySize: 1024  # Increased from 512 MB for better CPU
```

**File: `template.yaml`**
```yaml
Globals:
  Function:
    Timeout: 120  # Increased from 60 to 120 seconds
```

### Fix 2: Relaxed S3 Upload Timeouts

**File: `app/services/s3_service.py`**
```python
config=BotoConfig(
    connect_timeout=10,  # Increased from 5
    read_timeout=60,     # Increased from 10
    retries={'max_attempts': 3}  # Increased from 2
)
```

### Fix 3: API Gateway Timeout (Manual AWS Console Fix Required)

⚠️ **Important:** API Gateway has a hard limit of **29 seconds** for integration timeout.

If your Lambda takes longer than 29 seconds, API Gateway will return 504 even if Lambda continues running.

**To fix in AWS Console:**
1. Go to **API Gateway Console**
2. Select your API
3. Click on **Resources** → Select your endpoint
4. Click **Integration Request**
5. Expand **Advanced Settings**
6. Set **Integration Timeout**: Maximum is **29000 milliseconds (29 seconds)**

**Alternative Solution:** Make the endpoint asynchronous:
- Return immediate response to frontend
- Process upload in background
- Poll for completion or use WebSocket for updates

---

## Deployment Steps

### Option 1: Using Serverless Framework
```powershell
cd "E:\Visitor Module\backend"

# Deploy with updated configuration
serverless deploy --stage dev

# Or production
serverless deploy --stage prod
```

### Option 2: Using AWS Console (Manual Update)

1. **Update Lambda Configuration:**
   - Go to **Lambda Console**
   - Select your function: `visitor-management-api`
   - Click **Configuration** → **General configuration**
   - Click **Edit**
   - Set **Timeout**: `2 min 0 sec`
   - Set **Memory**: `1024 MB`
   - Click **Save**

2. **Redeploy Lambda Code with S3 fixes:**
   ```powershell
   # Package with updated S3 service
   cd "E:\Visitor Module\backend"
   
   # Create deployment package
   .\build-deploy.ps1
   
   # Upload to Lambda via AWS Console or CLI
   ```

---

## Additional Optimizations

### 1. Add VPC Endpoint for S3 (Recommended)

VPC Endpoints eliminate NAT Gateway latency for S3 access.

**In AWS Console:**
1. Go to **VPC Console**
2. Click **Endpoints** → **Create Endpoint**
3. Select **AWS services**
4. Search for `s3` and select `com.amazonaws.ap-south-1.s3` (Gateway type)
5. Select your VPC
6. Select your route tables
7. Click **Create**

**Cost:** FREE for Gateway endpoints
**Performance:** Reduces S3 latency by 50-80%

### 2. Make Background Tasks Truly Async

Current code attempts background SMS but may still block:

**File: `app/routers/visitor.py`**

Current approach uses `BackgroundTasks` which still blocks the response until Lambda finishes.

**Better approach:** Use AWS SQS or SNS for true async:
```python
# Instead of background_tasks.add_task()
# Send message to SQS queue
sqs_client.send_message(
    QueueUrl=settings.sms_queue_url,
    MessageBody=json.dumps({
        'visitor_id': visitor_id,
        'approver': person_to_meet,
        # ... other data
    })
)
```

Then have a separate Lambda consume the SQS queue for SMS sending.

### 3. Optimize Database Connection Pool

**File: `app/core/database.py`**

Already optimized with:
- `pool_pre_ping=True` ✅
- `pool_size=5` ✅
- `pool_recycle=300` ✅
- `connect_timeout=5` ✅

### 4. Image Compression Before Upload

Reduce image size on frontend before uploading:

**File: `frontend/components/visitor-form.tsx` or similar**
```typescript
// Add image compression
const compressImage = async (base64: string): Promise<string> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d')!;
      
      // Max dimensions
      const maxWidth = 800;
      const maxHeight = 800;
      
      let width = img.width;
      let height = img.height;
      
      if (width > height) {
        if (width > maxWidth) {
          height *= maxWidth / width;
          width = maxWidth;
        }
      } else {
        if (height > maxHeight) {
          width *= maxHeight / height;
          height = maxHeight;
        }
      }
      
      canvas.width = width;
      canvas.height = height;
      ctx.drawImage(img, 0, 0, width, height);
      
      resolve(canvas.toDataURL('image/jpeg', 0.7)); // 70% quality
    };
    img.src = base64;
  });
};
```

---

## Monitoring & Debugging

### Check Lambda Execution Time

**AWS Console:**
1. Go to **Lambda Console**
2. Select your function
3. Click **Monitor** tab
4. Click **View logs in CloudWatch**
5. Look for execution duration logs

**Expected durations:**
- Fast request (no SMS): 3-8 seconds
- Normal request (with SMS): 8-15 seconds
- Slow request (network issues): 15-30 seconds

### Enable Lambda Insights

For detailed performance metrics:

```yaml
# In serverless.yml
provider:
  layers:
    - arn:aws:lambda:ap-south-1:580247275435:layer:LambdaInsightsExtension:14
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: '*'
```

---

## Verification Steps

After deployment:

1. **Test the endpoint:**
   ```powershell
   # Use detailed-api-test.py
   python detailed-api-test.py
   ```

2. **Monitor CloudWatch:**
   - Check execution duration
   - Look for timeout errors
   - Verify S3 upload times

3. **Check API Gateway logs:**
   - Integration timeout should not occur
   - Response should be < 29 seconds

---

## Fallback: If Still Timing Out

If you still experience timeouts after all fixes:

### Option A: Return Immediate Response

```python
@router.post("/check-in-with-image")
async def check_in_visitor_with_image(...):
    # Create visitor record immediately
    new_visitor = Visitor(...)
    db.add(new_visitor)
    db.commit()
    
    # Queue image upload and SMS for background
    # (use SQS or SNS)
    
    # Return immediately
    return {
        "visitor": {...},
        "message": "Check-in initiated. Image upload in progress."
    }
```

### Option B: Use Asynchronous Lambda

Invoke a second Lambda for heavy operations:

```python
# In visitor endpoint
lambda_client.invoke(
    FunctionName='visitor-image-processor',
    InvocationType='Event',  # Async invocation
    Payload=json.dumps({
        'visitor_id': visitor_id,
        'image_data': base64_image
    })
)
```

---

## Summary

✅ **Completed Fixes:**
- Increased Lambda timeout: 30s → 120s
- Increased memory: 512MB → 1024MB  
- Relaxed S3 timeouts: 5s/10s → 10s/60s
- Increased S3 retry attempts: 2 → 3

⚠️ **Manual Actions Needed:**
1. Redeploy Lambda with `serverless deploy`
2. (Optional) Create VPC Endpoint for S3
3. (Optional) Configure API Gateway timeout if < 29s needed

🎯 **Expected Result:**
- Timeout errors eliminated
- Check-in completes in 10-20 seconds
- Better reliability during network variations