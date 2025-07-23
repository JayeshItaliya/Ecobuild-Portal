from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from cms.views.blog_management import BlogManagementListCreateAPIVIew
from cms.views.blog_management import BlogManagementRetrieveUpdateDestroyAPIView
from cms.views.document import DocumentAccessViewSet
from cms.views.document import DocumentViewSet

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"document-access", DocumentAccessViewSet, basename="document-access")

urlpatterns = [
    path("", include(router.urls)),
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
]
