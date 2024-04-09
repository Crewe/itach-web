import re

ItachError = {
    # Common
    "001": "Invalid Command (Unknown)",
    "002": "Invalid Module Address",
    "003": "Invalid Port Address",
    "016": "No Carriage Return",
    "023": "Invalid Parameter",
    "027": "Settings Locked",
    # Sensons
    "018": "Not a sensor or a relay",
}


def check_response(response: str) -> str:
    if type(response) is list:
        return None

    if re.fullmatch(r"ERR_.+", response):
        err_code = response.split(",")
        return [err_code[1], ItachError[err_code[1]]]

    return None
