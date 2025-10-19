"""
Model translation utilities for automatic field translation.
Provides mixin for Django models to auto-translate JSONField content.

HOW IT WORKS:
1. Add TRANSLATABLE_FIELDS list to your model
2. Fields are automatically translated when model.save() is called
3. Translations stored in JSONField format: {"en": "text", "he": "...", "ru": "...", "ar": "..."}

EXAMPLE:
    class FAQ(BaseTranslatableModel):
        question = JSONField(default=dict)
        answer = JSONField(default=dict)
        TRANSLATABLE_FIELDS = ["question", "answer"]  # Auto-translate these fields

    faq = FAQ.objects.create(question={"en": "Hello?"})
    # Automatically saved as: {"en": "Hello?", "he": "שלום?", "ru": "Здравствуй?", "ar": "مرحبا؟"}
"""

import logging
from typing import List

from accounts.translation import TARGET_LANGUAGES
from accounts.translation import translator

logger = logging.getLogger(__name__)


class AutoTranslateMixin:
    """
    Mixin for Django models to auto-translate selected fields' values.

    Include this mixin in your model and define TRANSLATABLE_FIELDS.
    All fields in TRANSLATABLE_FIELDS will be automatically translated
    to Hebrew (he), Russian (ru), and Arabic (ar) when the model is saved.
    """

    TRANSLATABLE_FIELDS: List[str] = []  # Define this in your model class

    def auto_translate_fields(self):
        """
        Automatically translate all fields listed in TRANSLATABLE_FIELDS.
        Called automatically before model.save().

        Process for each field:
        1. Convert string to dict: "Hello" -> {"en": "Hello"}
        2. Check for missing languages (he, ru, ar)
        3. Translate missing languages using Google Translation API
        4. Update field with all translations

        If translation fails, uses English text as fallback (no errors raised).
        """
        if not self.TRANSLATABLE_FIELDS:
            # No fields to translate, skip
            logger.debug(
                f"{self.__class__.__name__} has no TRANSLATABLE_FIELDS defined"
            )
            return

        for field_name in self.TRANSLATABLE_FIELDS:
            try:
                self._translate_field(field_name)
            except Exception as e:
                logger.error(
                    f"Error translating field '{field_name}' in {self.__class__.__name__}: {str(e)}",
                    exc_info=True,
                )
                # Continue with other fields even if one fails

    def _translate_field(self, field_name: str):
        """
        Translate a single field to all target languages.

        Handles three input formats:
        - String: "Hello" -> {"en": "Hello", "he": "שלום", ...}
        - Dict with English only: {"en": "Hello"} -> adds translations
        - Dict with some languages: Only fills missing ones

        Args:
            field_name: Name of the field to translate
        """
        # Get current value from the model instance
        value = getattr(self, field_name, None)

        if value is None:
            logger.debug(f"Field '{field_name}' is None, skipping translation")
            return

        # STEP 1: Convert plain string to dictionary format
        # Example: "Hello" becomes {"en": "Hello"}
        if isinstance(value, str):
            if not value.strip():
                value = {"en": ""}  # Empty string -> empty dict
            else:
                value = {"en": value}  # Convert to dict format
            logger.debug(f"Normalized string field '{field_name}' to dict format")

        # STEP 2: Add missing language translations
        if isinstance(value, dict):
            # Find which language has content (could be any language, not just English)
            # Priority: en, he, ru, ar (check in order)
            all_supported_langs = ["en"] + TARGET_LANGUAGES  # en, he, ru, ar
            base_text = ""
            source_lang = None

            # Find first language with content
            for lang in all_supported_langs:
                if lang in value and value[lang] and value[lang].strip():
                    base_text = value[lang]
                    source_lang = lang
                    break

            if not base_text or not base_text.strip():
                # If no content in any language, set all languages to empty
                for lang in all_supported_langs:
                    if lang not in value:
                        value[lang] = ""
            else:
                # Translate from source language to all other languages
                # Include English if source is not English
                target_langs_to_translate = []

                # Add English if it's missing and source is not English
                if source_lang != "en" and (
                    "en" not in value or not value.get("en", "").strip()
                ):
                    target_langs_to_translate.append("en")

                # Add target languages (he, ru, ar) if they're missing
                for lang in TARGET_LANGUAGES:
                    if lang != source_lang and (
                        lang not in value or not value.get(lang, "").strip()
                    ):
                        target_langs_to_translate.append(lang)

                if target_langs_to_translate:
                    logger.debug(
                        f"Translating field '{field_name}' from {source_lang} to: {target_langs_to_translate}"
                    )

                    for target_lang in target_langs_to_translate:
                        try:
                            # Translate from source_lang to target_lang
                            if source_lang == "en":
                                # English to other language (existing behavior)
                                translated_text = translator.translate_text(
                                    base_text, target_lang
                                )
                            else:
                                # Non-English to other language (including English)
                                # Google Translate auto-detects source language or we can specify
                                translated_text = self._translate_any_to_any(
                                    base_text, source_lang, target_lang
                                )

                            value[target_lang] = translated_text
                            logger.debug(
                                f"Successfully translated '{field_name}' from {source_lang} to {target_lang}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to translate '{field_name}' to {target_lang}: {str(e)}"
                            )
                            # Fallback: use base text if translation fails
                            value[target_lang] = base_text

            # Update the field with translated values
            setattr(self, field_name, value)

        elif not isinstance(value, (str, dict, type(None))):
            logger.warning(
                f"Field '{field_name}' has unexpected type {type(value).__name__}, "
                f"expected str or dict. Skipping translation."
            )

    def _translate_any_to_any(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """
        Translate text from any source language to any target language.

        Supports translation between any combination of en, he, ru, ar.
        Uses Google Translate which auto-detects source language or uses specified source.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'he', 'ru', 'ar')
            target_lang: Target language code (e.g., 'en', 'he', 'ru', 'ar')

        Returns:
            Translated text
        """
        try:
            # Use the translator's translate method
            # For non-English sources, we need to handle differently
            if hasattr(translator, "client") and translator.client:
                # Google Translator - supports any language pair
                result = translator.client.translate(
                    text, target_language=target_lang, source_language=source_lang
                )
                return result.get("translatedText", text)
            else:
                # FakeTranslator - just append language code
                return f"{text} [{target_lang}]"
        except Exception as e:
            logger.error(
                f"Translation failed from {source_lang} to {target_lang}: {str(e)}"
            )
            return text  # Return original text as fallback

    def save(self, *args, **kwargs):
        """
        Override save method to automatically translate fields before saving.

        Called automatically when you do: model.save() or Model.objects.create(...)
        Translations happen BEFORE the data is saved to database.

        If translation fails, the model is still saved (with English text only).
        Check Django logs for translation errors.
        """
        try:
            # Translate all TRANSLATABLE_FIELDS before saving
            self.auto_translate_fields()
        except Exception as e:
            # Log error but don't prevent saving
            logger.error(
                f"Translation failed for {self.__class__.__name__}, saving anyway: {str(e)}"
            )

        # Call parent save method to actually save to database
        super().save(*args, **kwargs)
