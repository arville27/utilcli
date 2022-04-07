from utilcli.modules import CommandResponse
from ipaddress import ip_address
from typing import Dict, List
from enum import Enum
import requests
import json


class Type(Enum):
    A = "A"
    MX = "MX"
    CNAME = "CNAME"
    ALIAS = "ALIAS"
    TXT = "TXT"
    NS = "NS"
    AAAA = "AAAA"
    SRV = "SRV"
    TLSA = "TLSA"
    CAA = "CAA"


class PorkbunRecord:
    def __init__(self, id: str, host: str, type: Type, ip: str, ttl: int, notes: str = None) -> None:
        self.id = id
        self.host = host
        self.type = type
        self.ttl = ttl
        self.ip = ip
        self.notes = notes

    @staticmethod
    def get_appropriate_type(record_type: str) -> Type:
        record_type = record_type.upper()
        for type in Type:
            if type.name == record_type:
                return type
        raise Exception("Invalid record type")

    def __str__(self):
        return f"ID    : {self.id}\n" f"Host  : {self.host}\n" f"Type  : {self.type.name}\n" f"IP    : {self.ip}\n"


class PorkbunResponse(CommandResponse):
    def __init__(
        self,
        is_ok: bool,
        message: str = None,
        list_records: List[PorkbunRecord] = None,
        new_record: PorkbunRecord = None,
        deleted_record: PorkbunRecord = None,
    ) -> None:
        super().__init__(is_ok, message)
        self.list_records = list_records
        self.new_record = new_record
        self.deleted_record = deleted_record

    def __str__(self):
        return json.dumps(
            {
                "is_ok": self.is_ok,
                "message": self.message,
                "list_records": self.list_records,
                "new_record": self.new_record,
                "deleted_record": self.deleted_record,
            },
            indent=2,
        )


class PorkbunAPI:

    __BASE = "https://porkbun.com/api/json/v3"

    def __init__(self, api_key: str, secret_key: str, domain: str, default_ip: str) -> None:
        self.__API_KEY = api_key
        self.__SECRET_KEY = secret_key
        self.DOMAIN = domain
        self.DEFAULT_IP = default_ip

    def __api_call(self, endpoint: str, payload: Dict = {}) -> Dict:
        try:
            default_payload = {
                "secretapikey": self.__SECRET_KEY,
                "apikey": self.__API_KEY,
            }

            url = f"{self.__BASE}{endpoint}"
            r = requests.post(url=url, json={**payload, **default_payload})
            return r.json()
        except Exception as e:
            raise Exception("Error occur while sending request to server")

    def create_record(self, host: str, ip: str, record_type: str, ttl: int) -> PorkbunResponse:
        ENDPOINT = f"/dns/create/{self.DOMAIN}"
        ip = ip if ip else self.DEFAULT_IP

        type = PorkbunRecord.get_appropriate_type(record_type)
        ip_obj = ip_address(ip)
        if not isinstance(ttl, int):
            raise Exception("TTL must be in integer type")
        payload = {"name": host, "type": type.name, "content": str(ip_obj), "ttl": ttl}

        res = self.__api_call(ENDPOINT, payload)

        if res.get("status") == "SUCCESS":
            return PorkbunResponse(
                is_ok=True,
                new_record=PorkbunRecord(
                    id=res.get("id"), host=f"{host}.{self.DOMAIN}", type=type, ip=str(ip_obj), ttl=ttl
                ),
            )
        else:
            return PorkbunResponse(is_ok=False, message=f'{res.get("message")} ({host}.{self.DOMAIN})')

    def list_record(self, record_type: str = None) -> PorkbunResponse:
        check = False
        type = None
        if record_type:
            type = PorkbunRecord.get_appropriate_type(record_type)
            check = True
        ENDPOINT = f"/dns/retrieve/{self.DOMAIN}"
        res = self.__api_call(ENDPOINT)
        if res.get("status") == "SUCCESS":
            return PorkbunResponse(
                is_ok=True,
                list_records=[
                    PorkbunRecord(
                        id=x.get("id"),
                        host=x.get("name"),
                        type=PorkbunRecord.get_appropriate_type(x.get("type")),
                        ttl=x.get("ttl"),
                        ip=x.get("content"),
                        notes=x.get("notes"),
                    )
                    for x in res.get("records")
                    if not check or PorkbunRecord.get_appropriate_type(x.get("type")) == type
                ],
            )
        else:
            return PorkbunResponse(is_ok=False, message=res.get("message"))

    def delete_record(self, host: str = None, id: str = None) -> PorkbunResponse:
        host = host.strip()
        if not id and not host:
            raise Exception("Please provide a host, hostname or id")
        BASE_ENDPOINT = f"/dns/delete/{self.DOMAIN}"
        if host:
            res = self.list_record()
            if not res.ok():
                raise Exception("Error while fetching list of records, try using record's id directly")

            is_hostname = True if host.find(".") == -1 else False
            if is_hostname:
                match = [x for x in res.list_records if host in x.host.split(".")]
            else:
                match = [x for x in res.list_records if host == x.host]

        if len(match) == 0:
            raise Exception("Provided host is invalid")

        ENDPOINT = f"{BASE_ENDPOINT}/{match[0].id}"
        res = self.__api_call(ENDPOINT)

        if res.get("status") == "SUCCESS":
            return PorkbunResponse(
                is_ok=True,
                deleted_record=match[0],
            )
        else:
            return PorkbunResponse(is_ok=False, message=res.get("message"))
