# Broadcast News API Reference

## Overview
API endpoints for managing and displaying news channel interviews with line-by-line interview content.

---

## Admin Panel
**Access**: `/admin/cms/broadcastnews/`

Add broadcast news with inline interview details (speaker, content, timestamp, order).

---

## API Endpoints

### Public Endpoints (No Authentication)

#### 1. List Published Broadcast News
```
GET /api/cms/broadcast-news/
```

**Query Parameters:**
- `search` - Search in title, channel, names, description
- `ordering` - Sort by field (e.g., `-broadcast_date`, `views_count`)
- `page` - Page number for pagination

**Response:**
```json
{
  "status_code": 200,
  "message": "Broadcast news fetched successfully",
  "data": {
    "count": 10,
    "next": "http://api.example.com/api/cms/broadcast-news/?page=2",
    "previous": null,
    "results": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": {"en": "CEO Interview", "ar": "مقابلة الرئيس التنفيذي"},
        "slug": "ceo-interview",
        "channel_name": {"en": "News Network"},
        "publication_name": {"en": "Business Weekly"},
        "interviewer_name": {"en": "John Smith"},
        "interviewee_name": {"en": "Jane Doe"},
        "interview_date": "2025-10-15",
        "broadcast_date": "2025-10-17T20:00:00Z",
        "description": {"en": "Exclusive interview about company vision"},
        "thumbnail_image": "/media/broadcast_news/thumbnails/image.jpg",
        "article_url": "https://businessweekly.com/interviews/ceo-2025",
        "status": "Published",
        "views_count": 150,
        "duration": "30 minutes",
        "is_featured": true,
        "display_order": 1,
        "created_at": "2025-10-10T10:00:00Z",
        "updated_at": "2025-10-16T15:30:00Z"
      }
    ]
  }
}
```

---

#### 2. Get Featured Broadcast News
```
GET /api/cms/broadcast-news/featured/
```

**Response:**
```json
{
  "status_code": 200,
  "message": "Featured broadcast news fetched successfully",
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": {"en": "CEO Interview"},
      "slug": "ceo-interview",
      "channel_name": {"en": "News Network"},
      "broadcast_date": "2025-10-17T20:00:00Z",
      "thumbnail_image": "/media/broadcast_news/thumbnails/image.jpg",
      "description": {"en": "Exclusive interview"},
      "duration": "30 minutes",
      "views_count": 150
    }
  ]
}
```

---

#### 3. Get Single Broadcast News (with Interview Lines)
```
GET /api/cms/broadcast-news/{slug}/
```

**Note**: Auto-increments `views_count` on each access.

