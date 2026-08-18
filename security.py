import hashlib

MIN_PASSWORD_LENGHT = 8

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    if len(password) < MIN_PASSWORD_LENGHT:
        print(
            f"Password must be atleast "
            f"{MIN_PASSWORD_LENGHT} characters long."
        )
        return False
    if password.isalpha():
        print("Password must contain at least one number.")
        return False
    if password.isdigit():
        print("Password must contain at least one letter.")
        return False
    return True
