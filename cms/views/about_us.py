"""
Unified About Us API - One endpoint for everything.
Frontend can create/update entire About Us page in a single API call.

API ENDPOINTS:
    GET    /api/cms/about-us/              - Get complete About Us page (public, no auth)
    POST   /api/cms/about-us/create/       - Create everything in one call (admin, requires auth)
    PATCH  /api/cms/about-us/{id}/update/  - Update everything in one call (admin, requires auth)
    DELETE /api/cms/about-us/{id}/delete/  - Delete About Us page (admin, requires auth)

USAGE EXAMPLE (Frontend):
    // Create complete About Us page with all data
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
"""

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

        # Validate the data first
        serializer = AboutUsPageUnifiedSerializer(
            data=request.data, context={"request": request}
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

        serializer = AboutUsPageUnifiedSerializer(
            about_us_page,
            data=request.data,
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
