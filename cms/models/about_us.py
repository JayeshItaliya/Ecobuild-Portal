"""
About Us models for company information and content management.
Supports multi-language content with automatic translation.
"""

from django.db import models
from django.db.models import JSONField

from backend.models import BaseTranslatableModel


class AboutUsPage(BaseTranslatableModel):
    """
    Main About Us page content.
    Supports multiple sections with rich content and automatic translation.
    """

    # Hero Section
    hero_title = JSONField(default=dict, help_text="Main hero title")
    hero_subtitle = JSONField(default=dict, help_text="Hero subtitle/tagline")
    hero_description = JSONField(default=dict, help_text="Hero description text")
    hero_image = models.ImageField(
        upload_to="about_us/hero/", null=True, blank=True, help_text="Hero banner image"
    )
    hero_video_url = models.URLField(
        null=True, blank=True, help_text="Optional hero video URL"
    )

    # Company Overview
    company_name = JSONField(default=dict, help_text="Company name")
    company_tagline = JSONField(default=dict, help_text="Company tagline/slogan")
    company_description = JSONField(default=dict, help_text="Main company description")
    founded_year = models.IntegerField(null=True, blank=True, help_text="Year founded")
    company_logo = models.ImageField(upload_to="about_us/logos/", null=True, blank=True)

    # Mission & Vision
    mission_statement = JSONField(default=dict, help_text="Company mission statement")
    vision_statement = JSONField(default=dict, help_text="Company vision statement")
    core_values = JSONField(
        default=list,
        help_text="List of core values (each item should be a dict with 'title' and 'description')",
    )

    # Company Story
    our_story_title = JSONField(default=dict, help_text="Story section title")
    our_story_content = JSONField(default=dict, help_text="Company story/history")
    our_story_image = models.ImageField(
        upload_to="about_us/story/", null=True, blank=True
    )

    # Statistics/Achievements
    years_of_experience = models.IntegerField(
        null=True, blank=True, help_text="Years in business"
    )
    projects_completed = models.IntegerField(
        null=True, blank=True, help_text="Number of completed projects"
    )
    satisfied_clients = models.IntegerField(
        null=True, blank=True, help_text="Number of clients"
    )
    team_members_count = models.IntegerField(
        null=True, blank=True, help_text="Number of team members"
    )

    # Call to Action
    cta_title = JSONField(default=dict, help_text="Call-to-action title")
    cta_description = JSONField(default=dict, help_text="Call-to-action description")
    cta_button_text = JSONField(default=dict, help_text="CTA button text")
    cta_button_link = models.URLField(null=True, blank=True, help_text="CTA link URL")

    # SEO
    meta_title = JSONField(default=dict, help_text="Page meta title for SEO")
    meta_description = JSONField(
        default=dict, help_text="Page meta description for SEO"
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this page is currently active"
    )

    # Translatable fields - will auto-translate when saved
    TRANSLATABLE_FIELDS = [
        "hero_title",
        "hero_subtitle",
        "hero_description",
        "company_name",
        "company_tagline",
        "company_description",
        "mission_statement",
        "vision_statement",
        "our_story_title",
        "our_story_content",
        "cta_title",
        "cta_description",
        "cta_button_text",
        "meta_title",
        "meta_description",
    ]

    class Meta:
        db_table = "about_us_page"
        verbose_name = "About Us Page"
        verbose_name_plural = "About Us Pages"

    def __str__(self):
        company = (
            self.company_name.get("en", "About Us")
            if isinstance(self.company_name, dict)
            else "About Us"
        )
        return f"About Us - {company}"


