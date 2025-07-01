from accounts.utils.translation import FakeTranslator

translator = FakeTranslator()


class AutoTranslateMixin:
    """
    Mixin to auto-translate model fields to multiple languages.
    Should be used with models that contain JSONFields for translations.
    """

    TRANSLATABLE_FIELDS = []

    def auto_translate_fields(self):
        for field in self.TRANSLATABLE_FIELDS:
            field_value = getattr(self, field)
            if isinstance(field_value, dict) and "en" in field_value:
                continue  # Already translated
            base_text = field_value if isinstance(field_value, str) else None
            if base_text:
                translations = translator.generate_translations(base_text)
                setattr(self, field, translations)

    def save(self, *args, **kwargs):
        self.auto_translate_fields()
        super().save(*args, **kwargs)
