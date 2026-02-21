def z_norm(x: list[float]) -> list[float]:
    n = len(x)
    if n == 0:
        return []
    mu = sum(x) / n
    var = sum((v - mu) ** 2 for v in x) / n
    std = var ** 0.5
    if std == 0:
        return [0.0 for _ in x]
    return [(v - mu) / std for v in x]
