from utilcli.modules import CommandResponse
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import requests
import json
import re


class ShlinkIdentifier:
    def __init__(self, identifier: str, available_domain: List[str]) -> None:
        self.__domain = None
        splitted_identifier = identifier.split("/")
        if self.validate_url(identifier):
            parsed_url = urlparse(identifier)
            self.__domain = parsed_url.netloc
            self.__short_code = parsed_url.path[1::]
        elif len(splitted_identifier) > 1 and len([x for x in splitted_identifier if x in available_domain]) > 0:
            self.__short_code = splitted_identifier.pop()
            self.__domain = splitted_identifier.pop()
        else:
            self.__short_code = identifier

    def get_short_code(self) -> str:
        return self.__short_code

    def is_domain_specified(self) -> Tuple:
        return (True if self.__domain else False, self.__domain)

    @staticmethod
    def validate_url(url: str, validate_protocol: bool = True) -> bool:
        url = urlparse(url)
        if (re.match(r"https?", url.scheme) if validate_protocol else True) and len(url.netloc) > 0:
            return True
        return False


class ShlinkResponse(CommandResponse):
    def __init__(
        self,
        is_ok: bool,
        status_code: int,
        message: str = None,
        domains: List[str] = None,
        error_type: str = None,
        short_code: str = None,
        short_url: str = None,
    ) -> None:
        super().__init__(is_ok, message)
        self.domains = domains
        self.error_type = error_type
        self.status_code = status_code
        self.short_code = short_code
        self.short_url = short_url

    def __str__(self):
        return json.dumps(
            {
                "is_ok": self.is_ok,
                "status_code": self.status_code,
                "message": self.message,
                "error_type": self.error_type,
                "domains": self.domains,
                "short_code": self.short_code,
                "short_url": self.short_url,
            },
            indent=2,
        )


class ShlinkAPI:
    def __init__(self, domain: str, api_key: str) -> None:
        self.API_DOMAIN = domain
        self.API_KEY = api_key
        self.API_ENDPOINT = f"https://{self.API_DOMAIN}/rest/v2"
        self.__HEADER = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": self.API_KEY,
        }

    @staticmethod
    def validate_url(url: str, validate_protocol: bool = True) -> bool:
        url = urlparse(url)
        if (re.match(r"https?", url.scheme) if validate_protocol else True) and len(url.netloc) > 0:
            return True
        return False

    def __construct_message(self, response: Dict) -> str:
        return f"[{response.get('type')}] {response.get('title')}\n{response.get('detail')}"

    def get_available_domain(self) -> ShlinkResponse:
        ENDPOINT = "/domains"
        res = self.__api_call(endpoint=ENDPOINT)
        if res.get("status_code") == 200:
            return ShlinkResponse(
                is_ok=True,
                status_code=res.get("status_code"),
                domains=[x.get("domain") for x in res.get("domains").get("data")],
            )
        else:
            return ShlinkResponse(
                is_ok=False,
                status_code=res.get("status_code"),
                error_type=res.get("type"),
                message=self.__construct_message(response=res),
            )

    def __api_call(
        self,
        method: str = "GET",
        payload: Dict = {},
        params: Dict = None,
        endpoint: str = None,
    ) -> Dict:
        FINAL_ENDPOINT = f'{self.API_ENDPOINT}{endpoint if endpoint else ""}'
        try:
            r = requests.request(
                method=method,
                url=FINAL_ENDPOINT,
                headers=self.__HEADER,
                json=payload,
                params=params,
            )
            res = {"status_code": r.status_code}
            return {**r.json(), **res} if len(r.text) > 0 else res
        except Exception:
            raise Exception("Error occur while sending request to server")

    def edit_short_url(self, identifier: str, new_long_url: str) -> ShlinkResponse:
        ENDPOINT = "/short-urls"
        if not self.validate_url(new_long_url):
            raise Exception(
                "Please provide a valid url, make sure the new url contains either http:// or https:// prefix"
            )

        res = self.get_available_domain()
        if not res.ok():
            return res
        shlink_identifier = ShlinkIdentifier(identifier, res.domains)

        payload = {"longUrl": new_long_url, "validateUrl": True, "crawlable": False}

        status, domain = shlink_identifier.is_domain_specified()
        query_param = {"domain": domain} if status else None
        res = self.__api_call(
            "PATCH",
            payload=payload,
            params=query_param,
            endpoint=f"{ENDPOINT}/{shlink_identifier.get_short_code()}",
        )
        if res.get("status_code") != 200:
            return ShlinkResponse(
                is_ok=False,
                status_code=res.get("status_code"),
                error_type=res.get("type"),
                message=self.__construct_message(res),
            )
        else:
            return ShlinkResponse(is_ok=True, status_code=res.get("status_code"))

    def delete_short_url(self, identifier: str) -> ShlinkResponse:
        ENDPOINT = "/short-urls"
        res = self.get_available_domain()
        if not res.ok():
            return res
        shlink_identifier = ShlinkIdentifier(identifier, res.domains)

        status, domain = shlink_identifier.is_domain_specified()
        query_param = {"domain": domain} if status else None

        res = self.__api_call(
            "DELETE",
            params=query_param,
            endpoint=f"{ENDPOINT}/{shlink_identifier.get_short_code()}",
        )

        if res.get("status_code") == 204:
            return ShlinkResponse(is_ok=True, status_code=res.get("status_code"))
        else:
            return ShlinkResponse(
                is_ok=False,
                status_code=res.get("status_code"),
                error_type=res.get("type"),
                message=self.__construct_message(res),
            )

    def shorten(self, url: str, slug: str = None, alt_domain: str = None) -> ShlinkResponse:
        ENDPOINT = "/short-urls"
        if not self.validate_url(url):
            raise Exception("Please provide a valid url, make sure the url contains either http:// or https:// prefix")

        payload = {
            "longUrl": url,
            "findIfExists": False,
            "domain": self.API_DOMAIN,
            "validateUrl": True,
            "crawlable": False,
        }

        if alt_domain:
            res = self.get_available_domain()
            if not res.ok():
                return res
            if alt_domain in res.domains:
                payload["domain"] = alt_domain
            else:
                raise Exception(f'Please provide a valid domain. Available domain: "{", ".join(res.domains)}"')

        if slug:
            payload["customSlug"] = slug

        res = self.__api_call("POST", endpoint=ENDPOINT, payload=payload)

        if res.get("status_code") != 200:
            return ShlinkResponse(
                is_ok=False,
                status_code=res.get("status_code"),
                error_type=res.get("type"),
                message=self.__construct_message(res),
            )
        else:
            return ShlinkResponse(
                is_ok=True,
                status_code=res.get("status_code"),
                short_code=res.get("shortCode"),
                short_url=res.get("shortUrl"),
            )
