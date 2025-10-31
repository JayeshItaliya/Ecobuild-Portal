# Product API

This document describes the Product API endpoints for managing products with category and subcategory support. The API supports multilingual responses and filtering by category hierarchy.

## Base URLs
- **GET**    `/api/cms/product/`                     - Public endpoint to list products (with filtering)
- **POST**   `/api/cms/product/`                      - Admin endpoint to create a product
- **GET**    `/api/cms/product/<uuid:pk>/`            - Public endpoint to get a single product
- **PATCH**  `/api/cms/product/<uuid:pk>/`            - Admin endpoint to update a product
- **DELETE** `/api/cms/product/<uuid:pk>/`           - Admin endpoint to delete a product

## Language Support
- Send `Accept-Language` header with one of: `en`, `ar`, `he`, `ru`
- Defaults to `en` if not provided
- All translatable fields (title, subtitle, category names) are automatically translated

## Response Format
All responses use this format:
```json
{
  "status_code": 200,
  "data": { ... },
  "message": "..."
}
```

## Authentication
- **GET** endpoints are public (no authentication required)
- **POST/PATCH/DELETE** endpoints require admin authentication

---

## 1. List Products

### Request
```http
GET /api/cms/product/
Accept-Language: he
```

### Query Parameters (Optional)
- `category` - Filter by any category ID (parent or subcategory)
- `parent_category` - Filter by parent category ID only
- `subcategory` - Filter by subcategory ID only
- `search` - Search in product title
- `ordering` - Order by `created_at` or `updated_at` (use `-created_at` for descending)
- `page` - Page number for pagination
- `page_size` - Items per page (default: 10)

### Response (200)
```json
{
  "status_code": 200,
  "data": {
    "total_count": 25,
    "count": 10,
    "next": "http://api.example.com/api/cms/product/?page=2",
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "מוצר בנייה ירוקה",
        "subtitle": "פתרון בנייה בת קיימא",
        "category": {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "name": "חומרי בנייה"
        },
        "parent_category": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "name": "בנייה"
        },
        "sections": [],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "Products fetched successfully"
}
```

### Filtering Examples
```http
# Get products by category
GET /api/cms/product/?category=550e8400-e29b-41d4-a716-446655440000

# Get products by parent category
GET /api/cms/product/?parent_category=770e8400-e29b-41d4-a716-446655440002

# Get products by subcategory
GET /api/cms/product/?subcategory=660e8400-e29b-41d4-a716-446655440001

# Search and paginate
GET /api/cms/product/?search=green&page=2&page_size=20
```

---

## 2. Get Single Product

### Request
```http
GET /api/cms/product/550e8400-e29b-41d4-a716-446655440000/
Accept-Language: ar
```

### Response (200)
```json
{
  "status_code": 200,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "منتج البناء الأخضر",
    "subtitle": "حل البناء المستدام",
    "category": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "مواد البناء"
    },
    "parent_category": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "البناء"
    },
    "sections": [
      {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "product": {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "title": "منتج البناء الأخضر"
        },
        "order": 1,
        "section_type": "text",
        "content_text": "وصف تفصيلي للمنتج",
        "content_image": "https://example.com/image.jpg",
        "content_file": null,
        "image_position": "center"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Product fetched successfully"
}
```

---

## 3. Create Product (Admin)

### Request
```http
POST /api/cms/product/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
Accept-Language: en
```

