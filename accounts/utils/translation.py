from typing import Dict

TARGET_LANGUAGES = ["he", "ru", "ar"]
BASE_LANGUAGE = "en"


class FakeTranslator:
    """
    Fake translator for development/testing only.
    Replace with GoogleTranslator when you set up credentials.
    """

    def translate_text(self, text: str, target_lang: str) -> str:
        return f"{text} [{target_lang}]"  # fake translation format

    def generate_translations(
        self, base_text: str, base_lang: str = BASE_LANGUAGE
    ) -> Dict[str, str]:
        translations = {base_lang: base_text}
        for lang in TARGET_LANGUAGES:
            translations[lang] = self.translate_text(base_text, lang)
        return translations


# TODO Uncomment code when we get google translation APIs

# from google.cloud import translate_v2 as translate
# from django.conf import settings

# TARGET_LANGUAGES = ['he', 'ru', 'ar']

# class GoogleTranslator:
#     def __init__(self):
#         self.client = translate.Client()

#     def translate_text(self, text: str, target_lang: str):
#         if not text:
#             return ""
#         result = self.client.translate(text, target_language=target_lang)
#         return result.get("translatedText", "")

#     def generate_translations(self, base_text: str, base_lang: str = "en") -> dict:
#         translations = {base_lang: base_text}
#         for lang in TARGET_LANGUAGES:
#             translations[lang] = self.translate_text(base_text, lang)
#         return translations
