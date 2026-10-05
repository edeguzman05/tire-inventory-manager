import re


def normalize_tire_size(size):
    if not isinstance(size, str):
        return None

    size = size.strip().upper()
    size = size.replace(" ", "")

    # Supports:
    # 225/45R17
    # P215/60R16
    # LT245/75R16
    # ST205/75R15
    pattern = r"^(P|LT|ST)?\d{3}/\d{2}R\d{2}$"

    if not re.match(pattern, size):
        return None

    return size