import json
import subprocess
import typer
from pathlib import Path


def copy_to_clipboard(data: str) -> None:
    subprocess.run("clip", universal_newlines=True, input=data)


def load_config():
    config_path: Path = Path(typer.get_app_dir("utilcli")) / "config.json"
    if not config_path.is_file():
        typer.echo("Config file doesn't exist yet")
        raise typer.Exit(code=1)
    with open(config_path) as config:
        return json.loads(config.read())


try:
    CONFIG = load_config()
except Exception as e:
    typer.echo(e)
    quit(code=1)
