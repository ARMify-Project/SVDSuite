import itertools


def process_binary_value_with_wildcard(binary_str: str) -> list[int]:
    if "x" in binary_str:
        return [int(b, 2) for b in replace_x_combinations(binary_str)]
    return [int(binary_str, 2)]


def replace_x_combinations(binary_str: str) -> list[str]:
    x_count = binary_str.count("x")
    combinations = itertools.product("01", repeat=x_count)
    return [replace_x_with_combination(binary_str, combination) for combination in combinations]


def replace_x_with_combination(binary_str: str, combination: tuple[str, ...]) -> str:
    temp_str = binary_str
    for bit in combination:
        temp_str = temp_str.replace("x", bit, 1)
    return temp_str
