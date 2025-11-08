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

        if isinstance(value, dict):
            return value.get(lang_code) or value.get("en")
        return value

    def to_internal_value(self, data):
        """
        Method to convert the incoming data to the internal representation.
        Expects either:
        1. A string (will be stored as {"en": string})
        2. A dictionary with language codes as keys
        """
        if isinstance(data, str):
            return {"en": data}
        elif isinstance(data, dict):
            # Validate the data structure
            for key, value in data.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise serializers.ValidationError(
                        "Invalid translation format. Expected string values for language codes."
                    )
            return data
        raise serializers.ValidationError(
            "Invalid translation format. Expected string or dictionary."
        )
