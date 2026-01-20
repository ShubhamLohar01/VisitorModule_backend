# Build Lambda Layer Using Docker (Recommended)

The `pydantic_core` error happens because Windows-installed packages aren't compatible with Linux (Lambda runs on Linux).

## Solution: Use Docker to Build Layer

Docker will create a Linux environment to build the layer correctly.

### Step 1: Install Docker Desktop

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Wait for Docker to be running (green icon in system tray)

### Step 2: Build Layer Using Docker

**Option A: Use the provided script**

1. Make sure Docker is running
2. Run:
   ```bash
   docker build -t lambda-layer-builder -f Dockerfile.layer .
   docker run --rm -v "%CD%":/output lambda-layer-builder
   ```

**Option B: Manual Docker commands**

1. Create a file `Dockerfile.layer`:
   ```dockerfile
   FROM public.ecr.aws/lambda/python:3.11
   
   WORKDIR /layer
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt -t python/lib/python3.11/site-packages/
   
   RUN cd python && zip -r /output/layer.zip .
   ```

2. Build and run:
   ```bash
   docker build -t lambda-layer-builder -f Dockerfile.layer .
   docker run --rm -v "%CD%":/output lambda-layer-builder
   ```

3. This will create `layer.zip` in your current directory

### Step 3: Upload to AWS

1. Go to Lambda Console → Layers
2. Create new layer (or update existing)
3. Upload the `layer.zip` created by Docker
4. Attach to your Lambda function

---

## Alternative: Use EC2 Linux Instance

If Docker doesn't work, you can:

1. Launch an EC2 Linux instance (t2.micro is free tier)
2. SSH into it
3. Install Python 3.11 and pip
4. Run the prepare script there
5. Download the layer.zip

---

## Quick Fix: Try Without pydantic_core

If you need a quick workaround, you can try installing pydantic without the core:

```bash
pip install pydantic --no-binary pydantic-core
```

But this is not recommended for production.
