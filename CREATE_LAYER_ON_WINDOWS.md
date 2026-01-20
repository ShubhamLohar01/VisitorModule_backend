# Create Lambda Layer on Windows (Without Linux)

आप Windows पर directly Linux-compatible dependencies download करके Lambda layer बना सकते हैं!

---

## Method 1: PowerShell Script (Recommended) ⭐

### Step 1: Run the Script

PowerShell में यह command run करें:

```powershell
cd "E:\Visitor Module\backend"
.\create_lambda_layer_windows.ps1
```

**Note:** अगर script run नहीं हो रहा, तो execution policy change करें:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Wait for Download

Script automatically:
- ✅ Linux-compatible wheels download करेगा
- ✅ सही folder structure बनाएगा
- ✅ Unnecessary files clean करेगा
- ✅ ZIP file create करेगा

**Time:** 5-10 minutes

---

## Method 2: Manual Commands

अगर script काम नहीं करे, तो manually commands run करें:

### Step 1: Create Folder Structure

```powershell
cd "E:\Visitor Module\backend"
mkdir -p lambda-layer\python\lib\python3.11\site-packages
cd lambda-layer\python\lib\python3.11\site-packages
```

### Step 2: Download Linux Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Download Linux-compatible wheels
python -m pip install `
    --platform manylinux2014_x86_64 `
    --target . `
    --only-binary :all: `
    --no-cache-dir `
    --python-version 3.11 `
    --implementation cp `
    --abi cp311 `
    -r ..\..\..\..\..\requirements.txt
```

### Step 3: Clean Up

```powershell
# Remove __pycache__
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove .pyc files
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
```

### Step 4: Create ZIP

```powershell
# Go back to backend folder
cd "E:\Visitor Module\backend"

# Create ZIP
Compress-Archive -Path lambda-layer\python -DestinationPath layer.zip -Force

# Check size
(Get-Item layer.zip).Length / 1MB
```

---

## Method 3: Using Batch File

```cmd
cd "E:\Visitor Module\backend"
create_lambda_layer_windows.bat
```

---

## Important Notes

### ✅ Advantages:
- Windows पर directly काम करता है
- Linux environment की जरूरत नहीं
- Pre-built wheels use करता है (GLIBC compatible)

### ⚠️ Limitations:
- कुछ packages के लिए wheels available नहीं हो सकते
- अगर `--only-binary` fail हो, तो EC2 use करना होगा

### 🔧 If It Fails:

अगर कुछ packages install नहीं हो रहे, तो:

1. **Check error message** - कौन सा package fail हो रहा है
2. **Try without `--only-binary`** (लेकिन यह Windows पर build करने की कोशिश करेगा, जो fail होगा)
3. **Use EC2** (Option 3 in CREATE_LAYER_WITHOUT_DOCKER.md) - सबसे reliable method

---

## After Creating layer.zip

1. **If file < 50 MB:**
   - Lambda Console → Layers → Create layer
   - Upload `layer.zip` directly

2. **If file > 50 MB:**
   - Upload to S3 first:
     ```powershell
     aws s3 cp layer.zip s3://your-bucket-name/layer.zip
     ```
   - Lambda Console → Layers → Create layer
   - Select "Upload from S3"
   - Enter S3 URL

---

## Troubleshooting

### Error: "No matching distribution found"
**Solution:** उस package के लिए Linux wheel available नहीं है। EC2 use करें।

### Error: "Platform not supported"
**Solution:** `manylinux2014_x86_64` के बजाय `manylinux1_x86_64` try करें:
```powershell
python -m pip install --platform manylinux1_x86_64 ...
```

### File too large
**Solution:** More cleanup करें:
```powershell
# Remove test files
Get-ChildItem -Path . -Recurse -Directory -Filter "tests" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter "test" | Remove-Item -Recurse -Force
```

---

## Success!

अगर script successfully complete हो जाए, तो आपको `layer.zip` file मिलेगी जो AWS Lambda में use कर सकते हैं! 🎉
