from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from accounts.models import CompanyInfo
from accounts.serializers.company_info import CompanyInfoSerializer


class BaseCompanyInfoAPIView(TranslatedResponseMixin):
    """Base API view for CompanyInfo, provides queryset, serializer, and permissions."""

    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CompanyInfoCreateAPIView(BaseCompanyInfoAPIView, ListCreateAPIView):
    """Create the CompanyInfo record (only one allowed)."""

    def post(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            return Response(
                {
                    "error": "Company info already exists. You can update the record if changes are needed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "data": self.get_serializer(instance).data,
                "message": "Company info created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class CompanyInfoRetrieveUpdateAPIView(
    BaseCompanyInfoAPIView, RetrieveUpdateDestroyAPIView
):
    """Retrieve or update the single CompanyInfo record."""

    http_method_names = ["get", "patch"]

    def get(self, request, *args, **kwargs):
        """Retrieve the company info (translated if language provided)."""
        lang_code = self.get_language_code(request)
        instance = self.get_queryset().first()
        if not instance:
            return Response(
                {"error": "Company info record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        instance = self.translate_instance(instance, lang_code)
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """Update the company info record."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=request.user)
        return Response(
            {
                "data": self.get_serializer(instance).data,
                "message": "Company info updated successfully.",
            },
            status=status.HTTP_200_OK,
        )
