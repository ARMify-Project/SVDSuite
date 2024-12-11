def or_if_none[T](a: None | T, b: None | T) -> None | T:
    return a if a is not None else b
