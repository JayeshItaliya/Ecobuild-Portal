import random,string
def generate_password(length=12):
    """Generate a random strong password."""
    # Define the characters to use in the password
    characters = string.ascii_letters + string.digits

    # Generate the password randomly
    password = "".join(random.choice(characters) for _ in range(length))

    return password
