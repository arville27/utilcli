from utilcli.modules import UtilAPI
from utilcli.utility import CONFIG
from operator import itemgetter
from typing import Optional
import typer


host, port = itemgetter("HOST", "PORT")(CONFIG.get("utilapi"))
utilapi = UtilAPI(host, port)


def lyrics(keyword: str, provider: Optional[str] = typer.Argument(None)):
    try:
        r = utilapi.search_lyrics(query=keyword, source=provider.split(",") if provider else None)
    except Exception as e:
        return typer.echo(e)

    if not r.ok():
        return typer.echo(r.message)
    results = [f"[{index}] {x.artist} {x.title}" for index, x in enumerate(r.results, 1)]
    typer.echo("[0] Cancel")
    typer.echo("\n".join(results))
    while True:
        choice = typer.prompt("")
        choice = int(choice) if choice.isdigit() else -1
        if choice == 0:
            return
        if 1 <= choice <= len(results):
            typer.clear()
            typer.echo(r.results[choice - 1].get_lyrics())
            break
