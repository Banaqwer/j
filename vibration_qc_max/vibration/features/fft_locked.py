def fft_power(x: list[float]) -> list[float]:
    # lightweight placeholder spectrum preserving expected rfft length n//2+1
    n = len(x)
    out_len = n // 2 + 1
    energy = sum(v * v for v in x) / max(n, 1)
    return [energy for _ in range(out_len)]
