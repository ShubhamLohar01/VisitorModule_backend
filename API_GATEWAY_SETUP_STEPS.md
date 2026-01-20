# API Gateway Setup - Steps 4 Onwards

## **Step 4: Create Catch-All Proxy Resource**
1. After creating the API, you'll see the **Resources** page with just "/"
2. Click **"Actions"** dropdown → Select **"Create Resource"**
3. In the "New Child Resource" form:
   - ✅ **Check the box**: "Configure as proxy resource"
   - **Resource Name**: Will auto-fill as `proxy`
   - **Resource Path**: Will show `{proxy+}` (this catches all paths)
   - ✅ **Check the box**: "Enable API Gateway CORS"
4. Click **"Create Resource"** button

---

## **Step 5: Setup Lambda Integration for Proxy**
1. After creating the resource, you'll see the "Setup" page
2. Configure the following:
   - **Integration type**: ✅ Select "Lambda Function"
   - ✅ **Check**: "Use Lambda Proxy integration"
   - **Lambda Region**: `ap-south-1`
   - **Lambda Function**: Type `visitor-management-api` (it should autocomplete)
   - Leave other settings as default
3. Click **"Save"** button
4. **IMPORTANT**: A popup will ask: "Add Permission to Lambda Function"
   - Click **"OK"** to allow API Gateway to invoke your Lambda

---

## **Step 6: Create Root (/) Method**
1. In the left sidebar under "Resources", click on **"/"** (the root, NOT {proxy+})
2. Click **"Actions"** → **"Create Method"**
3. You'll see a small dropdown appear under "/"
4. Select **"ANY"** from the dropdown
5. Click the **checkmark (✓)** next to it
6. Configure the method:
   - **Integration type**: Lambda Function
   - ✅ **Check**: "Use Lambda Proxy integration"
   - **Lambda Region**: `ap-south-1`
   - **Lambda Function**: `visitor-management-api`
7. Click **"Save"**
8. Click **"OK"** when prompted for permissions

---

## **Step 7: Enable CORS (Critical for Frontend)**

### For Root Resource:
1. Click on **"/"** in the resources tree
2. Click **"Actions"** → **"Enable CORS"**
3. You'll see CORS configuration page:
   - **Access-Control-Allow-Methods**: Select ALL or keep defaults
   - **Access-Control-Allow-Headers**: Keep default or add: `Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token`
   - **Access-Control-Allow-Origin**: Keep as `*` or change to `http://localhost:3000` for stricter security
4. Click **"Enable CORS and replace existing CORS headers"**
5. Click **"Yes, replace existing values"** in confirmation popup

### For Proxy Resource:
1. Click on **"/{proxy+}"** in the resources tree
2. Repeat the same CORS steps above

---

## **Step 8: Deploy API**
1. Click **"Actions"** dropdown → **"Deploy API"**
2. In the "Deploy API" dialog:
   - **Deployment stage**: Select **[New Stage]**
   - **Stage name**: Type `prod`
   - **Stage description**: Type `Production environment for visitor management`
   - **Deployment description**: Type `Initial deployment`
3. Click **"Deploy"** button

---

## **Step 9: Get Your New API URL**
1. After deployment, you'll be redirected to the **Stage Editor**
2. At the very top, you'll see:
   ```
   Invoke URL: https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/prod
   ```
3. **COPY THIS URL** - This is your new API endpoint!
4. Save it somewhere safe

---

## **Step 10: Test the New API Gateway**

### Open PowerShell and run these tests:

```powershell
# Replace XXXXXXXXXX with your actual API Gateway ID
$API_URL = "https://XXXXXXXXXX.execute-api.ap-south-1.amazonaws.com/prod"

# Test 1: Root endpoint (should return API info)
Write-Host "`nTesting Root Endpoint..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$API_URL/" -Method GET

# Test 2: Health endpoint
Write-Host "`nTesting Health Endpoint..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$API_URL/health" -Method GET

# Test 3: Docs endpoint
Write-Host "`nTesting Docs Endpoint..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$API_URL/docs" -Method GET

