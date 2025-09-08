import django_filters

from accounts.models import User
from cms.models.blog import BlogPost
from cms.models.blog import ContactMessage
from cms.models.document import Document
from cms.models.faq import FAQ
from cms.models.gallery import Gallery
from cms.models.gallery import GalleryCategory
from cms.models.product import ProductCategory


class BlogPostFilter(django_filters.FilterSet):
    """Filter set for BlogPost model."""

    title = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFromToRangeFilter()
    created_by = django_filters.NumberFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = BlogPost
        fields = ["title", "created_at", "created_by", "is_active"]


class GalleryFilter(django_filters.FilterSet):
    """Filter set for Gallery model."""

    category = django_filters.NumberFilter()
    created_at = django_filters.DateTimeFromToRangeFilter()
    created_by = django_filters.NumberFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Gallery
        fields = ["category", "created_at", "created_by", "is_active"]


class GalleryCategoryFilter(django_filters.FilterSet):
    """Filter set for GalleryCategory model."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFromToRangeFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = GalleryCategory
        fields = ["name", "created_at", "is_active"]


class ProductCategoryFilter(django_filters.FilterSet):
    """Filter set for ProductCategory model."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    parent = django_filters.NumberFilter()
    created_at = django_filters.DateTimeFromToRangeFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = ProductCategory
        fields = ["name", "parent", "created_at", "is_active"]


class FAQFilter(django_filters.FilterSet):
    """Filter set for FAQ model."""

    question = django_filters.CharFilter(lookup_expr="icontains")
    answer = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFromToRangeFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = FAQ
        fields = ["question", "answer", "created_at", "is_active"]


class ContactMessageFilter(django_filters.FilterSet):
    """Filter set for ContactMessage model."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    message = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message", "created_at"]


class DocumentFilter(django_filters.FilterSet):
    """Filter set for Document model."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFromToRangeFilter()
    created_by = django_filters.NumberFilter()

    class Meta:
        model = Document
        fields = ["name", "created_at", "created_by"]


class TeamMemberFilter(django_filters.FilterSet):
    """Filter set for User model (Team Members)."""

    email = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()
    role = django_filters.NumberFilter()

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active", "role"]
