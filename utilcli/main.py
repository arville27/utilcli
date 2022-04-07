from utilcli.commands import shlink, porkbun, lyrics
import typer

app = typer.Typer()
app.add_typer(shlink, name="shlink")
app.add_typer(porkbun, name="porkbun")

# Base level command
app.command()(lyrics)
