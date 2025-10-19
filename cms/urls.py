from django.urls import path
from rest_framework.routers import DefaultRouter

from cms.views.about_us import create_about_us
from cms.views.about_us import delete_about_us
from cms.views.about_us import get_about_us
from cms.views.about_us import update_about_us
from cms.views.blog_management import BlogManagementListCreateAPIView
from cms.views.blog_management import BlogManagementRetrieveUpdateDestroyAPIView
from cms.views.broadcast_news import BroadcastNewsFeaturedView
from cms.views.broadcast_news import BroadcastNewsManagementViewSet
from cms.views.broadcast_news import BroadcastNewsPublicDetailView
from cms.views.broadcast_news import BroadcastNewsPublicListView
from cms.views.contact import ContactMessageListCreateAPIView
from cms.views.contact import ContactMessageRetrieveUpdateDestroyAPIView
from cms.views.document import DocumentAccessViewSet
from cms.views.document import DocumentViewSet
from cms.views.faq import FAQListCreateAPIView
from cms.views.faq import FAQRetrieveUpdateDestroyAPIView
from cms.views.gallery.gallery import GalleryListCreateAPIView
from cms.views.gallery.gallery import GalleryRetrieveUpdateDestroyAPIView
from cms.views.gallery.gallery_category import GalleryCategoryChoicesAPIView
from cms.views.gallery.gallery_category import GalleryCategoryListCreateAPIView
from cms.views.gallery.gallery_category import (
    GalleryCategoryRetrieveUpdateDestroyAPIView,
)
from cms.views.notification import AdminNotificationListAPIView
from cms.views.product.product import ProductListCreateAPIView
from cms.views.product.product import ProductRetrieveUpdateDestroyAPIView
from cms.views.product.product_category import ProductCategoryListCreateAPIView
from cms.views.product.product_category import (
    ProductCategoryRetrieveUpdateDestroyAPIView,
)

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"document-access", DocumentAccessViewSet, basename="document-access")
router.register(
    r"broadcast-news-management",
    BroadcastNewsManagementViewSet,
    basename="broadcast-news-management",
)

urlpatterns = [
    path(
        "admin-notifications/",
        AdminNotificationListAPIView.as_view(),
        name="admin-notification-list",
    ),
    # About Us
    path("about-us/", get_about_us, name="about-us-get"),
    path("about-us/create/", create_about_us, name="about-us-create"),
    path("about-us/<uuid:pk>/update/", update_about_us, name="about-us-update"),
    path("about-us/<uuid:pk>/delete/", delete_about_us, name="about-us-delete"),
    # Blog
    path(
        "blog-management/",
        BlogManagementListCreateAPIView.as_view(),
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
        GalleryListCreateAPIView.as_view(),
        name="gallery-list-crete",
    ),
    path(
        "gallery/<str:pk>/",
        GalleryRetrieveUpdateDestroyAPIView.as_view(),
        name="gallery-retrive-update-delete",
    ),
    path(
        "gallery-category-choices/",
        GalleryCategoryChoicesAPIView.as_view(),
        name="gallery-category-choices",
    ),
    path(
        "contact-messages/",
        ContactMessageListCreateAPIView.as_view(),
        name="contact-message-list-create",
    ),
    path(
        "contact-messages/<str:pk>/",
        ContactMessageRetrieveUpdateDestroyAPIView.as_view(),
        name="contact-message-detail",
    ),
    path("faq/", FAQListCreateAPIView.as_view(), name="faq-list-create"),
    path("faq/<str:pk>/", FAQRetrieveUpdateDestroyAPIView.as_view(), name="faq-detail"),
    path(
        "product-category/",
        ProductCategoryListCreateAPIView.as_view(),
        name="product-category-list-create",
    ),
    path(
        "product-category/<str:pk>/",
        ProductCategoryRetrieveUpdateDestroyAPIView.as_view(),
        name="product-category-detail-update-delete",
    ),
    path(
        "product/",
        ProductListCreateAPIView.as_view(),
        name="product-list-create",
    ),
    path(
        "product/<str:pk>/",
        ProductRetrieveUpdateDestroyAPIView.as_view(),
        name="product-retrieve-update-destroy",
    ),
    # Broadcast News - Public Endpoints
    path(
        "broadcast-news/",
        BroadcastNewsPublicListView.as_view(),
        name="broadcast-news-public-list",
    ),
    path(
        "broadcast-news/featured/",
        BroadcastNewsFeaturedView.as_view(),
        name="broadcast-news-featured",
    ),
    path(
        "broadcast-news/<slug:slug>/",
        BroadcastNewsPublicDetailView.as_view(),
        name="broadcast-news-public-detail",
    ),
]

urlpatterns += router.urls
