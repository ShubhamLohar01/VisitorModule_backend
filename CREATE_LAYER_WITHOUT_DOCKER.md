# Create Lambda Layer Without Docker - 3 Easy Options

Since you don't have Docker, here are 3 alternatives to create a Linux-compatible Lambda layer:

---

## Option 1: AWS CloudShell ⚠️ GLIBC Compatibility Issues

AWS CloudShell is a free Linux environment in your AWS Console. No installation needed!

**⚠️ WARNING:** CloudShell may have GLIBC version mismatches with Lambda runtime, causing errors like `GLIBC_2.28 not found`. If you encounter this error, **use Option 3 (EC2)** instead, which matches Lambda's runtime exactly.

### Step 1: Open AWS CloudShell

1. Log in to AWS Console
2. Click the **CloudShell icon** (terminal icon) in the top navigation bar
3. Wait for CloudShell to open (first time takes 1-2 minutes)

### Step 2: Upload requirements.txt

1. In CloudShell, click the **"Actions"** menu (hamburger icon, top right)
2. Select **"Upload file"**
3. Browse and select your `requirements.txt` file from `E:\Visitor Module\backend\`
4. Click **"Upload"**

### Step 3: Install Python 3.11 (CloudShell has Python 3.9 by default)

CloudShell comes with Python 3.9, but Lambda needs 3.11. Let's install Python 3.11:

```bash
# Check current Python version
python3 --version  # Will show Python 3.9.x

# Check which Linux version CloudShell is using
cat /etc/os-release

# Try to install Python 3.11
# For Amazon Linux 2023:
sudo yum install -y python3.11 python3.11-pip python3.11-devel gcc

# For Amazon Linux 2 (if above fails):
# Python 3.11 might not be available - use Option B below instead
```

**If Python 3.11 installs successfully:**
```bash
# Verify Python 3.11 is installed
python3.11 --version  # Should show Python 3.11.x

# Upgrade pip for Python 3.11
python3.11 -m pip install --upgrade pip setuptools wheel
```

**If Python 3.11 installation fails (common in CloudShell):**

CloudShell often uses Amazon Linux 2 which doesn't have Python 3.11 easily available. You have two options:

**Option A: Use EC2 instead (Recommended)**
- EC2 Amazon Linux 2023 has Python 3.11 pre-installed
- See **Option 3** below in this guide
- This is the most reliable method

**Option B: Build with Python 3.9 but target 3.11 (Advanced)**
This is tricky and may have compatibility issues. Only use if you must:
```bash
# Install packages using pip3 (Python 3.9) but target 3.11 structure
# This requires pip to download Python 3.11 wheels
pip3 install --upgrade pip
pip3 install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir --python-version 3.11 --only-binary :all:
```
**Warning:** This may not work for all packages, especially native extensions like `pydantic-core`.

### Step 4: Create Layer Structure

Now create the layer using Python 3.11:

```bash
# Create folder structure
mkdir -p lambda-layer/python/lib/python3.11/site-packages
cd lambda-layer

# Install dependencies using Python 3.11 (this will take 5-10 minutes)
# CloudShell is already Linux x86_64, so native extensions will build correctly
python3.11 -m pip install --upgrade pip setuptools wheel
python3.11 -m pip install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir

# Verify pydantic-core was installed correctly
ls -la python/lib/python3.11/site-packages/pydantic_core/ | head -20
python3.11 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('SUCCESS: pydantic-core native module found')"

# Reduce layer size by removing unnecessary files
# Remove __pycache__ directories and .pyc files (saves significant space)
find python/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find python/lib/python3.11/site-packages -name "*.pyc" -delete
find python/lib/python3.11/site-packages -name "*.pyo" -delete

