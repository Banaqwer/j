from vibration.backtest.execution_rules import next_open_execution


def test_next_open_execution() -> None:
    assert next_open_execution(10) == 11
