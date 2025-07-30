from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from cms.views.blog_management import BlogManagementListCreateAPIVIew
from cms.views.blog_management import BlogManagementRetrieveUpdateDestroyAPIView
from cms.views.document import DocumentAccessViewSet
from cms.views.document import DocumentViewSet
from cms.views.gallery.gallery import GalleryListAPIView
from cms.views.gallery.gallery import GalleryRetrieveUpdateDestroyAPIView
from cms.views.gallery.gallery_category import GalleryCategoryListCreateAPIView
from cms.views.gallery.gallery_category import (
    GalleryCategoryRetrieveUpdateDestroyAPIView,
)

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"document-access", DocumentAccessViewSet, basename="document-access")

urlpatterns = [
    path("", include(router.urls)),
    # Blog
    path(
        "blog-management/",
        BlogManagementListCreateAPIVIew.as_view(),
        name="blog-management",
    ),
    path(
        "blog-management/<str:pk>/",
        BlogManagementRetrieveUpdateDestroyAPIView.as_view(),
        name="blog-management",
    ),
    # Gallery Category
    path(
        "gallery-category/",
        GalleryCategoryListCreateAPIView.as_view(),
        name="gallery-category-list-create",
    ),
    path(
        "gallery-category/<str:pk>/",
        GalleryCategoryRetrieveUpdateDestroyAPIView.as_view(),
        name="gallery-category-update-delete",
    ),
    path(
        "gallery/",
        GalleryListAPIView.as_view(),
        name="gallery-list-crete",
    ),
    path(
        "gallery/<str:pk>/",
        GalleryRetrieveUpdateDestroyAPIView.as_view(),
        name="gallery-retrive-update-delete",
    ),
]
