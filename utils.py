import random
import string


def generate_otp():
    chars = string.ascii_lowercase + string.ascii_uppercase + '123456789'
    otp = ""
    for i in range(7):
        otp += random.choice(chars)
    return otp


def get_verification_model():
    pass
