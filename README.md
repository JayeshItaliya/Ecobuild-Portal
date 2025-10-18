# Ecobuild Portal

Django-based multilingual content management system with automatic translation to Hebrew, Russian, and Arabic.

**Python**: 3.12.3+ | **Django**: 5.2.3

---

## 🚀 Quick Start

```bash
# 1. Setup environment
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment (.env file)
# Copy and edit the .env file with your settings
# For translation: Set USE_GOOGLE_TRANSLATE=true and add google-credentials.json

# 3. Setup database
python manage.py migrate
python manage.py createsuperuser

# 4. Run server
python manage.py runserver
```

Visit: http://localhost:8000

---

## 🌍 Automatic Translation

Content is automatically translated to **Hebrew (he)**, **Russian (ru)**, and **Arabic (ar)**.

### Models with Auto-Translation:
- **Accounts**: CompanyInfo, Role, ActivityLog
- **CMS**: Document, ContactMessage, FAQ, GalleryCategory, Product, ProductCategory, ProductSection
- **About Us**: AboutUsPage, TeamMember, CompanyTimeline, CompanyAchievement

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
├── utils/             # Translation utilities
├── locale/            # Translation files
└── requirements.txt   # Dependencies
```

---

## 🔧 Key Files

- **accounts/translation.py** - Translation service (Google API integration)
- **utils/model_translation.py** - Auto-translation mixin for models
- **backend/settings.py** - Configuration (see GOOGLE CLOUD TRANSLATION API section)

---

## 📝 Environment Variables

Key variables in `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=1  # Set to 0 in production
USE_GOOGLE_TRANSLATE=true  # Enable real translations
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
```

---

## 🔒 Security

- ✅ Credentials protected in `.gitignore`
- ✅ Environment variables for secrets
- ✅ HTTPS in production
- ✅ CORS configured

---

## 📚 Documentation

### API Documentation
- Swagger: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

### Feature Documentation
All feature-specific API references and guides are available in the **[docs/](docs/)** folder:
- [Broadcast News API Reference](docs/BROADCAST_NEWS_API_REFERENCE.md)

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

**Version**: 1.0 | **Last Updated**: October 2025
