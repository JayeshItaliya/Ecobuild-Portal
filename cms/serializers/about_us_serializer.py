"""
Serializers for About Us page functionality.
Unified API - Create entire About Us page with all related data in one call.

UNIFIED SERIALIZER:
    AboutUsPageUnifiedSerializer - Handles creation/update of complete About Us page
    Accepts nested data for:
    - team_members (list of team member objects)
    - timeline (list of timeline events)
    - achievements (list of awards/certifications)
    - sections (list of additional content sections)

    All data created/updated in a single database transaction.
    All translatable fields automatically translated to Hebrew, Russian, Arabic.

RESPONSE SERIALIZER:
    AboutUsPageResponseSerializer - Returns complete About Us page with all related data
    Returns translated content based on Accept-Language header

EXAMPLE REQUEST (Create everything):
    {
        "hero_title": {"en": "Welcome"},
        "company_name": {"en": "Ecobuild Solutions"},
        "team_members": [
            {"full_name": "John Doe", "job_title": {"en": "CEO"}, "bio": {"en": "..."}}
        ],
        "timeline": [{"year": 2004, "title": {"en": "Founded"}, "description": {"en": "..."}}],
        "achievements": [...],
        "sections": [...]
    }

FORM DATA SUPPORT:
    Now supports FormData for file uploads with JSON strings for nested fields:
    - hero_image, company_logo for main page
    - Separate file uploads for nested arrays using naming convention:
      * team_members_{index}_profile_image (for team member profile images)
      * timeline_{index}_image (for timeline entry images)
      * achievements_{index}_certificate_image (for achievement certificates)
      * Use index positions (0, 1, 2, etc.) for multiple items
"""

import logging

from django.db import transaction
from rest_framework import serializers

from accounts.mixins import TranslatedField
from cms.models.about_us import AboutUsPage
from cms.models.about_us import CompanyAchievement
from cms.models.about_us import CompanyTimeline
from cms.models.about_us import TeamMember

logger = logging.getLogger(__name__)

# ============================================================================
# NESTED SERIALIZERS FOR RELATED DATA
# ============================================================================


class TeamMemberNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for team members within About Us page."""

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "full_name",
            "job_title",
            "bio",
            "profile_image",
            "display_order",
            "is_leadership",
            "is_active",
        ]
        read_only_fields = ["id"]


class CompanyTimelineNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for timeline within About Us page."""

    class Meta:
        model = CompanyTimeline
        fields = [
            "id",
            "year",
            "title",
            "description",
            "image",
            "display_order",
            "is_active",
        ]
        read_only_fields = ["id"]


class CompanyAchievementNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for achievements within About Us page."""

    class Meta:
        model = CompanyAchievement
        fields = [
            "id",
            "title",
            "description",
            "awarded_by",
            "year",
            "certificate_image",
            "display_order",
            "is_active",
        ]
        read_only_fields = ["id"]


# ============================================================================
# UNIFIED ABOUT US PAGE SERIALIZER (SIMPLIFIED FOR ADMIN MANAGEMENT)
# ============================================================================


class AboutUsPageUnifiedSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for About Us page with essential related data.

    Frontend can send everything in one API call:
    - About Us page content (simplified fields)
    - Team members (essential fields only)
    - Company timeline
    - Achievements

    All data is created/updated in a single transaction.
    """

    # Nested related data
    team_members = TeamMemberNestedSerializer(many=True, required=False)
    timeline = CompanyTimelineNestedSerializer(many=True, required=False)
    achievements = CompanyAchievementNestedSerializer(many=True, required=False)

    class Meta:
        model = AboutUsPage
        fields = [
            "id",
            # Hero Section - Simplified
            "hero_title",
            "hero_subtitle",
            "hero_image",
            # Company Info - Essential only
            "company_name",
            "company_description",
            "founded_year",
            "company_logo",
            # Mission & Vision - Core values
            "mission_statement",
            "vision_statement",
            # Story - Simplified
            "our_story_title",
            "our_story_content",
            # SEO - Essential for website
            "meta_title",
            "meta_description",
            # Status
            "is_active",
            # Related data - Essential only
            "team_members",
            "timeline",
            "achievements",
            # Meta
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """
        Validate that only one About Us page can exist.
        """
        # Check if this is a create operation (no instance provided)
        if not self.instance:
            existing_page = AboutUsPage.objects.filter(deleted_at__isnull=True).first()
            if existing_page:
                raise serializers.ValidationError(
                    "About Us page already exists. Only one About Us page is allowed. Use the update endpoint to modify the existing page."
                )
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create About Us page with all related data in one transaction.
        """
        try:
            # Extract nested data
            team_members_data = validated_data.pop("team_members", [])
            timeline_data = validated_data.pop("timeline", [])
            achievements_data = validated_data.pop("achievements", [])

            # Create About Us page
            user = (
                self.context.get("request").user
                if self.context.get("request")
                else None
            )
            about_us_page = AboutUsPage.objects.create(
                **validated_data, created_by=user
            )

            # Create related data
            if team_members_data:
                self._create_team_members(team_members_data, user)
            if timeline_data:
                self._create_timeline(timeline_data, user)
            if achievements_data:
                self._create_achievements(achievements_data, user)

            return about_us_page

        except Exception as e:
            # Transaction will be rolled back automatically
            raise serializers.ValidationError(f"Error creating About Us page: {str(e)}")

    def update(self, instance, validated_data):
        """
        Update About Us page with all related data in one transaction.
        """
        # Extract nested data
        team_members_data = validated_data.pop("team_members", None)
        timeline_data = validated_data.pop("timeline", None)
        achievements_data = validated_data.pop("achievements", None)

        # Update About Us page fields
        user = self.context.get("request").user if self.context.get("request") else None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user
        instance.save()

        # Update related data if provided
        if team_members_data is not None:
            self._update_team_members(team_members_data, user)
        if timeline_data is not None:
            self._update_timeline(timeline_data, user)
        if achievements_data is not None:
            self._update_achievements(achievements_data, user)

        return instance

    def _create_team_members(self, team_members_data, user):
        """Create team members."""
        serializer = TeamMemberNestedSerializer(data=team_members_data, many=True)
        if serializer.is_valid():
            # Use serializer.save() for proper file handling, then set created_by
            team_members = serializer.save()
            if user:
                # Update created_by for all team members
                TeamMember.objects.filter(
                    id__in=[member.id for member in team_members]
                ).update(created_by=user)
        else:
            raise serializers.ValidationError(
                f"Team members validation error: {serializer.errors}"
            )

    def _update_team_members(self, team_members_data, user):
        """Update team members - replace all existing with new data."""
        # Delete existing team members
        TeamMember.objects.all().delete(soft=True, deleted_by_user=user)
        # Create new ones
        self._create_team_members(team_members_data, user)

    def _create_timeline(self, timeline_data, user):
        """Create timeline entries."""
        serializer = CompanyTimelineNestedSerializer(data=timeline_data, many=True)
        if serializer.is_valid():
            # Use serializer.save() for proper file handling, then set created_by
            timeline_entries = serializer.save()
            if user:
                # Update created_by for all timeline entries
                CompanyTimeline.objects.filter(
                    id__in=[entry.id for entry in timeline_entries]
                ).update(created_by=user)
        else:
            raise serializers.ValidationError(
                f"Timeline validation error: {serializer.errors}"
            )

    def _update_timeline(self, timeline_data, user):
        """Update timeline - replace all existing with new data."""
        CompanyTimeline.objects.all().delete(soft=True, deleted_by_user=user)
        self._create_timeline(timeline_data, user)

    def _create_achievements(self, achievements_data, user):
        """Create achievements."""
        serializer = CompanyAchievementNestedSerializer(
            data=achievements_data, many=True
        )
        if serializer.is_valid():
            # Use serializer.save() for proper file handling, then set created_by
            achievements = serializer.save()
            if user:
                # Update created_by for all achievements
                CompanyAchievement.objects.filter(
                    id__in=[achievement.id for achievement in achievements]
                ).update(created_by=user)
        else:
            raise serializers.ValidationError(
                f"Achievements validation error: {serializer.errors}"
            )

    def _update_achievements(self, achievements_data, user):
        """Update achievements - replace all existing with new data."""
        CompanyAchievement.objects.all().delete(soft=True, deleted_by_user=user)
        self._create_achievements(achievements_data, user)


# ============================================================================
# RESPONSE SERIALIZER WITH TRANSLATIONS
# ============================================================================


class TeamMemberResponseSerializer(serializers.ModelSerializer):
    """Team member with translated content."""

    full_name = TranslatedField()
    job_title = TranslatedField()
    bio = TranslatedField()

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "full_name",
            "job_title",
            "bio",
            "profile_image",
            "is_leadership",
            "display_order",
        ]


class CompanyTimelineResponseSerializer(serializers.ModelSerializer):
    """Timeline with translated content."""

    title = TranslatedField()
    description = TranslatedField()

    class Meta:
        model = CompanyTimeline
        fields = ["id", "year", "title", "description", "image", "display_order"]


class CompanyAchievementResponseSerializer(serializers.ModelSerializer):
    """Achievement with translated content."""

    title = TranslatedField()
    description = TranslatedField()
    awarded_by = TranslatedField()

    class Meta:
        model = CompanyAchievement
        fields = [
            "id",
            "title",
            "description",
            "awarded_by",
            "year",
            "certificate_image",
            "display_order",
        ]


class AboutUsPageResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer with all related data and translations.
    Returns translated content based on Accept-Language header.
    """

    # Translated fields - Simplified
    hero_title = TranslatedField()
    hero_subtitle = TranslatedField()
    company_name = TranslatedField()
    company_description = TranslatedField()
    mission_statement = TranslatedField()
    vision_statement = TranslatedField()
    our_story_title = TranslatedField()
    our_story_content = TranslatedField()
    meta_title = TranslatedField()
    meta_description = TranslatedField()

    # Related data with translations
    team_members = serializers.SerializerMethodField()
    timeline = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()

    class Meta:
        model = AboutUsPage
        fields = [
            "id",
            "hero_title",
            "hero_subtitle",
            "hero_image",
            "company_name",
            "company_description",
            "founded_year",
            "company_logo",
            "mission_statement",
            "vision_statement",
            "our_story_title",
            "our_story_content",
            "meta_title",
            "meta_description",
            "is_active",
            "team_members",
            "timeline",
            "achievements",
        ]

    def get_team_members(self, obj):
        """Get team members with translations."""
        team_members = TeamMember.objects.filter(is_active=True).order_by(
            "display_order"
        )
        request = self.context.get("request")
        if request:
            lang_code = request.headers.get("Accept-Language", "en").lower()
            # Translate team members
            from accounts.mixins import TranslatedResponseMixin

            mixin = TranslatedResponseMixin()
            team_members = mixin.translate_queryset(team_members, lang_code)
        return TeamMemberResponseSerializer(
            team_members, many=True, context=self.context
        ).data

    def get_timeline(self, obj):
        """Get timeline with translations."""
        timeline = CompanyTimeline.objects.filter(is_active=True).order_by(
            "-year", "display_order"
        )
        request = self.context.get("request")
        if request:
            lang_code = request.headers.get("Accept-Language", "en").lower()
            from accounts.mixins import TranslatedResponseMixin

            mixin = TranslatedResponseMixin()
            timeline = mixin.translate_queryset(timeline, lang_code)
        return CompanyTimelineResponseSerializer(
            timeline, many=True, context=self.context
        ).data

    def get_achievements(self, obj):
        """Get achievements with translations."""
        achievements = CompanyAchievement.objects.filter(is_active=True).order_by(
            "display_order"
        )
        request = self.context.get("request")
        if request:
            lang_code = request.headers.get("Accept-Language", "en").lower()
            from accounts.mixins import TranslatedResponseMixin

            mixin = TranslatedResponseMixin()
            achievements = mixin.translate_queryset(achievements, lang_code)
        return CompanyAchievementResponseSerializer(
            achievements, many=True, context=self.context
        ).data