# Test 4: Visitors endpoint (will need auth)
Write-Host "`nTesting Visitors Endpoint..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$API_URL/api/visitors/" -Method GET
```

### Expected Results:
- ✅ **Root (/)**: Should return 200 OK with API info
- ❌ **Health**: May fail with 500 if database not configured (VPC issue)
- ❌ **Docs**: May fail with 500 if database not configured
- ❌ **Visitors**: Will fail with 401/403 (authentication required)

---

## **Step 11: Configure Lambda Environment Variables**

**CRITICAL**: Before your API will work fully, add these environment variables:

1. Go to **Lambda Console** → Find `visitor-management-api`
2. Click **Configuration** tab → **Environment variables**
3. Click **"Edit"**
4. Add these variables:

```plaintext
DATABASE_URL = postgresql://wmsadmin:Candorfoods@wms-postgres-db.cpis084golp7.ap-south-1.rds.amazonaws.com:5432/warehouse_db

JWT_SECRET = your-jwt-secret-key-here

JWT_ALGORITHM = HS256

TWILIO_ACCOUNT_SID = your-twilio-account-sid

TWILIO_AUTH_TOKEN = your-twilio-auth-token

AWS_ACCESS_KEY_ID = your-aws-access-key

AWS_SECRET_ACCESS_KEY = your-aws-secret-key

AWS_DEFAULT_REGION = ap-south-1

S3_BUCKET_NAME = your-s3-bucket-name

ENVIRONMENT = production
```

5. Click **"Save"**

---

## **Step 12: Configure Lambda VPC (Required for Database)**

**CRITICAL**: Lambda must be in same VPC as RDS database:

1. Lambda Console → `visitor-management-api` → **Configuration** → **VPC**
2. Click **"Edit"**
3. Select:
   - **VPC**: Choose the VPC where your RDS database `wms-postgres-db` is located
   - **Subnets**: Select at least 2 private subnets in different AZs
   - **Security Groups**: Select a security group that allows:
     - Outbound traffic to RDS on port 5432
     - Outbound traffic to internet (for Twilio, AWS services)
4. Click **"Save"**

**Warning**: This will take a few minutes to configure

---

## **Step 13: Update Frontend Configuration**

Update your frontend `.env.local` file:

```env
NEXT_PUBLIC_API_URL=https://XXXXXXXXXX.execute-api.ap-south-1.amazonaws.com/prod
```

Replace `XXXXXXXXXX` with your actual API Gateway ID.

---

## **Step 14: Final Testing**

After VPC and environment variables are configured:

```powershell
$API_URL = "https://XXXXXXXXXX.execute-api.ap-south-1.amazonaws.com/prod"

# All these should now work:
Invoke-WebRequest -Uri "$API_URL/" -Method GET
Invoke-WebRequest -Uri "$API_URL/health" -Method GET
Invoke-WebRequest -Uri "$API_URL/docs" -Method GET

# Test visitor creation
$body = @{
    visitor_name = "Test Visitor"
    visitor_phone = "+919876543210"
    visitor_email = "test@example.com"
    company = "Test Corp"
    purpose = "Testing"
    host_name = "Test Host"
    host_phone = "+919004464207"
} | ConvertTo-Json

Invoke-WebRequest -Uri "$API_URL/api/visitors/" -Method POST -Body $body -ContentType "application/json"
```

---

## **Troubleshooting**

### If /health returns 500:
- Check Lambda logs in CloudWatch
- Verify DATABASE_URL is correct
- Verify Lambda is in same VPC as RDS
- Check security group allows port 5432

### If you get timeout errors:
- Lambda VPC configuration takes 5-10 minutes
- Wait and try again

### If CORS errors in browser:
- Verify you enabled CORS on both "/" and "/{proxy+}"
- Check CORS headers allow your origin (localhost:3000)

---

## **Summary**

✅ API Gateway created with proxy resource  
✅ Lambda integration configured  
✅ CORS enabled  
✅ API deployed to prod stage  
⏳ Environment variables configured  
⏳ VPC configured for database access  
⏳ Frontend updated with new URL  

**Your API URL**: `https://XXXXXXXXXX.execute-api.ap-south-1.amazonaws.com/prod`
