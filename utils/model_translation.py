from accounts.translation import TARGET_LANGUAGES
from accounts.translation import FakeTranslator

translator = FakeTranslator()


class AutoTranslateMixin:
    """
    Mixin for models to auto-translate selected fields' values.
    """

    TRANSLATABLE_FIELDS = []

    def auto_translate_fields(self):
        for field in self.TRANSLATABLE_FIELDS:
            value = getattr(self, field)

            # STEP 1: Normalize str to dict {"en": value}
            if isinstance(value, str):
                value = {"en": value}

            # STEP 2: Fill missing translations
            if isinstance(value, dict):
                base_text = value.get("en", "")
                for lang in TARGET_LANGUAGES:
                    if lang not in value:
                        value[lang] = translator.translate_text(base_text, lang)

                setattr(self, field, value)

    def save(self, *args, **kwargs):
        self.auto_translate_fields()
        super().save(*args, **kwargs)
