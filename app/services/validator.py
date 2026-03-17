def validate_characters(text: str, allowed_chars: list[str]) -> bool:
    """
    Returns True if all Chinese characters in text are allowed.
    """

    allowed_set = set(allowed_chars)

    for char in text:
        # Check if char is a CJK Unified Ideograph
        if "\u4e00" <= char <= "\u9fff":
            if char not in allowed_set:
                return False

    return True

def validate_characters_verbose(text: str, allowed_chars: list[str]):
    allowed_set = set(allowed_chars)
    invalid_chars = set()

    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            if char not in allowed_set:
                invalid_chars.add(char)

    return len(invalid_chars) == 0, invalid_chars