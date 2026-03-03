def circular_shift(x: list[int], shift: int) -> list[int]:
    n = len(x)
    if n == 0:
        return []
    shift %= n
    return x[-shift:] + x[:-shift]
