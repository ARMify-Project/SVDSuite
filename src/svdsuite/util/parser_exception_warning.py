class ParserWarning(Warning):
    pass


class ParserException(Exception):
    pass


# Customize the warning format
def custom_warning_format(message: str, category: type, _: str, __: int, ___: None | str) -> str:
    return f"{category.__name__}: {message}\n"
