"""
Translation service for automatic content translation.
Supports Google Cloud Translation API with fallback to fake translator for testing.

Configuration in .env:
    USE_GOOGLE_TRANSLATE=true  # Enable Google Translation API
    GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json  # Path to credentials file

Supported languages: Hebrew (he), Russian (ru), Arabic (ar)
"""

import logging
import os
from typing import Dict

from django.conf import settings

logger = logging.getLogger(__name__)

# Supported translation languages - modify this list to add/remove languages
TARGET_LANGUAGES = ["he", "ru", "ar"]  # Hebrew, Russian, Arabic
BASE_LANGUAGE = "en"  # Source language for all translations


class FakeTranslator:
    """
    Development/testing translator - does NOT call Google API.
    Simulates translation by appending language code to the text.

    Used when:
    - USE_GOOGLE_TRANSLATE=false in .env
    - Google credentials are missing or invalid
    - Testing without API costs
    """

    def translate_text(self, text: str, target_lang: str) -> str:
        """Simulate translation by appending language code. No API calls made."""
        if not text:
            return ""
        return f"{text} [{target_lang}]"  # Returns: "Hello [he]" for Hebrew

    def generate_translations(
        self, base_text: str, base_lang: str = BASE_LANGUAGE
    ) -> dict:
        """Generate fake translations for all target languages."""
        translations = {base_lang: base_text}
        for lang in TARGET_LANGUAGES:
            translations[lang] = self.translate_text(base_text, lang)
        return translations


class GoogleTranslator:
    """
    Production translator using Google Cloud Translation API.

    Requirements:
    1. Google Cloud project with Translation API enabled
    2. Service account with "Cloud Translation API User" role
    3. JSON credentials file in project root
    4. Environment variables set in .env:
       - USE_GOOGLE_TRANSLATE=true
       - GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json

    Cost: FREE for first 500k characters/month, then $20 per 1M characters
    """

    def __init__(self):
        """Initialize Google Cloud Translation client with credentials."""
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Initialize the Google Cloud Translation client with proper error handling.
        Automatically loads credentials from the path specified in settings.
        """
        try:
            from google.cloud import translate_v2 as translate

            # Get credentials file path from settings (configured in backend/settings.py)
            credentials_path = getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", None)

            if credentials_path and os.path.exists(credentials_path):
                # Set environment variable for Google Cloud SDK
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                logger.info(f"Google Cloud credentials loaded from: {credentials_path}")
            elif credentials_path:
                logger.warning(
                    f"Google Cloud credentials file not found at: {credentials_path}"
                )
                raise FileNotFoundError(
                    f"Credentials file not found: {credentials_path}"
                )

            # Initialize the client
            self.client = translate.Client()
            logger.info("Google Cloud Translation API client initialized successfully")

        except ImportError as e:
            logger.error(
                "google-cloud-translate package not installed. "
                "Run: pip install google-cloud-translate"
            )
            raise ImportError(
                "Google Cloud Translation library not installed. "
                "Please install it with: pip install google-cloud-translate"
            ) from e

        except Exception as e:
            logger.error(f"Failed to initialize Google Translation client: {str(e)}")
            raise RuntimeError(
                f"Failed to initialize Google Cloud Translation API: {str(e)}"
            ) from e

    def translate_text(self, text: str, target_lang: str) -> str:
        """
        Translate text to target language using Google Cloud Translation API.

        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'he', 'ru', 'ar')

        Returns:
            Translated text or empty string on error

        Raises:
            Exception: If translation fails
        """
        if not text or not text.strip():
            return ""

        if not self.client:
            raise RuntimeError("Google Translation client not initialized")

        try:
            # Call Google Cloud Translation API
            result = self.client.translate(
                text, target_language=target_lang, source_language=BASE_LANGUAGE
            )

            translated_text = result.get("translatedText", "")

            logger.debug(
                f"Translated text to {target_lang}: {text[:50]}... -> {translated_text[:50]}..."
            )

            return translated_text

        except Exception as e:
            logger.error(f"Translation failed for language '{target_lang}': {str(e)}")
            # Re-raise to allow calling code to handle the error
            raise Exception(f"Translation to {target_lang} failed: {str(e)}") from e

    def generate_translations(
        self, base_text: str, base_lang: str = BASE_LANGUAGE
    ) -> Dict[str, str]:
        """
        Generate translations for all target languages.

        Args:
            base_text: Text in base language to translate
            base_lang: Base language code (default: 'en')

        Returns:
            Dictionary mapping language codes to translated text
            Example: {"en": "Hello", "he": "שלום", "ru": "Привет", "ar": "مرحبا"}
        """
        translations = {base_lang: base_text}

        if not base_text or not base_text.strip():
            # Return empty translations for empty input
            for lang in TARGET_LANGUAGES:
                translations[lang] = ""
            return translations

        for lang in TARGET_LANGUAGES:
            try:
                translations[lang] = self.translate_text(base_text, lang)
            except Exception as e:
                logger.error(
                    f"Failed to translate to {lang}, using original text: {str(e)}"
                )
                # Fallback: use original text if translation fails
                translations[lang] = base_text

        return translations


def get_translator():
    """
    Factory function to get the appropriate translator instance.

    Automatically selects the right translator based on configuration:
    - GoogleTranslator: When USE_GOOGLE_TRANSLATE=true (production)
    - FakeTranslator: When USE_GOOGLE_TRANSLATE=false (development/testing)

    Returns:
        Translator instance (GoogleTranslator or FakeTranslator)
    """
    use_google = getattr(settings, "USE_GOOGLE_TRANSLATE", False)

    if use_google:
        try:
            logger.info("Initializing Google Cloud Translation API")
            return GoogleTranslator()
        except Exception as e:
            logger.warning(
                f"Failed to initialize Google Translator, falling back to FakeTranslator: {str(e)}"
            )
            return FakeTranslator()
    else:
        logger.info("Using FakeTranslator for development/testing")
        return FakeTranslator()


# Global translator instance - automatically initialized when Django starts
# Use this instance throughout the project for all translations
# Example: from accounts.translation import translator; translator.translate_text("Hello", "he")
translator = get_translator()
