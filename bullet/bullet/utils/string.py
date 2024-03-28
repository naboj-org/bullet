def shorten(string: str, length: int) -> str:
    if len(string) <= length:
        return string

    return f"{string[:length]}…"
