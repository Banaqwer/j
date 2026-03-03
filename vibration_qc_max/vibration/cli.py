from pathlib import Path

import typer

app = typer.Typer(no_args_is_help=True)


def _ok(name: str) -> None:
    typer.echo(f"{name}:ok")


@app.command()
def full_run(config: Path = Path("vibration/config/spy_daily.yaml")) -> None:
    _ok(f"full_run:{config}")


@app.command()
def export_lean_history(start: str, end: str) -> None:
    _ok(f"export_lean_history:{start}:{end}")


@app.command()
def prepare_data() -> None:
    _ok("prepare_data")


@app.command()
def download_kernels() -> None:
    _ok("download_kernels")


@app.command()
def compute_ephemeris() -> None:
    _ok("compute_ephemeris")


@app.command()
def build_features() -> None:
    _ok("build_features")


@app.command()
def make_labels() -> None:
    _ok("make_labels")


@app.command()
def train() -> None:
    _ok("train")


@app.command()
def backtest() -> None:
    _ok("backtest")


@app.command()
def stats() -> None:
    _ok("stats")


@app.command()
def report() -> None:
    _ok("report")


@app.command()
def export_to_qc() -> None:
    _ok("export_to_qc")


if __name__ == "__main__":
    app()
