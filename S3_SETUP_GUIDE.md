# S3 Storage Setup Guide for Production

Complete guide to implement AWS S3 file storage in your Ecobuild Portal production environment.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Install Required Packages](#install-required-packages)
3. [AWS S3 Setup](#aws-s3-setup)
4. [Configure Environment Variables](#configure-environment-variables)
5. [How to Use the Storage System](#how-to-use-the-storage-system)
6. [Testing](#testing)
7. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

- AWS Account
- Django project already set up
- Access to your production server

---

## 1. Install Required Packages

### Step 1.1: Install Dependencies

The error you're seeing (`ModuleNotFoundError: No module named 'storages'`) means you need to install the required packages.

```bash
# Activate your virtual environment first
source env/bin/activate  # or env\Scripts\activate on Windows

# Install the new packages
pip install boto3==1.34.0
pip install django-storages==1.14.2

# Or install all requirements
pip install -r requirements.txt
```

### Step 1.2: Verify Installation

```bash
python -c "import storages; print('django-storages installed successfully')"
python -c "import boto3; print('boto3 installed successfully')"
```

---

## 2. AWS S3 Setup

### Step 2.1: Create S3 Bucket

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **S3** service
3. Click **"Create bucket"**
4. Configure:
   - **Bucket name**: `ecobuild-portal-media` (must be globally unique)
   - **Region**: `ap-south-1` (Mumbai) or your preferred region
   - **Block Public Access**: Uncheck "Block all public access" (we need public read)
   - Click **"Create bucket"**

### Step 2.2: Configure Bucket Policy

1. Go to your bucket → **Permissions** tab
2. Scroll to **Bucket Policy**
3. Add this policy (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

### Step 2.3: Configure CORS (if needed)

If your frontend is on a different domain:

1. Go to **Permissions** → **CORS**
2. Add this configuration:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### Step 2.4: Create IAM User

1. Go to **IAM** service → **Users**
2. Click **"Add users"**
3. User name: `ecobuild-s3-user`
4. Select **"Access key - Programmatic access"**
5. Click **"Next: Permissions"**
6. Click **"Attach existing policies directly"**
7. Search and select: **"AmazonS3FullAccess"** (or create custom policy)
8. Click through to **"Create user"**
9. **IMPORTANT**: Copy the **Access Key ID** and **Secret Access Key** (you won't see them again!)

### Alternative: Custom IAM Policy (Recommended for Production)

For better security, use a custom policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR-BUCKET-NAME",
                "arn:aws:s3:::YOUR-BUCKET-NAME/*"
            ]
        }
    ]
}
```

---

## 3. Configure Environment Variables

### Step 3.1: Update Your .env File

**For Production Server:**

```env
# Django Core
SECRET_KEY=your-production-secret-key-change-this
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (use PostgreSQL in production)
DB_NAME=ecobuild_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# File Storage - ENABLE S3
USE_S3_STORAGE=true

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=ecobuild-portal-media
AWS_S3_REGION_NAME=ap-south-1

# Translation (optional)
USE_GOOGLE_TRANSLATE=true
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json

# CORS & CSRF
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# URLs
DOMAIN_URL=https://yourdomain.com
FRONTEND_DOMAIN=https://frontend.yourdomain.com
```

**For Local Development (keep S3 disabled):**

```env
# File Storage - USE LOCAL
USE_S3_STORAGE=false
DEBUG=1
```

---

## 4. How to Use the Storage System

The storage system is already implemented! Here's how it works:

### 4.1 Models (Automatic)

Your models already work with S3! No changes needed:

```python
# This automatically uses S3 when USE_S3_STORAGE=true
class Product(models.Model):
    image = models.ImageField(upload_to='products/')  # ✅ Works with S3
    brochure = models.FileField(upload_to='documents/')  # ✅ Works with S3
```

### 4.2 Manual File Upload (in Views/Serializers)

Use the storage utilities:

```python
from utils.storage import upload_file, delete_file, get_file_url

# Upload a file
file_path = upload_file(
    file=request.FILES['image'],
    upload_path='products/images',
    file_type='image'  # Validates automatically
)

# Get file URL (returns S3 URL in production)
url = get_file_url(file_path)

# Delete file
delete_file(file_path)
```

### 4.3 Serializers - Add URL Fields

```python
from rest_framework import serializers
from utils.storage import get_file_url, validate_file

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'image_url']

    def get_image_url(self, obj):
        """Returns S3 URL in production, local URL in development"""
        if obj.image:
            return get_file_url(obj.image.name)
        return None

    def validate_image(self, value):
        """Validate file before upload"""
        if value:
            is_valid, error_msg = validate_file(value, file_type='image')
            if not is_valid:
                raise serializers.ValidationError(error_msg)
        return value
```

### 4.4 File Validation

Built-in file type and size validation:

| Type | Extensions | Max Size |
|------|-----------|----------|
| `'image'` | jpg, jpeg, png, gif, webp, svg, bmp | 10 MB |
| `'video'` | mp4, avi, mov, wmv, flv, webm, mkv | 100 MB |
| `'document'` | pdf, doc, docx, xls, xlsx, ppt, pptx, txt | 20 MB |
| `'file'` | zip, rar, 7z, tar, gz | 50 MB |

---

## 5. Testing

### Step 5.1: Test S3 Connection

```bash
python manage.py shell
```

```python
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Test upload
test_content = ContentFile(b"Test content")
path = default_storage.save('test/test.txt', test_content)
print(f"Saved to: {path}")

# Test URL generation
url = default_storage.url(path)
print(f"URL: {url}")
# Should be: https://your-bucket.s3.region.amazonaws.com/media/test/test.txt

# Test delete
default_storage.delete(path)
print("Deleted successfully")
```

### Step 5.2: Test Through API

1. **Upload a file** through your API (e.g., create a Gallery item)
2. **Check S3 Console** - file should appear in your bucket
3. **Access the URL** - file should be publicly accessible
4. **Delete the item** - file should be removed from S3

### Step 5.3: Verify Existing Models

Test with Gallery (already updated):

```python
from cms.models import Gallery
from django.core.files.uploadedfile import SimpleUploadedFile

# Create test file
test_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

# Upload through model
gallery = Gallery.objects.create(
    image=test_file,
    category=your_category
)

# Check URL
print(gallery.image.url)  # Should be S3 URL

# Delete
gallery.delete()  # File automatically removed from S3
```

---

## 6. Common Issues & Solutions

### Issue 1: `ModuleNotFoundError: No module named 'storages'`

**Solution:**
```bash
pip install django-storages==1.14.2 boto3==1.34.0
```

### Issue 2: `NoCredentialsError` or `ClientError`

**Cause:** AWS credentials not found or incorrect

**Solution:**
1. Check `.env` file has correct values:
   ```env
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   ```
2. Verify credentials are correct in AWS IAM
3. Restart Django server after changing `.env`

### Issue 3: `Access Denied` when accessing files

**Cause:** Bucket policy doesn't allow public read

**Solution:**
1. Go to S3 bucket → Permissions
2. Uncheck "Block all public access"
3. Add bucket policy (see Step 2.2)

### Issue 4: Files uploading but returning 403 Forbidden

**Cause:** Incorrect ACL or bucket permissions

**Solution:**
Update `utils/custom_storages.py`:
```python
class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'  # Make sure this is set
    file_overwrite = False
```

### Issue 5: CORS errors from frontend

**Cause:** CORS not configured

**Solution:**
Add CORS configuration to S3 bucket (see Step 2.3)

### Issue 6: Files still saving locally instead of S3

**Cause:** `USE_S3_STORAGE` not set correctly

**Solution:**
1. Check `.env`: `USE_S3_STORAGE=true`
2. Restart Django: `python manage.py runserver`
3. Verify in shell:
   ```python
   from django.conf import settings
   print(settings.USE_S3_STORAGE)  # Should be True
   ```

---

## 7. Deployment Checklist

Before deploying to production:

- [ ] Install `boto3` and `django-storages` packages
- [ ] Create S3 bucket in AWS
- [ ] Configure bucket policy for public read
- [ ] Create IAM user with S3 permissions
- [ ] Add AWS credentials to `.env`
- [ ] Set `USE_S3_STORAGE=true` in production `.env`
- [ ] Set `DEBUG=0` in production
- [ ] Configure CORS if needed
- [ ] Test file upload through API
- [ ] Verify files appear in S3 bucket
- [ ] Test file URLs are accessible
- [ ] Test file deletion removes from S3
- [ ] Set up S3 bucket versioning (optional but recommended)
- [ ] Configure S3 lifecycle rules for old files (optional)

---

## 8. Migration from Local to S3

If you already have files in local `/media/` folder:

### Option 1: Manual Upload to S3

```bash
# Install AWS CLI
pip install awscli

# Configure AWS CLI
aws configure

# Sync local media to S3
aws s3 sync media/ s3://your-bucket-name/media/
```

### Option 2: Keep Existing Files Local, New Files to S3

Just enable S3. Existing file URLs in database will still point to local files.
New uploads go to S3 automatically.

---

## 9. Cost Estimation

AWS S3 Pricing (approximate, check current AWS pricing):

**Storage:**
- First 50 TB: $0.023 per GB/month
- Example: 10 GB = ~$0.23/month

**Requests:**
- PUT/POST: $0.005 per 1,000 requests
- GET: $0.0004 per 1,000 requests

**Data Transfer:**
- First 1 GB/month: Free
- Next 9.999 TB: $0.09 per GB

**Typical Usage for Small Project:**
- Storage: 10 GB = $0.23/month
- Requests: 10,000 = $0.05/month
- Transfer: 5 GB = $0.45/month
- **Total: ~$1-2/month**

---

## 10. Quick Reference

### Environment Variables

```env
# Enable S3
USE_S3_STORAGE=true

# AWS Credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=ap-south-1
```

### Common Commands

```python
# Upload
from utils.storage import upload_file
path = upload_file(file, 'folder/', 'image')

# Get URL
from utils.storage import get_file_url
url = get_file_url(path)

# Delete
from utils.storage import delete_file
delete_file(path)

# Validate
from utils.storage import validate_file
is_valid, error = validate_file(file, 'image')
```

---

## 11. Support & Resources

- **AWS S3 Documentation**: https://docs.aws.amazon.com/s3/
- **django-storages Documentation**: https://django-storages.readthedocs.io/
- **Project Source Code**:
  - Storage utilities: `utils/storage.py`
  - Custom backends: `utils/custom_storages.py`
  - Settings: `backend/settings.py`

---

## Summary

1. ✅ Install `boto3` and `django-storages`
2. ✅ Create S3 bucket with public read policy
3. ✅ Create IAM user with S3 access
4. ✅ Add credentials to `.env`
5. ✅ Set `USE_S3_STORAGE=true`
6. ✅ Test upload/download/delete
7. ✅ Deploy and monitor

**That's it!** Your file storage now works with S3 in production and local storage in development, with no code changes needed.

---

**Version**: 1.1
**Last Updated**: October 2025
