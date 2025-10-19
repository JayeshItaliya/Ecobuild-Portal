"""
Unified About Us API - One endpoint for everything.
Frontend can create/update entire About Us page in a single API call.

API ENDPOINTS:
    GET    /api/cms/about-us/              - Get complete About Us page (public, no auth)
    POST   /api/cms/about-us/create/       - Create everything in one call (admin, requires auth)
    PATCH  /api/cms/about-us/{id}/update/  - Update everything in one call (admin, requires auth)
    DELETE /api/cms/about-us/{id}/delete/  - Delete About Us page (admin, requires auth)

USAGE EXAMPLES (Frontend):

    // JSON Request (No file uploads)
    const response = await fetch('/api/cms/about-us/create/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer YOUR_TOKEN',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            hero_title: { en: "Welcome to Ecobuild" },
            company_name: { en: "Ecobuild Solutions" },
            team_members: [
                { full_name: "John Doe", job_title: { en: "CEO" }, bio: { en: "..." } }
            ],
            timeline: [
                { year: 2004, title: { en: "Founded" }, description: { en: "..." } }
            ],
            achievements: [...],
            sections: [...]
        })
    });

    // FormData Request (With file uploads)
    const formData = new FormData();
    formData.append('hero_title', JSON.stringify({ en: "Welcome to Ecobuild" }));
    formData.append('company_name', JSON.stringify({ en: "Ecobuild Solutions" }));
    formData.append('hero_image', fileInput.files[0]); // File upload

    // Team members data as JSON string (no files in nested structure)
    formData.append('team_members', JSON.stringify([
        { full_name: "John Doe", job_title: { en: "CEO" }, bio: { en: "..." } }
    ]));

    // Separate file uploads using naming convention: array_field_index_file_field
    formData.append('team_members_0_profile_image', profileImageFile); // For first team member's profile image
    formData.append('timeline_0_image', timelineImageFile); // For first timeline entry's image
    formData.append('achievements_0_certificate_image', certificateFile); // For first achievement's certificate

    const response = await fetch('/api/cms/about-us/create/', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer YOUR_TOKEN' },
        body: formData // No Content-Type header needed for FormData
    });

    // Get About Us in Hebrew
    const response = await fetch('/api/cms/about-us/', {
        headers: { 'Accept-Language': 'he' }
    });
    // Returns all content translated to Hebrew!

FEATURES:
    ✅ One API call creates: About Us page + Team + Timeline + Achievements + Sections
    ✅ Automatic translation to Hebrew, Russian, Arabic
    ✅ Response includes all related data with translations
    ✅ Language selection via Accept-Language header
    ✅ Supports both JSON and FormData for file uploads
"""

import json
import logging

from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from accounts.mixins import TranslatedResponseMixin
from backend.utils import generic_response
from cms.models.about_us import AboutUsPage
from cms.serializers.about_us_serializer import AboutUsPageResponseSerializer
from cms.serializers.about_us_serializer import AboutUsPageUnifiedSerializer


def parse_form_data_for_about_us(data):
    """
    Parse FormData to handle JSON strings for nested fields and translatable fields.
    Also handles separate file uploads for nested arrays using naming convention.

    This function converts JSON strings from FormData into proper Python objects
    for nested fields like team_members, timeline, achievements, and translatable fields.

    File upload naming convention supported:
    - team_members_{index}_profile_image
    - timeline_{index}_image
    - achievements_{index}_certificate_image

    Where {index} is the array position (0, 1, 2, etc.)
    """
    parsed_data = {}
    separate_files = {}  # Store separate file uploads for later mapping

    # Fields that should be parsed as JSON (translatable fields and nested lists)
    json_fields = [
        "hero_title",
        "hero_subtitle",
        "company_name",
        "company_description",
        "mission_statement",
        "vision_statement",
        "our_story_title",
        "our_story_content",
        "meta_title",
        "meta_description",
        "team_members",
        "timeline",
        "achievements",
    ]

    for key, value in data.items():
        # Check if this is a separate file upload with naming convention
        if _is_nested_file_field(key):
            separate_files[key] = value
        elif key in json_fields and isinstance(value, str):
            # Only parse if it looks like JSON (starts with { or [)
            if value.strip().startswith(("{", "[")):
                try:
                    parsed_data[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError) as e:
                    logging.warning(f"Failed to parse JSON for field {key}: {e}")
                    # Keep the original string value if parsing fails
                    parsed_data[key] = value
            else:
                parsed_data[key] = value
        else:
            parsed_data[key] = value

    # Map separate file uploads to nested arrays
    if separate_files:
        parsed_data = _map_separate_files_to_nested_arrays(parsed_data, separate_files)

    return parsed_data


def _is_nested_file_field(field_name):
    """
    Check if field name follows the nested file naming convention.

    Supported patterns:
    - team_members_{index}_profile_image
    - timeline_{index}_image
    - achievements_{index}_certificate_image
    """
    import re

    patterns = [
        r"^team_members_\d+_profile_image$",
        r"^timeline_\d+_image$",
        r"^achievements_\d+_certificate_image$",
    ]

    return any(re.match(pattern, field_name) for pattern in patterns)