# Remove test files and documentation (optional, saves more space)
find python/lib/python3.11/site-packages -type d -name "tests" -exec rm -r {} + 2>/dev/null || true
find python/lib/python3.11/site-packages -type d -name "test" -exec rm -r {} + 2>/dev/null || true
find python/lib/python3.11/site-packages -type d -name "__tests__" -exec rm -r {} + 2>/dev/null || true
find python/lib/python3.11/site-packages -name "*.md" -delete 2>/dev/null || true
find python/lib/python3.11/site-packages -name "*.txt" -not -name "*.dist-info" -exec rm {} + 2>/dev/null || true

# Check size after cleanup
du -sh python/

# Create ZIP file (you're still in lambda-layer directory)
zip -r layer.zip python/

# Check file size
ls -lh layer.zip
```

### Step 5: Upload layer.zip to Lambda

**Option A: If layer.zip is under 50 MB (Direct Upload)**

1. In CloudShell, click **"Actions"** menu
2. Select **"Download file"**
3. Enter: `layer.zip`
4. Click **"Download"**
5. Save it to your backend folder
6. Go to Lambda Console → Layers → Create layer
7. Upload the downloaded `layer.zip` directly

**Option B: If layer.zip is over 50 MB (Use S3 - Recommended)**

Lambda allows up to 250 MB (unzipped) when uploaded via S3:

```bash
# Upload to S3 (replace YOUR-BUCKET-NAME with your bucket name)
aws s3 cp layer.zip s3://YOUR-BUCKET-NAME/lambda-layers/layer.zip

# Or create a bucket first if you don't have one
aws s3 mb s3://lambda-layers-bucket
aws s3 cp layer.zip s3://lambda-layers-bucket/layer.zip
```

Then in Lambda Console:
1. Go to Lambda Console → Layers → Create layer
2. Select **"Upload a file from Amazon S3"**
3. Enter S3 link: `s3://YOUR-BUCKET-NAME/lambda-layers/layer.zip`
4. Select Python 3.11
5. Create layer

**Note:** If you don't have an S3 bucket, you can create one in S3 Console (free tier includes 5 GB).

### Step 6: Create Layer in AWS

1. Go to Lambda Console → Layers
2. Create new layer
3. Upload the downloaded `layer.zip`
4. Select Python 3.11
5. Attach to your Lambda function

**Done!** ✅

### Troubleshooting: pydantic-core Error (if needed)

If you get this error:
```
No module named 'pydantic_core._pydantic_core'
```

**Solution:** Rebuild the layer with these additional steps:

```bash
# Go back to lambda-layer directory
cd lambda-layer

# Remove old installation
rm -rf python/lib/python3.11/site-packages/*

# Install build dependencies (if needed)
sudo yum install -y gcc python3-devel || sudo apt-get install -y gcc python3-dev

# Upgrade pip and install wheel (use python3.11 if installed, otherwise pip3)
python3.11 -m pip install --upgrade pip setuptools wheel 2>/dev/null || pip3 install --upgrade pip setuptools wheel

# Install dependencies again (this ensures native extensions are built correctly)
python3.11 -m pip install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir 2>/dev/null || pip3 install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir

# Verify pydantic-core installation
python3.11 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('SUCCESS: pydantic-core native module found')" 2>/dev/null || python3 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('✅ pydantic-core native module found!')"

# If verification fails, try installing pydantic-core separately
python3.11 -m pip install --upgrade pydantic-core==2.41.5 -t python/lib/python3.11/site-packages/ --no-cache-dir 2>/dev/null || pip3 install --upgrade pydantic-core==2.41.5 -t python/lib/python3.11/site-packages/ --no-cache-dir

# Recreate ZIP
cd ..
rm -f layer.zip
zip -r layer.zip python/

# Re-upload to Lambda Layer
```

**Alternative:** If the above doesn't work, try installing without specifying pydantic-core version (let pip choose compatible version):

```bash
# Edit requirements.txt temporarily to remove pydantic-core line
# Then install, and pip will install the correct version automatically
python3.11 -m pip install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir 2>/dev/null || pip3 install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir
```

---

## Option 2: Use WSL (Windows Subsystem for Linux)

If you have WSL installed, you can use it:

### Step 1: Open WSL

1. Open PowerShell
2. Type: `wsl`
3. Press Enter

