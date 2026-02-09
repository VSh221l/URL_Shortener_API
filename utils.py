import secrets
import string
import re
from urllib.parse import urlparse
from logging_config import logger


def is_valid_url(url:str) -> bool:
    try:
        result = urlparse(url)
        return bool(result.scheme and result.netloc)
    except ValueError:
        return False

def generate_code(length: int = 8) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join([secrets.choice(letters) for _ in range(length)])