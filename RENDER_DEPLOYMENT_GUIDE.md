# Render Deployment Guide

## ✅ Quick Fix for "can't open file main.py" Error

The error occurs because Render is trying to run `python main.py`, but your FastAPI app is at `app/main.py`.

---

## 🔧 Solution: Update Start Command in Render

### Option 1: Using Render Dashboard (Recommended)

1. **Go to your Render service dashboard**
2. **Click on "Settings"** tab
3. **Scroll to "Start Command"**
4. **Change it to:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. **Save changes**
6. **Redeploy**

### Option 2: Using render.yaml (If you have one)

I've created `render.yaml` for you. If Render detects it, it will use these settings automatically.

---

## 📋 Complete Render Configuration

### Required Settings in Render Dashboard:

#### 1. **Build Command:**
```bash
pip install -r requirements.txt
```

#### 2. **Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 3. **Python Version:**
- Set to: `3.11.0` or `3.11`

#### 4. **Root Directory:**
- Leave empty (default) or set to: `backend` (if your repo root is parent folder)

---

## 🔑 Environment Variables to Set in Render

Go to Render Dashboard → Your Service → Environment → Add the following:

### Required:
```
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET=your-secret-key-here
```

### Optional (but recommended):
```
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### AWS (if using S3):
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1
AWS_S3_BUCKET_NAME=your-bucket-name
```

### Twilio (if using SMS):
```
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-phone-number
TWILIO_ENABLED=true
TWILIO_SMS_ENABLED=true
```

### CORS (if needed):
```
API_CORS_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
```

---

## 📁 Project Structure

Your project structure should be:
```
backend/
├── app/
│   ├── main.py          ← FastAPI app is here
│   ├── core/
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   └── services/
├── requirements.txt
├── render.yaml          ← I created this for you
└── .env                 ← Not uploaded to Render (use Environment Variables instead)
```

---

## ✅ Verification Steps

After updating the start command:

1. **Check Build Logs:**
   - Should see: `Successfully installed fastapi...`
   - Should see: All packages installing correctly

2. **Check Runtime Logs:**
   - Should see: `INFO:     Started server process`
   - Should see: `INFO:     Uvicorn running on http://0.0.0.0:PORT`
   - Should see: `Application startup complete`

3. **Test Health Endpoint:**
   - Visit: `https://your-service.onrender.com/docs`
   - Should see FastAPI docs page

---

## 🚨 Common Issues & Fixes

### Issue 1: "ModuleNotFoundError: No module named 'app'"
**Fix:** Make sure Root Directory in Render is set correctly (usually empty or `backend`)

### Issue 2: "Port already in use"
**Fix:** Use `$PORT` environment variable (already in the start command)

### Issue 3: "Database connection failed"
**Fix:** 
- Check `DATABASE_URL` is set correctly
- Format: `postgresql://user:password@host:5432/dbname`
- Make sure PostgreSQL service is running in Render

### Issue 4: "Import errors"
**Fix:**
- Check `requirements.txt` has all dependencies
- Verify build completed successfully
- Check build logs for any failed installations

---

## 📝 Quick Reference

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Build Command:**
```bash
pip install -r requirements.txt
```

**Python Version:**
```
3.11.0
```

---

## 🎯 Next Steps

1. ✅ Update Start Command in Render dashboard
2. ✅ Set all Environment Variables
3. ✅ Save and redeploy
4. ✅ Check logs for success
5. ✅ Test your API endpoints

Your app should now deploy successfully on Render! 🚀