class TeamMember(BaseTranslatableModel):
    """
    Team member/leadership information for About Us page.
    """

    # Personal Information
    full_name = models.CharField(max_length=255, help_text="Full name")
    job_title = JSONField(default=dict, help_text="Job title/position")
    bio = JSONField(default=dict, help_text="Biography/description")

    # Contact & Social
    email = models.EmailField(null=True, blank=True, help_text="Contact email")
    phone = models.CharField(max_length=20, null=True, blank=True, help_text="Phone")
    linkedin_url = models.URLField(null=True, blank=True, help_text="LinkedIn profile")
    twitter_url = models.URLField(null=True, blank=True, help_text="Twitter profile")

    # Media
    profile_image = models.ImageField(
        upload_to="about_us/team/", null=True, blank=True, help_text="Profile photo"
    )

    # Display
    display_order = models.IntegerField(
        default=0, help_text="Display order (lower numbers first)"
    )
    is_leadership = models.BooleanField(
        default=False, help_text="Is this person part of leadership team?"
    )
    is_active = models.BooleanField(default=True, help_text="Show on website?")

    # Translatable fields
    TRANSLATABLE_FIELDS = ["job_title", "bio"]

    class Meta:
        db_table = "team_member"
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ["display_order", "full_name"]

    def __str__(self):
        return f"{self.full_name} - {self.job_title.get('en', '') if isinstance(self.job_title, dict) else ''}"


class CompanyTimeline(BaseTranslatableModel):
    """
    Company milestones and timeline for About Us page.
    """

    year = models.IntegerField(help_text="Year of milestone")
    title = JSONField(default=dict, help_text="Milestone title")
    description = JSONField(default=dict, help_text="Milestone description")
    image = models.ImageField(
        upload_to="about_us/timeline/",
        null=True,
        blank=True,
        help_text="Timeline image",
    )
    display_order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True, help_text="Show on website?")

    TRANSLATABLE_FIELDS = ["title", "description"]

    class Meta:
        db_table = "company_timeline"
        verbose_name = "Company Timeline"
        verbose_name_plural = "Company Timeline"
        ordering = ["-year", "display_order"]  # Most recent first

    def __str__(self):
        title = (
            self.title.get("en", "Milestone")
            if isinstance(self.title, dict)
            else "Milestone"
        )
        return f"{self.year} - {title}"


class CompanyAchievement(BaseTranslatableModel):
    """
    Company awards, certifications, and achievements.
    """

    title = JSONField(default=dict, help_text="Achievement title")
    description = JSONField(default=dict, help_text="Achievement description")
    awarded_by = JSONField(default=dict, help_text="Organization/entity that awarded")
    year = models.IntegerField(null=True, blank=True, help_text="Year received")
    certificate_image = models.ImageField(
        upload_to="about_us/achievements/",
        null=True,
        blank=True,
        help_text="Certificate/award image",
    )
    display_order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True, help_text="Show on website?")

    TRANSLATABLE_FIELDS = ["title", "description", "awarded_by"]

    class Meta:
        db_table = "company_achievement"
        verbose_name = "Company Achievement"
        verbose_name_plural = "Company Achievements"
        ordering = ["display_order", "-year"]

    def __str__(self):
        title = (
            self.title.get("en", "Achievement")
            if isinstance(self.title, dict)
            else "Achievement"
        )
        return f"{title} ({self.year})" if self.year else title


class AboutUsSection(BaseTranslatableModel):
    """
    Flexible additional sections for About Us page.
    Allows admin to add custom sections with different content types.
    """

    SECTION_TYPES = [
        ("text", "Text Content"),
        ("text_image", "Text with Image"),
        ("image_text", "Image with Text"),
        ("features", "Feature List"),
        ("statistics", "Statistics"),
        ("quote", "Quote/Testimonial"),
        ("video", "Video"),
    ]

    section_type = models.CharField(
        max_length=20, choices=SECTION_TYPES, default="text"
    )
    title = JSONField(default=dict, help_text="Section title")
    subtitle = JSONField(default=dict, help_text="Section subtitle")
    content = JSONField(default=dict, help_text="Main content")

    # Media
    image = models.ImageField(upload_to="about_us/sections/", null=True, blank=True)
    video_url = models.URLField(null=True, blank=True, help_text="Video URL")

    # Additional data (for features, statistics, etc.)
    additional_data = JSONField(
        default=dict,
        blank=True,
        help_text="Additional structured data (e.g., feature list, stats)",
    )

    # Display
    display_order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True, help_text="Show on website?")

    TRANSLATABLE_FIELDS = ["title", "subtitle", "content"]

    class Meta:
        db_table = "about_us_section"
        verbose_name = "About Us Section"
        verbose_name_plural = "About Us Sections"
        ordering = ["display_order"]

    def __str__(self):
        title = (
            self.title.get("en", "Section")
            if isinstance(self.title, dict)
            else "Section"
        )
        return f"{self.section_type.title()} - {title}"
