"""
Validation utilities for content and translation fields.
Provides security validation to prevent malicious input and control API costs.
"""

from django.core.exceptions import ValidationError

# Maximum characters per translatable field to prevent API abuse and excessive costs
MAX_TRANSLATION_LENGTH = 10000  # 10,000 characters per field


def validate_translation_text_length(
    text: str, max_length: int = MAX_TRANSLATION_LENGTH
) -> str:
    """
    Validate text length before translation to prevent API abuse.

    Args:
        text: Text to validate
        max_length: Maximum allowed length

    Returns:
        The original text if valid

    Raises:
        ValidationError: If text exceeds max_length
    """
    if not text:
        return text

    if len(text) > max_length:
        raise ValidationError(
            f"Text too long for translation. Maximum {max_length} characters allowed. "
            f"Current length: {len(text)} characters."
        )

    return text


def validate_translation_dict(
    value: dict, max_length: int = MAX_TRANSLATION_LENGTH
) -> dict:
    """
    Validate a translation dictionary (JSONField with language keys).

    Args:
        value: Dictionary with language codes as keys
        max_length: Maximum allowed length for each text value

    Returns:
        The original dict if valid

    Raises:
        ValidationError: If any value exceeds max_length
    """
    if not isinstance(value, dict):
        return value

    for lang_code, text in value.items():
        if isinstance(text, str):
            validate_translation_text_length(text, max_length)

    return value


# Optional: HTML sanitization utilities
# Uncomment and use if you need to allow HTML in your content
# Requires: pip install bleach

# import bleach
#
# ALLOWED_HTML_TAGS = ['p', 'br', 'strong', 'em', 'u', 'b', 'i', 'a', 'ul', 'ol', 'li']
# ALLOWED_HTML_ATTRIBUTES = {'a': ['href', 'title']}
#
# def sanitize_html_content(text: str) -> str:
#     """
#     Sanitize HTML content to prevent XSS attacks.
#
#     Args:
#         text: HTML text to sanitize
#
#     Returns:
#         Sanitized text with only allowed tags and attributes
#     """
#     if not text:
#         return text
#
#     return bleach.clean(
#         text,
#         tags=ALLOWED_HTML_TAGS,
#         attributes=ALLOWED_HTML_ATTRIBUTES,
#         strip=True
#     )
