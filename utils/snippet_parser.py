import re

def extract_kavenegar_info(code):
    token_match = re.search(r"apikey\s*:\s*['\"]([a-fA-F0-9+/=]+)['\"]", code)
    token = token_match.group(1) if token_match else None

    sender_match = re.search(r"sender\s*:\s*['\"](\d+)['\"]", code)
    sender = sender_match.group(1) if sender_match else None

    receptor_match = re.search(r"receptor\s*:\s*['\"](\d+)['\"]", code)
    receptor = receptor_match.group(1) if receptor_match else None

    return receptor, sender, token