**Response:**
```json
{
  "status_code": 200,
  "message": "Broadcast news details fetched successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": {"en": "CEO Interview", "ar": "مقابلة الرئيس التنفيذي"},
    "slug": "ceo-interview",
    "channel_name": {"en": "News Network", "ar": "شبكة الأخبار"},
    "publication_name": {"en": "Business Weekly", "ar": "بزنس ويكلي"},
    "interviewer_name": {"en": "John Smith"},
    "interviewee_name": {"en": "Jane Doe"},
    "interview_date": "2025-10-15",
    "broadcast_date": "2025-10-17T20:00:00Z",
    "description": {"en": "Exclusive interview about the company's future vision"},
    "thumbnail_image": "/media/broadcast_news/thumbnails/interview.jpg",
    "article_url": "https://businessweekly.com/interviews/ceo-2025",
    "video_url": "https://youtube.com/watch?v=xxxxx",
    "video_file": "/media/broadcast_news/videos/interview.mp4",
    "status": "Published",
    "views_count": 151,
    "duration": "30 minutes",
    "meta_title": {"en": "CEO Interview - News Network"},
    "meta_description": {"en": "Watch exclusive interview with our CEO"},
    "is_featured": true,
    "display_order": 1,
    "details": [
      {
        "id": "detail-uuid-1",
        "speaker": {"en": "John Smith", "ar": "جون سميث"},
        "content": {"en": "Welcome to the show. Today we have a special guest.", "ar": "مرحبا بكم في البرنامج"},
        "timestamp": "00:00:30",
        "order": 1,
        "created_at": "2025-10-10T10:05:00Z",
        "updated_at": "2025-10-10T10:05:00Z"
      },
      {
        "id": "detail-uuid-2",
        "speaker": {"en": "Jane Doe", "ar": "جين دو"},
        "content": {"en": "Thank you for having me. It's a pleasure to be here.", "ar": "شكرا لاستضافتي"},
        "timestamp": "00:00:45",
        "order": 2,
        "created_at": "2025-10-10T10:05:00Z",
        "updated_at": "2025-10-10T10:05:00Z"
      },
      {
        "id": "detail-uuid-3",
        "speaker": {"en": "John Smith"},
        "content": {"en": "Let's talk about your company's vision for 2026."},
        "timestamp": "00:01:00",
        "order": 3,
        "created_at": "2025-10-10T10:05:00Z",
        "updated_at": "2025-10-10T10:05:00Z"
      }
    ],
    "created_at": "2025-10-10T10:00:00Z",
    "updated_at": "2025-10-16T15:30:00Z"
  }
}
```

---

### Admin Endpoints (Authentication Required)

#### 4. List All Broadcast News (Admin)
```
GET /api/cms/broadcast-news-management/
```

**Query Parameters:**
- `status` - Filter by status (`Draft` or `Published`)
- `is_featured` - Filter featured items (`true` or `false`)
- `search` - Search in title, channel, names, description
- `ordering` - Sort by field (e.g., `-broadcast_date`, `display_order`)
- `page` - Page number

**Response:** Same structure as public list endpoint

---

#### 5. Create Broadcast News
```
POST /api/cms/broadcast-news-management/
```

**Request Payload:**
```json
{
  "title": {
    "en": "Interview with CEO",
    "ar": "مقابلة مع الرئيس التنفيذي"
  },
  "channel_name": {
    "en": "News Network",
    "ar": "شبكة الأخبار"
  },
  "publication_name": {
    "en": "Business Weekly",
    "ar": "بزنس ويكلي"
  },
  "interviewer_name": {
    "en": "John Smith"
  },
  "interviewee_name": {
    "en": "Jane Doe"
  },
  "interview_date": "2025-10-15",
  "broadcast_date": "2025-10-17T20:00:00Z",
  "description": {
    "en": "An exclusive interview about company vision",
    "ar": "مقابلة حصرية حول رؤية الشركة"
  },
  "video_url": "https://youtube.com/watch?v=xxxxx",
  "status": "Published",
  "duration": "30 minutes",
  "meta_title": {
    "en": "CEO Interview - News Network"
  },
  "meta_description": {
    "en": "Watch our exclusive interview"
  },
  "is_featured": true,
  "display_order": 1,
  "details": [
    {
      "speaker": {"en": "John Smith", "ar": "جون سميث"},
      "content": {"en": "Welcome to the show", "ar": "مرحبا بكم"},
      "timestamp": "00:00:30",
      "order": 1
    },
    {
      "speaker": {"en": "Jane Doe", "ar": "جين دو"},
      "content": {"en": "Thank you for having me", "ar": "شكرا لاستضافتي"},
      "timestamp": "00:00:45",
      "order": 2
    },
    {
      "speaker": {"en": "John Smith"},
      "content": {"en": "Let's talk about your vision"},
      "timestamp": "00:01:00",
      "order": 3
    }
  ]
}
```

**Response:**
```json
{
  "status_code": 201,
  "message": "Broadcast news created successfully",
  "data": {
    "id": "newly-created-uuid",
    "slug": "interview-with-ceo",
    // ... all fields from request plus auto-generated fields
  }
}
```

