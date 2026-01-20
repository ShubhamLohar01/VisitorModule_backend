# Quick Fix: Make Endpoint Return Immediately (Bypass 29s Limit)

## The Real Problem

**API Gateway has a HARD 29-second timeout limit.** Even if your Lambda has 120s timeout, API Gateway will return 504 after 29 seconds.

Current flow (too slow):
```
Frontend → API Gateway → Lambda → Database Write → S3 Upload → Response
                         ↑________________________29s limit________________↑
```

## Solution: Return Immediately, Upload in Background

New flow (fast):
```
Frontend → API Gateway → Lambda → Database Write → Return Immediately (2-3s)
                                           ↓
                                  Background: S3 Upload (async)
```

---

## Option 1: Simple Fix - Skip Image Upload Temporarily

Test if the timeout is indeed from S3:

**Edit:** `backend/app/routers/visitor.py`

Find the S3 upload section (around line 330) and comment it out:

```python
# try:
#     # Upload image to S3 using visitor number as filename
#     img_url = s3_service.upload_visitor_image(
#         file_content=file_content,
#         visitor_number=visitor_number,
#         content_type=image.content_type
#     )
#
#     # Update visitor with image URL
#     new_visitor.img_url = img_url
#     db.commit()
#     db.refresh(new_visitor)
#
# except Exception as e:
#     # If image upload fails, rollback the visitor creation
#     db.delete(new_visitor)
#     db.commit()
#     raise HTTPException(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         detail=f"Failed to upload image: {str(e)}"
#     )

# Temporary: Set placeholder image URL
new_visitor.img_url = f"https://placeholder.com/visitor-{visitor_number}.jpg"
db.commit()
db.refresh(new_visitor)
```

**Test:** If form submits successfully now, the S3 upload is the bottleneck.

---

## Option 2: Best Fix - Async S3 Upload with Lambda

### Step 1: Modify Endpoint to Return Immediately

**File:** `backend/app/routers/visitor.py`

```python
@router.post("/check-in-with-image", response_model=VisitorCheckInResponse, status_code=status.HTTP_201_CREATED)
async def check_in_visitor_with_image(
    visitor_name: str = Form(...),
    mobile_number: str = Form(...),
    person_to_meet: str = Form(...),
    reason_to_visit: str = Form(...),
    email_address: str = Form(...),
    company: str = Form(...),
    warehouse: Optional[str] = Form(None),
    health_declaration: Optional[str] = Form(None),
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    import time
    start_time = time.time()
    
    logger.info(f"[TIMING] Endpoint started at {start_time}")
    
    # Validate image file
    allowed_content_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if image.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image format. Allowed formats: {', '.join(allowed_content_types)}"
        )

    # Read image content
    file_content = await image.read()
    logger.info(f"[TIMING] Image read: {time.time() - start_time:.2f}s")
    
    # Validate file size (max 10MB)
    max_file_size = 10 * 1024 * 1024
    if len(file_content) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file size exceeds 10MB limit"
        )

    # Create visitor record
    new_visitor = Visitor(
        visitor_name=visitor_name,
        mobile_number=mobile_number,
        email_address=email_address,
        company=company,
        person_to_meet=person_to_meet,
        reason_to_visit=reason_to_visit,
        warehouse=warehouse,
        health_declaration=health_declaration,
        status=VisitorStatus.WAITING,
        img_url="pending"  # Placeholder until upload completes
    )

    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)
    logger.info(f"[TIMING] DB write: {time.time() - start_time:.2f}s")

    visitor_number = new_visitor.check_in_time.strftime("%Y%m%d%H%M%S")

    # Upload to S3 in background (non-blocking)
    def upload_image_background():
        """Background task for S3 upload"""
        try:
            logger.info(f"[BACKGROUND] Starting S3 upload for visitor {visitor_number}")
            img_url = s3_service.upload_visitor_image(
                file_content=file_content,
                visitor_number=visitor_number,
                content_type=image.content_type
            )
            
            # Update visitor with image URL
            from app.core.database import SessionLocal
            db_bg = SessionLocal()
            try:
                visitor = db_bg.query(Visitor).filter(Visitor.id == new_visitor.id).first()
                if visitor:
                    visitor.img_url = img_url
                    db_bg.commit()
                    logger.info(f"[BACKGROUND] S3 upload complete for visitor {visitor_number}")
            finally:
                db_bg.close()
                
        except Exception as e:
            logger.error(f"[BACKGROUND] S3 upload failed: {str(e)}")

    # Add to background tasks
    background_tasks.add_task(upload_image_background)
    
    logger.info(f"[TIMING] Total response time: {time.time() - start_time:.2f}s")

    # Return immediately (visitor record created, image uploading in background)
    visitor_data = enrich_visitor_with_contact(new_visitor, db)
    
    # Send SMS in background
    # ... existing SMS code ...
    
    return {
        "message": "Visitor checked in successfully. Image upload in progress.",
        "visitor": visitor_data,
        "image_status": "uploading"  # Frontend can poll for completion
    }
```

