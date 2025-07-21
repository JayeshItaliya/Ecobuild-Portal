import math


def calculate_reading_time(text):
    words = len(text.split())
    return math.ceil(words / 200)  # 200 words/minute average reading speed


import uuid


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
