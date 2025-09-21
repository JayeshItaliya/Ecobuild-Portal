class TranslatedResponseMixin:
    def get_language_code(self, request):
        return request.headers.get("Accept-Language", "en").lower()

    def translate_instance(self, instance, lang_code):
        if hasattr(instance, "TRANSLATABLE_FIELDS"):
            for field in instance.TRANSLATABLE_FIELDS:
                field_val = getattr(instance, field, {})
                if isinstance(field_val, dict):
                    translated_value = field_val.get(lang_code) or field_val.get("en")
                    setattr(instance, field, translated_value)
        return instance

    def translate_queryset(self, queryset, lang_code):
        return [self.translate_instance(obj, lang_code) for obj in queryset]

from rest_framework import serializers
class TranslatedField(serializers.Field):
    def to_representation(self, value):
        request = self.context.get("request")
        lang_code = "en"
        if request:
            lang_code = request.headers.get("Accept-Language", "en").lower()
            print("Language code from request:", lang_code)

        if isinstance(value, dict):
            return value.get(lang_code) or value.get("en")
        return value