from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from accounts.models import CompanyInfo
from accounts.serializers.company_info import CompanyInfoSerializer


class BaseCompanyInfoAPIView(TranslatedResponseMixin):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer


class CompanyInfoCreateAPIView(BaseCompanyInfoAPIView, ListCreateAPIView):
    def post(self, request, *args, **kwargs):
        if CompanyInfo.objects.exists():  # only one allowed
            return Response(
                {
                    "error": "Company info already exists. You can update the record if changes are needed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompanyInfoRetrieveUpdateAPIView(
    BaseCompanyInfoAPIView, RetrieveUpdateDestroyAPIView
):
    http_method_names = ["get", "patch"]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)

        instance = CompanyInfo.objects.first()
        if not instance:
            return Response(
                {"error": "Company info record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance = self.translate_instance(instance, lang_code)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=self.request.user)

        return Response(
            {
                "data": self.get_serializer(instance).data,
                "message": "Company info updated successfully.",
            },
            status=status.HTTP_200_OK,
        )
