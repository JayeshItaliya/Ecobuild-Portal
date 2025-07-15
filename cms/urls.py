from django.urls import path, include
from cms.views.document import DocumentAccessViewSet, DocumentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'document-access', DocumentAccessViewSet, basename='document-access')

urlpatterns = [
    path('', include(router.urls)),
]