### Step 2: Add Endpoint to Check Upload Status

```python
@router.get("/{visitor_id}/upload-status")
def get_upload_status(
    visitor_id: int,
    db: Session = Depends(get_db)
):
    """Check if visitor image upload is complete"""
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    
    return {
        "visitor_id": visitor_id,
        "image_uploaded": visitor.img_url != "pending",
        "img_url": visitor.img_url if visitor.img_url != "pending" else None
    }
```

### Step 3: Update Frontend to Poll for Completion

**File:** `frontend/app/page.tsx`

```typescript
const handleFormSubmit = async (formData: VisitorFormData) => {
  setIsLoading(true);

  try {
    // ... existing form preparation ...

    const response = await fetch(`${API_ENDPOINTS.visitors}/check-in-with-image`, {
      method: 'POST',
      body: formDataToSend,
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json();
    
    // If image is still uploading, poll for completion
    if (data.image_status === 'uploading') {
      console.log('Image uploading in background, checking status...');
      
      const checkUploadStatus = async () => {
        for (let i = 0; i < 10; i++) {  // Check up to 10 times (20 seconds)
          await new Promise(resolve => setTimeout(resolve, 2000));  // Wait 2s
          
          const statusResponse = await fetch(
            `${API_ENDPOINTS.visitors}/${data.visitor.id}/upload-status`
          );
          const statusData = await statusResponse.json();
          
          if (statusData.image_uploaded) {
            console.log('Image upload complete!');
            break;
          }
        }
      };
      
      // Check status in background (don't wait for it)
      checkUploadStatus();
    }

    // Continue with rest of form submission logic...
    // Show success message immediately
    addToast('Check-in successful!', 'success');
    
  } finally {
    setIsLoading(false);
  }
};
```

---

## Option 3: Fastest Fix - Use Pre-Signed URL (Upload from Frontend)

Let S3 upload happen directly from frontend:

### Backend: Generate Pre-Signed URL

```python
@router.post("/generate-upload-url")
async def generate_upload_url(
    visitor_id: int,
    content_type: str = "image/jpeg",
    db: Session = Depends(get_db)
):
    """Generate pre-signed URL for direct S3 upload from frontend"""
    
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    
    visitor_number = visitor.check_in_time.strftime("%Y%m%d%H%M%S")
    object_key = f"visitors/{visitor_number}.jpg"
    
    # Generate pre-signed POST URL
    presigned_post = s3_service.s3_client.generate_presigned_post(
        Bucket=s3_service.bucket_name,
        Key=object_key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 0, 10485760]  # Max 10MB
        ],
        ExpiresIn=300  # 5 minutes
    )
    
    return {
        "upload_url": presigned_post['url'],
        "fields": presigned_post['fields'],
        "object_url": f"https://{s3_service.bucket_name}.s3.{s3_service.region}.amazonaws.com/{object_key}"
    }
```

### Frontend: Upload Directly to S3

```typescript
// 1. Create visitor record (fast, no image)
const visitorResponse = await fetch(`${API_ENDPOINTS.visitors}/check-in`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(visitorData)
});

const { visitor } = await visitorResponse.json();

// 2. Get pre-signed URL
const urlResponse = await fetch(
  `${API_ENDPOINTS.visitors}/generate-upload-url?visitor_id=${visitor.id}`
);
const { upload_url, fields } = await urlResponse.json();

// 3. Upload directly to S3 (bypasses Lambda)
const formData = new FormData();
Object.entries(fields).forEach(([key, value]) => {
  formData.append(key, value as string);
});
formData.append('file', imageBlob);

await fetch(upload_url, {
  method: 'POST',
  body: formData
});
```

---

## Recommended Approach

**For immediate fix:** Use **Option 2** (Background upload)
- Minimal code changes
- Response time: 2-5 seconds (within 29s limit)
- Image uploads in background

**For best performance:** Use **Option 3** (Pre-signed URL)
- Fastest (bypasses Lambda entirely)
- Response time: < 2 seconds
- S3 upload happens directly from browser
- More code changes needed

---

## Deploy After Changes

```powershell
cd "E:\Visitor Module\backend"

# Rebuild deployment package
Compress-Archive -Path app,lambda_handler.py -DestinationPath deployment-quick.zip -Force

# Upload via AWS Console:
# Lambda → Code → Upload from .zip file → deployment-quick.zip
```
