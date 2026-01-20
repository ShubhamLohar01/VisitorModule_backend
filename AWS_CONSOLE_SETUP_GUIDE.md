# Complete AWS Lambda + API Gateway Setup Guide (AWS Console)

This is a beginner-friendly, step-by-step guide to deploy your backend to AWS Lambda and API Gateway using the AWS Console (no CLI required).

---

## Prerequisites

Before starting, make sure you have:
- ✅ AWS Account (sign up at aws.amazon.com if you don't have one)
- ✅ ZIP file ready: `visitor-management-backend.zip`
- ✅ Database credentials (host, port, name, user, password)
- ✅ Email credentials (SMTP)
- ✅ Twilio credentials (if using SMS)
- ✅ JWT secret key (any random string, minimum 32 characters)

---

## Part 1: Create IAM Role for Lambda

### Step 1.1: Go to IAM Console

1. Log in to AWS Console: https://console.aws.amazon.com
2. In the search bar at the top, type **"IAM"**
3. Click on **"IAM"** service

### Step 1.2: Create Role

1. In the left sidebar, click **"Roles"**
2. Click the orange **"Create role"** button

### Step 1.3: Select Service

1. Under **"Select trusted entity"**, select **"AWS service"**
2. Under **"Use case"**, select **"Lambda"**
3. Click **"Next"**

### Step 1.4: Attach Policies

1. In the search box, type **"AWSLambdaBasicExecutionRole"**
2. Check the box next to **"AWSLambdaBasicExecutionRole"**
3. If you need database access, also search and check:
   - **"AmazonRDSFullAccess"** (for RDS database)
   - **"AmazonS3FullAccess"** (if using S3 for images)
4. Click **"Next"**

### Step 1.5: Name the Role

1. **Role name**: Type `lambda-visitor-management-role`
2. **Description**: (Optional) "Role for Visitor Management Lambda function"
3. Click **"Create role"**

### Step 1.6: Save Role ARN

1. After creation, you'll see the role details
2. **IMPORTANT**: Copy the **"ARN"** (looks like: `arn:aws:iam::123456789012:role/lambda-visitor-management-role`)
3. Save it somewhere - you'll need it later

---

## Part 2: Create Lambda Function

### Step 2.1: Go to Lambda Console

1. In AWS Console search bar, type **"Lambda"**
2. Click on **"Lambda"** service

### Step 2.2: Create Function

1. Click the orange **"Create function"** button

### Step 2.3: Configure Function

1. Select **"Author from scratch"** (should be selected by default)
2. **Function name**: Type `visitor-management-api`
3. **Runtime**: Select **"Python 3.11"** from dropdown
4. **Architecture**: Select **"x86_64"** (default)
5. **Execution role**: 
   - Select **"Use an existing role"**
   - Under **"Existing role"**, select `lambda-visitor-management-role` (the one you created)
6. Click **"Create function"**

### Step 2.4: Upload ZIP File

1. After function is created, scroll down to **"Code source"** section
2. Click **"Upload from"** dropdown button
3. Select **".zip file"**
4. Click **"Upload"** button
5. Browse and select your `visitor-management-backend.zip` file
6. Wait for upload to complete (you'll see a progress bar)
7. Click **"Save"** when upload finishes

### Step 2.5: Configure Handler

1. Scroll up to **"Code"** tab
2. In the **"Runtime settings"** section, click **"Edit"**
3. **Handler**: Change to `lambda_handler.lambda_handler`
   - (It might show `lambda_function.lambda_handler` by default - change it!)
4. Click **"Save"**

### Step 2.6: Set Timeout and Memory

1. Click **"Configuration"** tab (top of page)
2. Click **"General configuration"** in left sidebar
3. Click **"Edit"**
4. **Timeout**: Set to `30` seconds (or more if needed)
5. **Memory**: Set to `512` MB (or more if needed)
6. Click **"Save"**

---

## Part 3: Create and Attach Lambda Layer (CRITICAL)

### Step 3.1: Why You Need a Layer

Your Python application uses external libraries (FastAPI, mangum, boto3, etc.) that are NOT included in the basic Lambda runtime. You must create a **Lambda Layer** with all dependencies.

### Step 3.2: Upload Dependencies Layer

1. Go to **Lambda Console** → **Layers** (in left sidebar)
2. Click **"Create layer"**
3. **Layer configuration**:
   - Name: `visitor-management-dependencies`
   - Description: `Dependencies for Visitor Management System`
   - Upload: Select your `visitor-management-dependencies.zip` file (the one from build-layer.bat)
   - Compatible runtimes: Select **Python 3.11**
   - Compatible architectures: Select **x86_64**
4. Click **"Create"**
5. **IMPORTANT**: Copy the **Layer ARN** that appears

### Step 3.3: Attach Layer to Function

1. Go back to your Lambda function: `visitor-management-api`
2. Click **"Configuration"** tab
3. Click **"Layers"** in left sidebar  
4. Click **"Add a layer"**
5. Select **"Custom layers"**
6. Choose: `visitor-management-dependencies`
7. Select **"Version 1"** (latest)
8. Click **"Add"**

### Step 3.4: Verify Layer is Attached

After adding, you should see:
- Layer name: `visitor-management-dependencies`
- Version: 1
- Size: ~53 MB

**🚨 WITHOUT THIS STEP, YOU WILL GET "No module named 'mangum'" ERRORS!**

---

## Part 4: Configure Environment Variables

### Step 4.1: Add Environment Variables

1. Still in **"Configuration"** tab
2. Click **"Environment variables"** in left sidebar
3. Click **"Edit"**
4. Click **"Add environment variable"** for each variable below

### Step 4.2: Add All Required Variables

Add these one by one (click "Add environment variable" for each):

**Database Variables:**
- **Key**: `DB_HOST` → **Value**: `your-database-host.rds.amazonaws.com`
- **Key**: `DB_PORT` → **Value**: `5432`
- **Key**: `DB_NAME` → **Value**: `your_database_name`
- **Key**: `DB_USER` → **Value**: `your_database_user`
- **Key**: `DB_PASSWORD` → **Value**: `your_database_password`

**JWT Secret:**
- **Key**: `JWT_SECRET` → **Value**: `your-secret-jwt-key-minimum-32-characters-long`

**Environment:**
- **Key**: `ENVIRONMENT` → **Value**: `production`

**Email/SMTP Variables:**
- **Key**: `SMTP_USER` → **Value**: `your-email@gmail.com`
- **Key**: `SMTP_PASSWORD` → **Value**: `your-gmail-app-password`
- **Key**: `SMTP_HOST` → **Value**: `smtp.gmail.com`
- **Key**: `SMTP_PORT` → **Value**: `587`

**Twilio Variables (if using SMS):**
- **Key**: `TWILIO_ACCOUNT_SID` → **Value**: `your-twilio-sid`
- **Key**: `TWILIO_AUTH_TOKEN` → **Value**: `your-twilio-token`
- **Key**: `TWILIO_PHONE_NUMBER` → **Value**: `+1234567890`
- **Key**: `TWILIO_ENABLED` → **Value**: `true`
- **Key**: `TWILIO_SMS_ENABLED` → **Value**: `true`

**AWS Variables:**
- **Key**: `AWS_REGION` → **Value**: `ap-south-1` (or your region)
- **Key**: `AWS_S3_BUCKET_NAME` → **Value**: `your-bucket-name` (if using S3)
- **Key**: `AWS_ACCESS_KEY_ID` → **Value**: `your-access-key` (if using S3)
- **Key**: `AWS_SECRET_ACCESS_KEY` → **Value**: `your-secret-key` (if using S3)

**CORS and URLs:**
- **Key**: `API_CORS_ORIGINS` → **Value**: `*` (or specific frontend URL)
- **Key**: `FRONTEND_URL` → **Value**: `http://localhost:3000` (for local testing)
- **Key**: `DASHBOARD_URL` → **Value**: `http://localhost:3000/dashboard`

5. After adding all variables, click **"Save"**

---

## Part 5: Configure VPC (Only if Database is in VPC)

**Skip this section if your database is publicly accessible.**

### Step 5.1: Configure VPC

1. In **"Configuration"** tab
2. Click **"VPC"** in left sidebar
3. Click **"Edit"**
4. **VPC**: Select your database VPC
5. **Subnets**: Select at least 2 subnets (in different availability zones)
6. **Security groups**: Select security group that allows Lambda to access RDS
7. Click **"Save"**

**Note**: VPC configuration adds cold start delay. Only use if necessary.

---

## Part 6: Test Lambda Function

### Step 6.1: Create Test Event

1. Click **"Test"** tab (top of page)
2. Click **"Create new test event"** or **"Create event"**
3. Select **"Create new event"**
4. **Event name**: Type `test-health`
5. **Event JSON**: Replace with this:

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

6. Click **"Save"**

### Step 6.2: Run Test

1. Click **"Test"** button
2. Wait for execution to complete
3. Check the response:
   - **Status**: Should show "Succeeded"
   - **Response**: Should show `{"status": "ok", ...}`

**If you see "No module named 'mangum'" error:**
- ❌ **Layer not attached** - Go back to Part 3 and attach the dependencies layer
- ❌ **Wrong layer** - Make sure you uploaded the correct `visitor-management-dependencies.zip`
- ❌ **Architecture mismatch** - Verify layer is x86_64 and function is x86_64

**If you see other errors:**
- Check CloudWatch logs (click "View logs in CloudWatch")
- Verify environment variables are correct
- Check handler is set to `lambda_handler.lambda_handler`

---

## Part 7: Create API Gateway

### Step 7.1: Go to API Gateway Console

1. In AWS Console search bar, type **"API Gateway"**
2. Click on **"API Gateway"** service

### Step 7.2: Choose API Type

**For your visitor management system, use HTTP API (recommended):**

#### Option A: HTTP API (Recommended - Faster & Cheaper)

1. Click **"Create API"** button  
2. Under **"HTTP API"**, click **"Build"** button
3. **Add integrations**:
   - Click **"Add integration"**
   - Select **"Lambda"**  
   - **AWS Region**: Select your region (e.g., `ap-south-1`)
   - **Lambda function**: Choose `visitor-management-api`
   - **Version**: Select **"2.0"**
4. **API name**: Type `visitor-management-api`
5. Click **"Next"**
6. **Configure routes**: Should auto-create `ANY /{proxy+}` - Click **"Next"**  
7. **Configure stages**: Use `$default` stage - Click **"Next"**
8. **Review and create**: Click **"Create"**

#### Option B: REST API (More Features, Higher Cost)

1. Click **"Create API"** button
2. Under **"REST API"**, click **"Build"** button  
3. Follow the detailed REST API steps below if you need advanced features

### Step 7.3: Configure CORS (HTTP API)

For HTTP API:
1. In your API, click **"CORS"** in left sidebar
2. **Access-Control-Allow-Origin**: `*` (or `http://localhost:3000`)  
3. **Access-Control-Allow-Methods**: `*`
4. **Access-Control-Allow-Headers**: `content-type,authorization`
5. Click **"Save"**

### Step 7.4: Get API Endpoint URL

1. Click **"Stages"** in left sidebar
2. Click on `$default` (or your stage name)
3. **Copy the "Invoke URL"** 
   - Example: `https://abc123xyz.execute-api.ap-south-1.amazonaws.com`
4. **Save this URL** - this is your API endpoint!

---

#
---

## Part 8: Test API Gateway

### Step 8.1: Test Health Endpoint

1. Open a new browser tab
2. Go to: `https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod/health`
   - Replace `YOUR_API_ID` with your actual API ID
3. You should see a JSON response like:
   ```json
   {
     "status": "ok",
     "message": "Visitor Management System API is running",
     "version": "1.0.0"
   }
   ```

### Step 7.2: Test Root Endpoint

1. Go to: `https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod/`
2. You should see API information

**If you get errors:**
- Check Lambda function logs in CloudWatch
- Verify Lambda function is working (test it again)
- Check API Gateway method configuration

---

## Part 9: Connect Frontend to API Gateway

### Step 9.1: Find Your API Config File

In your frontend project, find where the API URL is configured. Common locations:
- `frontend/lib/api.ts`
- `frontend/lib/api-config.ts`
- `frontend/lib/constants.ts`
- `frontend/.env.local`

### Step 8.2: Update API URL

Replace the localhost API URL with your API Gateway URL:

**Before:**
```typescript
const API_BASE_URL = "http://localhost:8000";
// or
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

**After:**
```typescript
const API_BASE_URL = "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod";
// or for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod";
```

### Step 8.3: Update Environment Variables (if using .env)

If you have a `.env.local` file in frontend:

```env
NEXT_PUBLIC_API_URL=https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod
```

### Step 8.4: Restart Frontend

1. Stop your frontend dev server (Ctrl+C)
2. Restart it:
   ```bash
   npm run dev
   ```

---

## Part 10: Test with Frontend

### Step 10.1: Test Login

1. Open your frontend: `http://localhost:3000`
2. Go to login page
3. Try to log in with your credentials
4. Check browser console (F12) for any errors
5. Check Network tab to see API calls

### Step 9.2: Test API Calls

1. Open browser DevTools (F12)
2. Go to **"Network"** tab
3. Try different features:
   - Login
   - View dashboard
   - Create visitor
   - Approve/reject requests
4. Check if API calls are going to your API Gateway URL
5. Check responses for errors

### Step 9.3: Common Issues

**CORS Error:**
- Go back to API Gateway → Enable CORS again
- Make sure `Access-Control-Allow-Origin` includes `http://localhost:3000`

**401 Unauthorized:**
- Check if JWT_SECRET is set correctly
- Verify login endpoint is working

**500 Internal Server Error:**
- Check Lambda function logs in CloudWatch
- Verify all environment variables are set
- Check database connection

**502 Bad Gateway:**
- Lambda function might have an error
- Check CloudWatch logs
- Test Lambda function directly

---

## Part 11: View Logs and Debug

### Step 11.1: View Lambda Logs

1. Go to Lambda Console
2. Click on your function: `visitor-management-api`
3. Click **"Monitor"** tab
4. Click **"View CloudWatch logs"**
5. Click on the latest log stream
6. You'll see all function logs and errors

### Step 10.2: View API Gateway Logs

1. Go to API Gateway Console
2. Select your API
3. Click **"Stages"** in left sidebar
4. Click on your stage (e.g., `prod`)
5. Click **"Logs / Tracing"** tab
6. Enable logging if needed

---

## Quick Reference

### Important URLs to Save:

1. **Lambda Function**: 
   - Console: https://console.aws.amazon.com/lambda
   - Function: `visitor-management-api`

2. **API Gateway**: 
   - Console: https://console.aws.amazon.com/apigateway
   - API: `visitor-management-api`
   - Endpoint: `https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod`

3. **CloudWatch Logs**: 
   - Console: https://console.aws.amazon.com/cloudwatch
   - Log Group: `/aws/lambda/visitor-management-api`

### Handler Configuration:
- **Handler**: `lambda_handler.lambda_handler`
- **Runtime**: Python 3.11
- **Timeout**: 30 seconds (or more)
- **Memory**: 512 MB (or more)

### Environment Variables Checklist:
- ✅ DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- ✅ JWT_SECRET
- ✅ ENVIRONMENT
- ✅ SMTP_USER, SMTP_PASSWORD
- ✅ TWILIO_* (if using SMS)
- ✅ AWS_REGION
- ✅ API_CORS_ORIGINS
- ✅ FRONTEND_URL, DASHBOARD_URL

---

## Troubleshooting

### Issue: "Unable to import module 'lambda_function'"
**Solution**: Change handler to `lambda_handler.lambda_handler` in Lambda configuration

### Issue: "ModuleNotFoundError: No module named 'mangum'"
**Solution**: 
1. ❌ **MOST COMMON**: Dependencies layer not attached - Go to Lambda → Configuration → Layers → Add layer
2. ❌ **Wrong zip file**: Make sure you uploaded `visitor-management-dependencies.zip` (not the code package)
3. ❌ **Architecture mismatch**: Verify both layer and function are x86_64
4. ❌ **Runtime mismatch**: Verify both layer and function are Python 3.11
5. ❌ **Layer not built correctly**: Rebuild layer using `build-layer.bat`

### Issue: CORS errors in browser
**Solution**: 
1. Enable CORS in API Gateway
2. Set `API_CORS_ORIGINS` environment variable
3. Make sure frontend URL is in allowed origins

### Issue: Database connection timeout
**Solution**:
1. Check VPC configuration if database is in VPC
2. Verify security group rules
3. Check database credentials

### Issue: 502 Bad Gateway
**Solution**:
1. Check Lambda function logs
2. Test Lambda function directly
3. Verify handler is correct

---

## Next Steps

After successful setup:
1. ✅ Test all API endpoints from frontend
2. ✅ Monitor CloudWatch logs for errors
3. ✅ Set up CloudWatch alarms (optional)
4. ✅ Consider using custom domain (optional)
5. ✅ Set up CI/CD for automatic deployments (optional)

---

## Summary

You've successfully:
1. ✅ Created IAM role for Lambda
2. ✅ Created Lambda function
3. ✅ Uploaded your ZIP file
4. ✅ Configured environment variables
5. ✅ Created API Gateway
6. ✅ Connected API Gateway to Lambda
7. ✅ Enabled CORS
8. ✅ Deployed API
9. ✅ Connected frontend to API Gateway
10. ✅ Tested the integration

Your API is now live and accessible from your localhost frontend! 🎉