### Step 2: Navigate to Your Project

```bash
cd /mnt/e/Visitor\ Module/backend
```

### Step 3: Install Python 3.11 (if not installed)

```bash
sudo apt update
sudo apt install python3.11 python3-pip zip -y
```

### Step 4: Create Layer

```bash
# Create folder structure
mkdir -p lambda-layer/python/lib/python3.11/site-packages
cd lambda-layer

# Install dependencies
python3.11 -m pip install --upgrade pip setuptools wheel
python3.11 -m pip install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir

# Verify pydantic-core was installed correctly
python3.11 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('SUCCESS: pydantic-core native module found')"

# Reduce layer size by removing unnecessary files
find python/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find python/lib/python3.11/site-packages -name "*.pyc" -delete
find python/lib/python3.11/site-packages -name "*.pyo" -delete

# Create ZIP
cd ..
zip -r layer.zip python/

# Check size
ls -lh layer.zip
```

### Step 5: Use the layer.zip

The `layer.zip` will be in your backend folder. Upload it to AWS Lambda Layers.

---

## Option 3: Use Free EC2 Linux Instance ⭐ **RECOMMENDED FOR GLIBC COMPATIBILITY**

**Why EC2?** Lambda Python 3.11 uses Amazon Linux 2023. Building on the same OS ensures GLIBC compatibility and prevents errors like `GLIBC_2.28 not found`.

Create a free EC2 Linux instance, build the layer there, then download it.

### Step 1: Launch EC2 Instance

1. Go to EC2 Console
2. Click "Launch Instance"
3. **Name**: `lambda-layer-builder`
4. **AMI**: **Amazon Linux 2023** (MUST be 2023, not 2) - This matches Lambda Python 3.11 runtime exactly
5. **Instance type**: t2.micro (free tier eligible)
6. **Key pair**: Create new or use existing
7. Click "Launch Instance"

**Important:** Use Amazon Linux 2023, NOT Amazon Linux 2, to match Lambda's Python 3.11 runtime.

### Step 2: Connect to EC2

1. Wait for instance to be running
2. Click "Connect"
3. Use "EC2 Instance Connect" (browser-based, no SSH client needed)
4. Click "Connect"

### Step 3: Install Python and Dependencies

In EC2 terminal:

```bash
# Update system
sudo yum update -y

# Install Python 3.11 and build tools
sudo yum install python3.11 python3.11-pip python3.11-devel gcc zip -y

# Verify GLIBC version (should match Lambda runtime)
ldd --version

# Verify Python version
python3.11 --version

# Create folder
mkdir -p ~/lambda-layer/python/lib/python3.11/site-packages
cd ~/lambda-layer
```

### Step 4: Create requirements.txt

Create a file with your requirements:

```bash
cat > requirements.txt << 'EOF'
fastapi==0.121.3
starlette==0.49.3
uvicorn==0.34.0
mangum==0.20.0
boto3==1.35.71
sqlalchemy==2.0.44
psycopg2-binary==2.9.10
bcrypt==5.0.0
python-jose[cryptography]==3.5.0
cryptography==46.0.3
pydantic==2.12.4
pydantic-core==2.41.5
pydantic-settings==2.6.1
anyio==4.11.0
idna==3.11
sniffio==1.3.1
python-multipart==0.0.20
twilio==9.3.0
qrcode[pil]==7.4.2
Pillow==11.0.0
typing-extensions==4.15.0
annotated-types==0.7.0
annotated-doc==0.0.4
typing-inspection==0.4.2
cffi==2.0.0
pycparser==2.23
ecdsa==0.19.1
pyasn1==0.6.1
rsa==4.9.1
six==1.17.0
greenlet==3.2.4
EOF
```

### Step 5: Build Layer

```bash
# Install dependencies
python3.11 -m pip install --upgrade pip setuptools wheel
python3.11 -m pip install -r requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir

# Verify pydantic-core was installed correctly
python3.11 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('SUCCESS: pydantic-core native module found')"

# Create ZIP
zip -r layer.zip python/

# Check size
ls -lh layer.zip
```

