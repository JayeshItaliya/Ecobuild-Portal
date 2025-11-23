# Role and Permission Management System

## Overview

This document describes the comprehensive role and permission management system implemented for the Ecobuild Portal. The system allows administrators to dynamically create roles and assign granular permissions to control user access to different content types and API endpoints.

## Key Features

- **Dynamic Role Creation**: Admins can create custom roles with specific permissions
- **Granular Permissions**: Fine-grained control over what users can access
- **Subscription-based Access**: Permission levels tied to user subscription tiers
- **API Endpoint Protection**: Automatic permission checking for API endpoints
- **Admin Panel Integration**: Full admin interface for managing roles and permissions

## Models

### 1. Permission Model
```python
class Permission(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    resource_type = models.CharField(max_length=50, choices=PermissionResourceChoices.choices)
    action = models.CharField(max_length=20, choices=ActionType.choices)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    api_endpoint = models.CharField(max_length=200, blank=True, null=True)
    http_methods = models.JSONField(default=list, blank=True)
```

### 2. RolePermission Model
```python
class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    is_granted = models.BooleanField(default=True)
    subscription_level = models.CharField(max_length=20, choices=SubscriptionTypeChoices.choices, blank=True, null=True)
```

### 3. Updated Role Model
```python
class Role(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_system_role = models.BooleanField(default=False)
    subscription_required = models.CharField(max_length=20, choices=SubscriptionTypeChoices.choices, default=SubscriptionTypeChoices.FREE)
```

### 4. Updated User Model
The User model now includes:
- `subscription_type`: Current subscription level
- `subscription_expires_at`: When subscription expires
- Enhanced permission checking methods:
  - `has_permission(permission_codename)`
  - `has_permission_for_resource(resource_type, action)`
  - `get_all_permissions()`

## Permission Classes

### Custom Permission Classes
Located in `accounts/permissions.py`:

1. **CustomPermission**: Base permission class for specific permission checking
2. **HasResourcePermission**: Checks permissions based on resource type and action
3. **HasSubscriptionLevel**: Validates subscription level requirements
4. **IsOwnerOrHasPermission**: Allows access if user is owner or has permission
5. **Predefined permissions** for common use cases:
   - `CanViewProducts`, `CanCreateProducts`, `CanEditProducts`, `CanDeleteProducts`
   - `CanViewBlogs`, `CanViewDocuments`, `CanDownloadCADFiles`
   - `CanViewLearningVideos`, `CanManageUsers`, `CanManageRoles`

## API Endpoints

### Role Management
- `GET /api/account/role/` - List all roles
- `POST /api/account/role/` - Create new role
- `GET /api/account/role/<id>/` - Get role details
- `PATCH /api/account/role/<id>/` - Update role
- `DELETE /api/account/role/<id>/` - Delete role

### Permission Management
- `GET /api/account/permissions/` - List all permissions
- `POST /api/account/permissions/` - Create new permission
- `GET /api/account/permissions/<id>/` - Get permission details
- `PATCH /api/account/permissions/<id>/` - Update permission
- `DELETE /api/account/permissions/<id>/` - Delete permission
- `GET /api/account/permissions/by-resource-type/` - Get permissions grouped by resource type

### Role-Permission Management
- `GET /api/account/role/<role_id>/permissions/` - Get permissions for a role
- `POST /api/account/role/permissions/bulk-update/` - Bulk update role permissions

## Resource Types and Actions

### Resource Types (PermissionResourceChoices)
- `product` - Product information and details
- `product_category` - Product categories
- `blog` - Blog posts and articles
- `document` - General documents
- `gallery` - Image galleries
- `user` - User management
- `role` - Role management
- `permission` - Permission management
- `cms_content` - CMS content
- `learning_video` - Tutorial and learning videos (Premium)
- `cad_file` - CAD files and technical documents (Premium)
- `company_info` - Company information
- `notification` - System notifications
- `faq` - Frequently asked questions

### Actions (ActionType)
- `CREATE` - Create new resources
- `UPDATE` - Modify existing resources
- `DELETE` - Remove resources
- `VIEW` - Read/view resources

## Subscription Levels

### SubscriptionTypeChoices
- `FREE` - Basic access to public content
- `BASIC` - Standard access with some premium features
- `PREMIUM` - Access to learning videos and CAD files
- `ENTERPRISE` - Full administrative access

## Usage Examples

### 1. Protecting an API View
```python
from accounts.permissions import CanViewProducts, HasResourcePermission

class ProductListAPIView(ListAPIView):
    permission_classes = [CanViewProducts]

    # Or for more granular control:
    def get_permissions(self):
        if self.request.method == 'GET':
            return [CanViewProducts()]
        elif self.request.method == 'POST':
            return [HasResourcePermission('product', 'create')()]
        return [IsAuthenticated()]
```

### 2. Checking Permissions in Code
```python
# Check if user has specific permission
if request.user.has_permission('view_learning_video'):
    # Show premium content
    pass

# Check resource-based permission
if request.user.has_permission_for_resource('product', 'create'):
    # Allow product creation
    pass
```

### 3. Admin Interface Usage

1. **Create Role**: Go to Django Admin → Roles → Add Role
   - Enter role name and description
   - Select subscription requirement level
   - Save

2. **Assign Permissions**:
   - Edit the role
   - In the "Role permissions" section
   - Add permissions and set subscription levels

3. **Assign Role to User**:
   - Go to Users → Select User
   - Assign the role from dropdown
   - Set subscription type and expiration

## Setup Instructions

### 1. Run Migrations
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### 2. Create Default Permissions and Roles
```bash
python manage.py setup_permissions
```

This command will:
- Create all standard permissions for each resource type and action
- Create default roles (Admin, Editor, Viewer, Premium User)
- Assign appropriate permissions to each role

### 3. Verify Setup
1. Access Django Admin panel
2. Check that roles and permissions are created
3. Verify that users can be assigned roles
4. Test API endpoints with different permission levels

## Integration with Frontend

The system is designed to work with the Berry template React frontend. The API provides:

1. **Role and Permission Data**: Frontend can fetch available roles and permissions
2. **User Permission Checking**: API can validate user permissions before showing UI elements
3. **Subscription-based UI**: Different UI components can be shown based on subscription level

## Security Considerations

1. **Permission Override**: Superusers bypass all permission checks
2. **Subscription Expiration**: Expired subscriptions fall back to free level
3. **System Roles**: System roles cannot be deleted
4. **API Protection**: All endpoints protected with appropriate permission classes
5. **Audit Trail**: All changes tracked through activity logs

## Best Practices

1. **Principle of Least Privilege**: Assign minimum required permissions
2. **Regular Audits**: Review role assignments and permissions periodically
3. **Subscription Management**: Monitor subscription levels and expiration dates
4. **Testing**: Test permission changes in development before production

This system provides a robust foundation for managing user access and ensuring that content is appropriately protected based on user roles and subscription levels.
