import re


class DimException(Exception):
    pass


def resolve_dim(name: str, dim: None | int, dim_index: None | str) -> list[str]:
    if dim is None:
        raise DimException(f"can't resolve dim for '{name}' without a dim value")
    if dim < 1:
        raise DimException("dim value must be greater than 0")

    if "[%s]" in name:
        return _resolve_array(name, dim)
    elif "%s" in name:
        return _resolve_list(name, dim, dim_index)

    raise DimException(f"can't resolve dim for '{name}' without a '%s' or '[%s]' in the name")


def resolve_dim_index(dim: None | int, dim_index: None | str) -> list[str]:
    if dim is None:
        raise DimException("can't resolve dim index without a dim value")
    if dim < 1:
        raise DimException("dim value must be greater than 0")

    if dim_index is None:
        dim_index_list = [str(i) for i in range(dim)]
    elif re.match(r"[0-9]+\-[0-9]+", dim_index):
        start, end = dim_index.split("-")

        if int(start) >= int(end):
            raise DimException(f"dim index '{dim_index}' start value must be less than end value")

        dim_index_list = [str(i) for i in range(int(start), int(end) + 1)]
    elif re.match(r"[A-Z]-[A-Z]", dim_index):
        start, end = dim_index.split("-")

        if ord(start) >= ord(end):
            raise DimException(f"dim index '{dim_index}' start value must be less than end value")

        dim_index_list = [chr(i) for i in range(ord(start), ord(end) + 1)]
    elif re.match(r"[_0-9a-zA-Z]+(,\s*[_0-9a-zA-Z]+)+", dim_index):
        dim_index_no_whitespace = re.sub(r"\s+", "", dim_index)
        dim_index_list = dim_index_no_whitespace.split(",")
    else:
        raise DimException(f"can't resolve dim index for '{dim_index}'")

    if len(dim_index_list) != dim:
        raise DimException(f"dim index '{dim_index}' does not match the dim value '{dim}'")

    return dim_index_list


def _resolve_array(name: str, dim: int) -> list[str]:
    resolved_names: list[str] = []
    for i in range(dim):
        resolved_names.append(name.replace("[%s]", str(i)))
    return resolved_names


def _resolve_list(name: str, dim: int, dim_index: None | str) -> list[str]:
    resolved_names: list[str] = []
    for index in resolve_dim_index(dim, dim_index):
        resolved_names.append(name.replace("%s", index))

    return resolved_names
