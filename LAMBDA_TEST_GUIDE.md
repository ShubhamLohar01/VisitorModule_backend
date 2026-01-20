# Lambda Function Testing Guide

## Testing Your Lambda Function in AWS Console

After deploying your Lambda function, follow these steps to test it:

### Step 1: Navigate to Lambda Function
1. Go to AWS Lambda Console
2. Select your deployed function
3. Click on the **"Test"** tab

### Step 2: Create Test Events

Use these test events from `lambda-test-events.json`:

#### 🟢 Test 1: Health Check (START HERE)
**Event Name:** `test-health`
```json
{
  "resource": "/health",
  "path": "/health",
  "httpMethod": "GET",
  "headers": {
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "queryStringParameters": null,
  "pathParameters": null,
  "body": null,
  "isBase64Encoded": false,
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "test-api",
    "http": {
      "method": "GET",
      "path": "/health",
      "protocol": "HTTP/1.1"
    },
    "stage": "test"
  }
}
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": "{\"status\":\"healthy\",\"service\":\"visitor-management-api\"}"
}
```

---

#### 🟢 Test 2: Root Endpoint
**Event Name:** `test-root`
```json
{
  "resource": "/",
  "path": "/",
  "httpMethod": "GET",
  "headers": {
    "Accept": "application/json"
  },
  "queryStringParameters": null,
  "pathParameters": null,
  "body": null,
  "isBase64Encoded": false,
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "test-api",
    "http": {
      "method": "GET",
      "path": "/",
      "protocol": "HTTP/1.1"
    },
    "stage": "test"
  }
}
```

---

#### 🟢 Test 3: API Documentation
**Event Name:** `test-docs`
```json
{
  "resource": "/docs",
  "path": "/docs",
  "httpMethod": "GET",
  "headers": {
    "Accept": "text/html"
  },
  "queryStringParameters": null,
  "pathParameters": null,
  "body": null,
  "isBase64Encoded": false,
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "test-api",
    "http": {
      "method": "GET",
      "path": "/docs",
      "protocol": "HTTP/1.1"
    },
    "stage": "test"
  }
}
```

---

#### 🟢 Test 4: CORS Preflight
**Event Name:** `test-cors`
```json
{
  "resource": "/api/v1/appointments",
  "path": "/api/v1/appointments",
  "httpMethod": "OPTIONS",
  "headers": {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
    "Origin": "http://localhost:3000"
  },
  "queryStringParameters": null,
  "pathParameters": null,
  "body": null,
  "isBase64Encoded": false,
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "test-api",
    "http": {
      "method": "OPTIONS",
      "path": "/api/v1/appointments",
      "protocol": "HTTP/1.1"
    },
    "stage": "test"
  }
}
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
  }
}
```

---

### Step 3: How to Create a Test Event in AWS Console

1. Click **"Test"** tab in Lambda function
2. Click **"Create new event"**
3. Select **"API Gateway AWS Proxy"** template (optional)
4. Give it a name (e.g., `test-health`)
5. Paste the JSON event from above
6. Click **"Save"**
7. Click **"Test"** button

### Step 4: Understanding Test Results

#### ✅ Successful Response
```json
{
  "statusCode": 200,
  "headers": {...},
  "body": "..."
}
```

#### ❌ Common Errors

**1. Module Import Error**
```
"errorMessage": "Unable to import module 'lambda_handler': No module named 'mangum'"
```
**Solution:** Check that your deployment package includes all dependencies

**2. Database Connection Error**
```
"errorMessage": "could not connect to server: Connection refused"
```
**Solution:** Set environment variables for DATABASE_URL

**3. Timeout Error**
```
"errorMessage": "Task timed out after 3.00 seconds"
```
**Solution:** Increase Lambda timeout to 30+ seconds

---

### Environment Variables to Set

Go to **Configuration > Environment variables** and add:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
JWT_SECRET_KEY=your_secret_key
ENVIRONMENT=production
```

---

### Quick Test Checklist

- [ ] Deploy lambda-deployment-complete.zip
- [ ] Set Runtime to Python 3.11
- [ ] Set Handler to lambda_handler.lambda_handler
- [ ] Set Memory to 1024 MB
- [ ] Set Timeout to 30 seconds
- [ ] Add Environment Variables
- [ ] Create test event for /health
- [ ] Run test - should return 200 OK
- [ ] Check CloudWatch Logs for any errors

---

### Monitoring Test Results

**View Logs:**
1. Go to **Monitor** tab
2. Click **"View CloudWatch logs"**
3. Check latest log stream for detailed output

**Key Things to Check:**
- Cold start time (first invocation)
- Memory usage
- Duration
- Any import errors
- Database connection status

---

### Next Steps After Successful Test

1. ✅ Create API Gateway
2. ✅ Link Lambda to API Gateway
3. ✅ Deploy API Gateway
4. ✅ Test via public URL
5. ✅ Update frontend with API URL
