# Ecobuild Portal

Django-based multilingual content management system with automatic translation to Hebrew, Russian, and Arabic, featuring unified file storage with AWS S3 support.

**Python**: 3.12.3+ | **Django**: 5.2.3 | **Storage**: Local/S3

---

## 🚀 Quick Start

```bash
# 1. Setup environment
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# If you get "ModuleNotFoundError: No module named 'storages'":
# See INSTALL_DEPENDENCIES.md for quick fix

# 3. Configure environment
cp env.example .env
# Edit .env with your settings
# For translation: Set USE_GOOGLE_TRANSLATE=true and add google-credentials.json
# For S3 storage: Set USE_S3_STORAGE=true and add AWS credentials (see S3_SETUP_GUIDE.md)

# 4. Setup database
python manage.py migrate
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

Visit: http://localhost:8000

---

## 🌍 Automatic Translation

Content is automatically translated to **Hebrew (he)**, **Russian (ru)**, and **Arabic (ar)**.

### Models with Auto-Translation:
- **Accounts**: CompanyInfo, Role, ActivityLog
- **CMS**: Document, ContactMessage, FAQ, GalleryCategory, Product, ProductCategory, ProductSection
- **About Us**: AboutUsPage, TeamMember, CompanyTimeline, CompanyAchievement, AboutUsSection

### Configuration in `.env`:
```env
USE_GOOGLE_TRANSLATE=true  # Enable Google Translation API
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json  # Path to credentials
```

### How it works:
```python
# You create with English only:
faq = FAQ.objects.create(
    question={"en": "What is Ecobuild?"},
    answer={"en": "A construction company"}
)

# Automatically saves with all languages:
# question = {
#     "en": "What is Ecobuild?",
#     "he": "מהי אקובילד?",
#     "ru": "Что такое Ecobuild?",
#     "ar": "ما هو إيكوبيلد؟"
# }
```

**Cost**: FREE for first 500k characters/month (~75k-150k typical usage)

---

## 📁 Project Structure

```
Ecobuild-Portal/
├── accounts/          # Users, auth, company info
├── cms/               # Content (products, blog, FAQ, gallery)
├── backend/           # Django settings
├── utils/             # Translation & storage utilities
│   ├── storage.py           # Unified file storage system
│   ├── custom_storages.py   # S3 storage backends
│   └── model_translation.py # Auto-translation mixin
├── locale/            # Translation files
├── media/             # User uploads (local development)
└── requirements.txt   # Dependencies
```

---

## 🔧 Key Files

- **accounts/translation.py** - Translation service (Google API integration)
- **utils/model_translation.py** - Auto-translation mixin for models
- **utils/storage.py** - Unified file storage system (Local/S3)
- **utils/custom_storages.py** - Custom S3 storage backends
- **backend/settings.py** - Configuration (Translation & Storage)

---

## 📝 Environment Variables

Key variables in `.env`:

```env
# Django Core
SECRET_KEY=your-secret-key
DEBUG=1  # Set to 0 in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Translation
USE_GOOGLE_TRANSLATE=true  # Enable real translations
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json

# File Storage (Local vs S3)
USE_S3_STORAGE=false  # Set to true for S3 storage in production

# AWS S3 (Required only if USE_S3_STORAGE=true)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=ap-south-1
```

---

## 📦 File Storage System

This project features a **unified file storage system** that works seamlessly in both development and production:

### 🔧 How It Works

- **Development (Local)**: Files stored in `/media/` directory
- **Production (S3)**: Files stored in AWS S3 bucket
- **Automatic**: System automatically selects storage based on `USE_S3_STORAGE` setting

### 📁 Usage in Code

```python
from utils.storage import upload_file, delete_file, get_file_url

# Upload an image
file_path = upload_file(
    file=request.FILES['image'],
    upload_path='products/images',
    file_type='image'  # Auto-validates extension and size
)

# Get file URL (works for both local and S3)
image_url = get_file_url(file_path)

# Delete file
delete_file(file_path)
```

### 🎯 Supported File Types

| Type | Extensions | Max Size |
|------|-----------|----------|
| **Images** | jpg, jpeg, png, gif, webp, svg | 10 MB |
| **Videos** | mp4, avi, mov, wmv, flv, webm | 100 MB |
| **Documents** | pdf, doc, docx, xls, xlsx, ppt | 20 MB |
| **Archives** | zip, rar, 7z, tar, gz | 50 MB |

### 🔐 S3 Setup (Production)

1. Create AWS S3 bucket
2. Create IAM user with S3 permissions
3. Add credentials to `.env`:
   ```env
   USE_S3_STORAGE=true
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_STORAGE_BUCKET_NAME=your-bucket
   AWS_S3_REGION_NAME=ap-south-1
   ```
4. Install dependencies: `pip install boto3 django-storages`

### 📝 Models with File Fields

All file uploads in models automatically use the unified storage:

```python
class Product(models.Model):
    image = models.ImageField(upload_to='products/')  # Uses storage system
    brochure = models.FileField(upload_to='documents/')  # Uses storage system
```

---

## 🔒 Security

- ✅ Credentials protected in `.gitignore`
- ✅ Environment variables for secrets
- ✅ HTTPS in production
- ✅ CORS configured

---

## 📚 API Documentation

- Swagger: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

---

## 🧪 Testing Translation

```bash
python manage.py shell
```

```python
from accounts.translation import translator

# Test translation
result = translator.translate_text("Hello World", "he")
print(result)  # Output: שלום עולם

# Test on a model
from cms.models.faq import FAQ
faq = FAQ.objects.create(
    question={"en": "Test?"},
    answer={"en": "Testing auto-translation"}
)
print(faq.question)  # All 4 languages populated!
```

---

## 📖 Additional Documentation

- **[S3_SETUP_GUIDE.md](S3_SETUP_GUIDE.md)** - Complete guide for AWS S3 storage setup
  - Installation instructions
  - AWS S3 bucket configuration
  - Environment variables setup
  - Usage examples and code snippets
  - Troubleshooting common issues
  - Cost estimation

- **[env.example](env.example)** - Environment configuration template

---

## ✨ What's New in This Version

### File Storage System (v1.1)
- ✅ Unified file upload utility for images, videos, documents
- ✅ Automatic local/S3 storage switching based on environment
- ✅ Built-in file validation (type, size, extension)
- ✅ Automatic file cleanup on delete/update
- ✅ Full URL generation for both environments
- ✅ Example implementations in Gallery and Document models

### Translation System (v1.0)
- ✅ Automatic translation to Hebrew, Russian, Arabic
- ✅ Google Cloud Translation API integration
- ✅ Translation mixin for models
- ✅ Cost-efficient (free tier available)

---

**Version**: 1.1 | **Last Updated**: October 2025