### Payload
```json
{
  "title": {
    "en": "Green Building Product",
    "ar": "منتج البناء الأخضر",
    "he": "מוצר בנייה ירוקה",
    "ru": "Экологический строительный продукт"
  },
  "subtitle": {
    "en": "Sustainable building solution",
    "ar": "حل البناء المستدام",
    "he": "פתרון בנייה בת קיימא"
  },
  "category": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Note:**
- `title` and `subtitle` are JSON objects with language codes as keys
- `category` is the UUID of an existing ProductCategory
- Only `title` and `category` are required
- `subtitle` is optional

### Response (201)
```json
{
  "status_code": 201,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Green Building Product",
    "subtitle": "Sustainable building solution",
    "category": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Building Materials"
    },
    "parent_category": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Construction"
    },
    "sections": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Product created successfully."
}
```

### Error Response (400)
```json
{
  "status_code": 400,
  "data": {
    "category": ["Product category with id 123 does not exist."]
  },
  "error": "Product creation failed. Please check the provided data."
}
```

---

## 4. Update Product (Admin)

### Request
```http
PATCH /api/cms/product/550e8400-e29b-41d4-a716-446655440000/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
Accept-Language: he
```

### Payload (Partial Update)
```json
{
  "title": {
    "en": "Updated Product Name",
    "he": "שם מוצר מעודכן"
  },
  "category": "770e8400-e29b-41d4-a716-446655440002"
}
```

**Note:** All fields are optional in PATCH requests. Only include fields you want to update.

### Response (200)
```json
{
  "status_code": 200,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "שם מוצר מעודכן",
    "subtitle": "פתרון בנייה בת קיימא",
    "category": {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "בנייה"
    },
    "parent_category": null,
    "sections": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T14:20:00Z"
  },
  "message": "Product updated successfully."
}
```

---

## 5. Delete Product (Admin)

### Request
```http
DELETE /api/cms/product/550e8400-e29b-41d4-a716-446655440000/
Authorization: Bearer YOUR_TOKEN
```

### Response (204)
```json
{
  "status_code": 204,
  "data": null,
  "message": "Product deleted successfully."
}
```

---

## Field Descriptions

### Product Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Product unique identifier |
| `title` | JSON Object | Yes | Product title in multiple languages: `{"en": "...", "ar": "...", "he": "...", "ru": "..."}` |
| `subtitle` | JSON Object | No | Product subtitle in multiple languages |
| `category` | UUID | Yes | Category ID (must exist) |
| `parent_category` | Object | Auto | Parent category info (only if category is a subcategory) |
| `sections` | Array | Auto | Product sections array (read-only) |
| `created_at` | DateTime | Auto | Creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

### Category Object (in response)
```json
{
  "id": "uuid",
  "name": "translated category name"
}
```

### Section Object (in response)
```json
{
  "id": "uuid",
  "product": { "id": "uuid", "title": "string" },
  "order": 1,
  "section_type": "text|image|video",
  "content_text": "translated text",
  "content_image": "url or null",
  "content_file": "url or null",
  "image_position": "left|center|right"
}
```

---

## Quick Examples

### JavaScript/Fetch
```javascript
// List products with Hebrew translation
const response = await fetch('/api/cms/product/', {
  headers: {
    'Accept-Language': 'he'
  }
});
const data = await response.json();

// Create product (Admin)
const createResponse = await fetch('/api/cms/product/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'Accept-Language': 'en'
  },
  body: JSON.stringify({
    title: {
      en: "Green Building Product",
      he: "מוצר בנייה ירוקה"
    },
    subtitle: {
      en: "Sustainable solution"
    },
    category: "660e8400-e29b-41d4-a716-446655440001"
  })
});

// Filter by category
const filtered = await fetch(
  '/api/cms/product/?category=660e8400-e29b-41d4-a716-446655440001',
  { headers: { 'Accept-Language': 'ar' } }
);
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status_code": 400,
  "data": {
    "category": ["Product category with id {uuid} does not exist."]
  },
  "error": "Product creation failed. Please check the provided data."
}
```

### 401 Unauthorized
```json
{
  "status_code": 401,
  "data": null,
  "message": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "status_code": 404,
  "data": null,
  "message": "Not found."
}
```

---

## Notes

1. **Multilingual Support**: Always send `Accept-Language` header to get responses in the desired language
2. **Category Validation**: Category ID must exist in the system. Use the Product Category API to get available categories
3. **Pagination**: List endpoint returns paginated results with `total_count`, `count`, `next`, `previous`, and `results`
4. **Soft Delete**: DELETE operation performs soft delete (not permanent)
5. **Filtering**: You can combine multiple query parameters (e.g., `?category=xxx&search=green&ordering=-created_at`)