**Notes:**
- `slug` is auto-generated from title
- `thumbnail_image` and `video_file` should be uploaded using multipart/form-data
- `details` array is optional during creation

---

#### 6. Get Single Broadcast News (Admin)
```
GET /api/cms/broadcast-news-management/{id}/
```

**Response:** Same structure as public detail endpoint

---

#### 7. Update Broadcast News
```
PATCH /api/cms/broadcast-news-management/{id}/
```

**Request Payload (Partial Update):**
```json
{
  "status": "Published",
  "is_featured": false,
  "details": [
    {
      "speaker": {"en": "John Smith"},
      "content": {"en": "Updated welcome message"},
      "timestamp": "00:00:30",
      "order": 1
    }
  ]
}
```

**Note:** Updating `details` replaces all existing interview lines.

**Response:**
```json
{
  "status_code": 200,
  "message": "Broadcast news updated successfully",
  "data": {
    // ... updated broadcast news object
  }
}
```

---

#### 8. Delete Broadcast News
```
DELETE /api/cms/broadcast-news-management/{id}/
```

**Response:**
```json
{
  "status_code": 204,
  "message": "Broadcast news deleted successfully"
}
```

**Note:** Performs soft delete (sets `deleted_at` timestamp)

---

## Translation Support

All text fields support multiple languages using JSONField:

```json
{
  "field_name": {
    "en": "English text",
    "ar": "نص عربي",
    "he": "טקסט בעברית",
    "ru": "Русский текст"
  }
}
```

---

## File Upload

For `thumbnail_image` and `video_file`, use `multipart/form-data`:

```bash
curl -X POST /api/cms/broadcast-news-management/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F 'title={"en":"Interview"}' \
  -F 'channel_name={"en":"News Network"}' \
  -F 'interview_date=2025-10-15' \
  -F 'status=Published' \
  -F 'thumbnail_image=@/path/to/image.jpg' \
  -F 'video_file=@/path/to/video.mp4'
```

---

## Quick Examples

### Fetch and Display Interview
```javascript
fetch('/api/cms/broadcast-news/ceo-interview/')
  .then(res => res.json())
  .then(data => {
    const news = data.data;
    console.log(`${news.title.en} - ${news.channel_name.en}`);

    // Display interview line by line
    news.details.forEach(line => {
      console.log(`[${line.timestamp}] ${line.speaker.en}: ${line.content.en}`);
    });
  });
```

### Create Broadcast News
```javascript
fetch('/api/cms/broadcast-news-management/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    title: {en: "New Interview"},
    channel_name: {en: "News Channel"},
    interview_date: "2025-10-20",
    status: "Published",
    details: [
      {
        speaker: {en: "Host"},
        content: {en: "Welcome"},
        timestamp: "00:00:10",
        order: 1
      }
    ]
  })
})
.then(res => res.json())
.then(data => console.log('Created:', data.data));
```

---

## Models

### BroadcastNews
- Multi-language fields: `title`, `channel_name`, `publication_name`, `interviewer_name`, `interviewee_name`, `description`, `meta_title`, `meta_description`
- Media: `thumbnail_image`, `video_url`, `video_file`
- URLs: `video_url`, `article_url`
- Status: `Draft` or `Published`
- Auto-fields: `slug` (from title), `views_count` (auto-incremented)

### BroadcastNewsDetail
- Multi-language fields: `speaker`, `content`
- Optional: `timestamp`
- Required: `order` (for sequencing)

---

## Implementation Files

**Created:**
- `cms/models/broadcast_news.py`
- `cms/serializers/broadcast_news_serializer.py`
- `cms/views/broadcast_news.py`
- `cms/migrations/0004_broadcastnews_broadcastnewsdetail.py`

**Modified:**
- `cms/models/__init__.py`
- `cms/admin.py`
- `cms/urls.py`

---

**Version**: 1.0
**Updated**: October 2025