### Step 6: Download layer.zip

1. In EC2 Console, select your instance
2. Click "Actions" → "Instance settings" → "Get system log" (to see file location)
3. Or use S3 to transfer:
   ```bash
   # Upload to S3 (if you have S3 bucket)
   aws s3 cp layer.zip s3://your-bucket-name/layer.zip
   ```
4. Download from S3 to your computer

### Step 7: Terminate Instance (to avoid charges)

1. Select instance
2. Click "Instance state" → "Terminate instance"

---

## Quick Comparison

| Option | Difficulty | Time | Cost | Python Version | Best For |
|--------|-----------|------|------|----------------|----------|
| **AWS CloudShell** | ⭐⭐ Medium | 15 min | Free | 3.9 (need to install 3.11) | If Python 3.11 installs easily |
| **WSL** | ⭐⭐ Medium | 15 min | Free | 3.11 (installable) | If you have WSL installed |
| **EC2** | ⭐⭐⭐ Hard | 30 min | Free tier | 3.11 (pre-installed) | **Most reliable** ✅ |

---

## Recommendation: Use EC2 (Option 3) - Most Reliable

**Why EC2?**
- ✅ Python 3.11 pre-installed (no installation needed)
- ✅ Free tier eligible (t2.micro)
- ✅ Linux x86_64 environment (perfect for Lambda)
- ✅ No compatibility issues
- ✅ Most reliable for native extensions like pydantic-core

**Why NOT CloudShell?**
- ⚠️ Comes with Python 3.9 only
- ⚠️ Python 3.11 installation can be difficult
- ⚠️ May have issues with native extensions

**Follow Option 3 (EC2) above for the most reliable setup!**

If you prefer CloudShell, try Option 1 but be prepared to switch to EC2 if Python 3.11 installation fails.

---

## After Creating Layer

Once you have `layer.zip`:

1. Go to Lambda Console → Layers
2. Create new layer
3. Upload `layer.zip`
4. Select Python 3.11
5. Attach to your Lambda function
6. Test your function

Your Lambda will now have all dependencies! 🎉

---

## Troubleshooting

### Error: GLIBC Version Mismatch

If you get this error:
```
/lib64/libc.so.6: version `GLIBC_2.28' not found (required by ...)
```

**Cause:** The layer was built on a system with a newer GLIBC than Lambda's runtime.

**Solution:** 
1. **Use EC2 with Amazon Linux 2023** (Option 3) - This matches Lambda Python 3.11 runtime exactly
2. Make sure you're building on Amazon Linux 2023, NOT Amazon Linux 2 or CloudShell
3. Lambda Python 3.11 uses Amazon Linux 2023, so build on the same OS

**Why this happens:**
- CloudShell might use a different Linux version
- Building on Ubuntu/WSL can have different GLIBC versions
- Native extensions (like bcrypt, pydantic-core) are compiled against the system's GLIBC

### Error: pydantic-core Module Not Found

If you get this error:
```
No module named 'pydantic_core._pydantic_core'
```

This happens because `pydantic-core` is a compiled native extension that must be built for Lambda's Linux x86_64 environment.

**Quick fix:** Rebuild the layer with upgraded pip and `--no-cache-dir` flag:
```bash
cd lambda-layer
rm -rf python/lib/python3.11/site-packages/*
python3.11 -m pip install --upgrade pip setuptools wheel 2>/dev/null || pip3 install --upgrade pip setuptools wheel
python3.11 -m pip install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir 2>/dev/null || pip3 install -r ../requirements.txt -t python/lib/python3.11/site-packages/ --no-cache-dir
python3.11 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('SUCCESS')" 2>/dev/null || python3 -c "import sys; sys.path.insert(0, 'python/lib/python3.11/site-packages'); import pydantic_core._pydantic_core; print('SUCCESS')"
cd ..
zip -r layer.zip python/
```
Then re-upload the layer to AWS.
