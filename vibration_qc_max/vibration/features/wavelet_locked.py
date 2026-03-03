def normalized_power(coeff: list[complex], scale: float) -> list[float]:
    return [((c.real ** 2 + c.imag ** 2) / scale) for c in coeff]
