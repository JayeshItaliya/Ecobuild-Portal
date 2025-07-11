import random
import string

from accounts.models import User


def generate_password(length=12):
    """Generate a random strong password."""
    # Define the characters to use in the password
    characters = string.ascii_letters + string.digits

    # Generate the password randomly
    password = "".join(random.choice(characters) for _ in range(length))

    return password


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain part of it.
    """
    email = email or ""
    try:
        email_name, domain_part = email.strip().rsplit("@", 1)
    except ValueError:
        pass
    else:
        email = email_name + "@" + domain_part.lower()
    return email


def create_google_user(self, email, google_account_id, **user_model_kwargs):
    """
    Create a google user given an email and google account id
    """

    if not email:
        raise ValueError("messages.EMAIL_REQUIRED_ERROR")
    if not google_account_id:
        raise ValueError("messages.GOOGLE_CLIENT_ID_REQUIRED_ERROR")

    user = User.objects.create(
        email=normalize_email(email),
        google_account_id=google_account_id,
        **user_model_kwargs,
    )
    user.save()
    return user
