from utilcli.utility import copy_to_clipboard, CONFIG
from utilcli.modules import ShlinkAPI
from operator import itemgetter
from typing import Optional
import typer


app = typer.Typer()

domain, api_key = itemgetter(
    "DOMAIN",
    "API_KEY",
)(CONFIG.get("shlink"))

shlink_api = ShlinkAPI(domain, api_key)


@app.command()
def create_shorturl(
    url: str, slug: Optional[str] = typer.Argument(None), alt_domain: Optional[str] = typer.Argument("arv.cx")
):
    try:
        resp = shlink_api.shorten(url=url, slug=slug, alt_domain=alt_domain)
    except Exception as e:
        return typer.echo(e)
    if not resp.ok():
        return typer.echo(resp.message)
    typer.echo(resp.short_url)
    copy_to_clipboard(resp.short_url)


@app.command()
def delete_shorturl(url_identifier: str):
    try:
        resp = shlink_api.delete_short_url(url_identifier)
    except Exception as e:
        return typer.echo(e)
    if not resp.ok():
        return typer.echo(resp.message)
    typer.echo("URL successfully deleted")


@app.command()
def edit_shorturl(url_identifier: str, new_url: str):
    try:
        resp = shlink_api.edit_short_url(url_identifier, new_url)
    except Exception as e:
        return typer.echo(e)
    if not resp.ok():
        return typer.echo(resp.message)
    typer.echo("URL successfully updated")
