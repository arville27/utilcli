from utilcli.utility import copy_to_clipboard, CONFIG
from utilcli.modules import PorkbunAPI
from operator import itemgetter
import typer


app = typer.Typer()


api_key, secret_key, domain, default_ip = itemgetter("API_KEY", "SECRET_KEY", "DOMAIN", "SERVER_IP")(
    CONFIG.get("porkbun")
)
porkbun = PorkbunAPI(api_key, secret_key, domain, default_ip)


@app.command()
def create_record(host: str, ip: str = None, type: str = "A", ttl: int = 300):
    try:
        resp = porkbun.create_record(host=host, ip=ip, record_type=type, ttl=ttl)
    except Exception as e:
        return typer.echo(e)
    if not resp.ok():
        return typer.echo(resp.message)
    typer.echo(f"Record successfully created ({resp.new_record.host})")
    copy_to_clipboard(resp.new_record.host)


@app.command()
def list_record(type: str = "A"):
    try:
        resp = porkbun.list_record(record_type=type)
    except Exception as e:
        return typer.echo(e)
    if not resp.ok():
        return typer.echo(resp.message)
    for record in resp.list_records:
        typer.echo(record)


@app.command()
def delete_record(hostname: str):
    try:
        resp = porkbun.delete_record(hostname)
    except Exception as e:
        return typer.echo(e)
    if not resp.ok():
        return typer.echo(resp.message)
    typer.echo(f"Record succesfully deleted ({resp.deleted_record.host})")
