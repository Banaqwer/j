def fit_standardizer(
    train: dict[str, list[float]],
) -> tuple[dict[str, float], dict[str, float]]:
    mu: dict[str, float] = {}
    sigma: dict[str, float] = {}
    for k, vals in train.items():
        m = sum(vals) / len(vals)
        v = sum((x - m) ** 2 for x in vals) / len(vals)
        s = v ** 0.5 or 1.0
        mu[k] = m
        sigma[k] = s
    return mu, sigma


def apply_standardizer(
    df: dict[str, list[float]],
    mu: dict[str, float],
    sigma: dict[str, float],
) -> dict[str, list[float]]:
    return {k: [((x - mu[k]) / sigma[k]) for x in vals] for k, vals in df.items()}