def _map_separate_files_to_nested_arrays(parsed_data, separate_files):
    """
    Map separate file uploads to their correct positions in nested arrays.

    Args:
        parsed_data: The main parsed data dictionary
        separate_files: Dictionary of separate file uploads with naming convention
    """
    import re

    for field_name, file_obj in separate_files.items():
        if field_name.startswith("team_members_"):
            # Extract index from team_members_{index}_profile_image
            match = re.match(r"team_members_(\d+)_profile_image", field_name)
            if match and "team_members" in parsed_data:
                index = int(match.group(1))
                if (
                    isinstance(parsed_data["team_members"], list)
                    and len(parsed_data["team_members"]) > index
                ):
                    parsed_data["team_members"][index]["profile_image"] = file_obj

        elif field_name.startswith("timeline_"):
            # Extract index from timeline_{index}_image
            match = re.match(r"timeline_(\d+)_image", field_name)
            if match and "timeline" in parsed_data:
                index = int(match.group(1))
                if (
                    isinstance(parsed_data["timeline"], list)
                    and len(parsed_data["timeline"]) > index
                ):
                    parsed_data["timeline"][index]["image"] = file_obj

        elif field_name.startswith("achievements_"):
            # Extract index from achievements_{index}_certificate_image
            match = re.match(r"achievements_(\d+)_certificate_image", field_name)
            if match and "achievements" in parsed_data:
                index = int(match.group(1))
                if (
                    isinstance(parsed_data["achievements"], list)
                    and len(parsed_data["achievements"]) > index
                ):
                    parsed_data["achievements"][index]["certificate_image"] = file_obj

    return parsed_data


