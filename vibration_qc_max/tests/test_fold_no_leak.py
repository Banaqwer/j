from vibration.models.preprocess_foldsafe import apply_standardizer, fit_standardizer


def test_fold_safe_scaling() -> None:
    train = {"a": [1.0, 2.0, 3.0]}
    test = {"a": [4.0]}
    mu, sigma = fit_standardizer(train)
    transformed = apply_standardizer(test, mu, sigma)
    assert len(transformed["a"]) == 1