@api_view(["GET"])
@permission_classes([AllowAny])
def get_about_us(request):
    """
    GET /api/cms/about-us/

    Get complete About Us page with all related data.
    Returns translated content based on Accept-Language header.

    Public endpoint - no authentication required.

    Response includes:
    - About Us page content
    - Team members
    - Company timeline
    - Achievements
    - Additional sections

    All content automatically translated to requested language.
    """
    try:
        # Get active About Us page
        about_us_page = AboutUsPage.objects.filter(is_active=True).first()

        if not about_us_page:
            return generic_response(
                message="No active About Us page found",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Get language from request using mixin and translate the instance
        mixin = TranslatedResponseMixin()
        lang_code = mixin.get_language_code(request)
        about_us_page = mixin.translate_instance(about_us_page, lang_code)

        # Serialize with all related data
        serializer = AboutUsPageResponseSerializer(
            about_us_page, context={"request": request}
        )

        return generic_response(
            message="About Us page retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return generic_response(
            message=f"Error retrieving About Us page: {str(e)}",
            error_message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_about_us(request):
    """
    POST /api/cms/about-us/create/

    Create complete About Us page with all related data in ONE API call.

    IMPORTANT: Only one About Us page is allowed. If a page already exists,
    this endpoint will return a 409 Conflict error with instructions to use
    the update endpoint instead.

    Authentication required (admin only).

    SUPPORTS BOTH JSON AND FORMDATA:
    - JSON: Send Content-Type: application/json with JSON payload
    - FormData: Send Content-Type: multipart/form-data with JSON strings for nested fields

    For FormData, send JSON strings for nested/translatable fields and separate files:
    - hero_title='{"en": "Welcome", "ar": "مرحبا"}'
    - team_members='[{"full_name": "John", "job_title": {"en": "CEO"}}]'

    File uploads for nested arrays use naming convention:
    - team_members_0_profile_image (for first team member's profile image)
    - timeline_0_image (for first timeline entry's image)
    - achievements_0_certificate_image (for first achievement's certificate image)
    - Use index positions (0, 1, 2, etc.) for multiple items

    Request body can include:
    {
      "hero_title": {"en": "Welcome..."},
      "hero_subtitle": {"en": "..."},
      "company_name": {"en": "..."},
      "company_description": {"en": "..."},
      "founded_year": 2004,
      "years_of_experience": 20,
      "team_members": [
        {
          "full_name": "John Doe",
          "job_title": {"en": "CEO"},
          "bio": {"en": "..."},
          "email": "john@example.com",
          "is_leadership": true
        }
      ],
      "timeline": [
        {
          "year": 2004,
          "title": {"en": "Company Founded"},
          "description": {"en": "..."}
        }
      ],
      "achievements": [...],
      "sections": [...]
    }

    All translatable fields will be auto-translated to Hebrew, Russian, Arabic.
    """
    try:
        # Check if About Us page already exists
        existing_page = AboutUsPage.objects.filter(deleted_at__isnull=True).first()
        if existing_page:
            error_message = "About Us page already exists. Only one About Us page is allowed. Use the update endpoint to modify the existing page."
            return generic_response(
                message=error_message,
                data={
                    "existing_page_id": str(existing_page.id),
                    "update_url": f"/api/cms/about-us/{existing_page.id}/update/",
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        # Parse FormData if needed (for file uploads and JSON strings)
        data = request.data
        content_type = getattr(request, "content_type", "") or request.META.get(
            "CONTENT_TYPE", ""
        )

        # Check if this is FormData and needs JSON parsing
        # Also check if we have any string values that look like JSON for known fields
        is_form_data = "multipart/form-data" in content_type
        has_json_strings = any(
            isinstance(data.get(key), str)
            and data.get(key, "").strip().startswith(("{", "["))
            for key in [
                "hero_title",
                "company_name",
                "team_members",
                "timeline",
                "achievements",
            ]
            if key in data
        )

        if is_form_data or has_json_strings:
            data = parse_form_data_for_about_us(data)

        # Validate the data first
        serializer = AboutUsPageUnifiedSerializer(
            data=data, context={"request": request}
        )

        if not serializer.is_valid():
            return generic_response(
                message="Invalid data provided",
                data={"errors": serializer.errors, "received_data": request.data},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Create the About Us page
        about_us_page = serializer.save()

        # Return response with all data
        response_serializer = AboutUsPageResponseSerializer(
            about_us_page, context={"request": request}
        )

        return generic_response(
            message="About Us page created successfully with all related data",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    except serializers.ValidationError as e:
        return generic_response(
            message="Validation error while creating About Us page",
            data={
                "error": str(e),
                "detail": e.detail if hasattr(e, "detail") else None,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        # Log the full error for debugging (server-side only)
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating About Us page: {str(e)}", exc_info=True)

        return generic_response(
            message=f"Error creating About Us page: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_about_us(request, pk):
    """
    PATCH /api/cms/about-us/{id}/update/

    Update complete About Us page with all related data in ONE API call.

    Authentication required (admin only).

    SUPPORTS BOTH JSON AND FORMDATA:
    - JSON: Send Content-Type: application/json with JSON payload
    - FormData: Send Content-Type: multipart/form-data with JSON strings for nested fields

    For FormData, send JSON strings for nested/translatable fields and separate files:
    - hero_title='{"en": "Welcome", "ar": "مرحبا"}'
    - team_members='[{"full_name": "John", "job_title": {"en": "CEO"}}]'

    File uploads for nested arrays use naming convention:
    - team_members_0_profile_image (for first team member's profile image)
    - timeline_0_image (for first timeline entry's image)
    - achievements_0_certificate_image (for first achievement's certificate image)
    - Use index positions (0, 1, 2, etc.) for multiple items

    Can update:
    - About Us page content
    - Team members (replaces all existing)
    - Timeline (replaces all existing)
    - Achievements (replaces all existing)
    - Sections (replaces all existing)

    Only include fields you want to update.
    If you include nested data (team_members, timeline, etc.),
    it will replace ALL existing data for that type.
    """
    try:
        about_us_page = AboutUsPage.objects.get(id=pk)

        # Parse FormData if needed (for file uploads and JSON strings)
        data = request.data
        content_type = getattr(request, "content_type", "") or request.META.get(
            "CONTENT_TYPE", ""
        )

        # Check if this is FormData and needs JSON parsing
        # Also check if we have any string values that look like JSON for known fields
        is_form_data = "multipart/form-data" in content_type
        has_json_strings = any(
            isinstance(data.get(key), str)
            and data.get(key, "").strip().startswith(("{", "["))
            for key in [
                "hero_title",
                "company_name",
                "team_members",
                "timeline",
                "achievements",
            ]
            if key in data
        )

        if is_form_data or has_json_strings:
            data = parse_form_data_for_about_us(data)

        serializer = AboutUsPageUnifiedSerializer(
            about_us_page,
            data=data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            about_us_page = serializer.save()

            # Return response with all data
            response_serializer = AboutUsPageResponseSerializer(
                about_us_page, context={"request": request}
            )

            return generic_response(
                message="About Us page updated successfully",
                data=response_serializer.data,
                status_code=status.HTTP_200_OK,
            )

        return generic_response(
            message="Invalid data",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except AboutUsPage.DoesNotExist:
        return generic_response(
            message="About Us page not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        # Log the full error for debugging (server-side only)
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating About Us page: {str(e)}", exc_info=True)

        return generic_response(
            message=f"Error updating About Us page: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_about_us(request, pk):
    """
    DELETE /api/cms/about-us/{id}/

    Delete About Us page (soft delete).

    Authentication required (admin only).
    """
    try:
        about_us_page = AboutUsPage.objects.get(id=pk)
        about_us_page.delete(deleted_by_user=request.user, soft=True)

        return generic_response(
            message="About Us page deleted successfully",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    except AboutUsPage.DoesNotExist:
        return generic_response(
            message="About Us page not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        # Log the full error for debugging (server-side only)
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting About Us page: {str(e)}", exc_info=True)

        return generic_response(
            message=f"Error deleting About Us page: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
