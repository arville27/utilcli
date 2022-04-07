from typing import Callable, Dict, List, Optional
from utilcli.modules import CommandResponse
import requests
import json


class LyricsItem:
    def __init__(self, title: str, artist: str, provider: str, lyrics: Callable) -> None:
        self.title = title
        self.artist = artist
        self.provider = provider
        self.lyrics = lyrics

    def get_lyrics(self) -> str:
        return self.lyrics()

    def __str__(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "artist": self.artist,
                "provider": self.provider,
            },
            indent=2,
        )


class UtilAPIResponse(CommandResponse):
    def __init__(self, is_ok: bool, message: str = None, results: List[LyricsItem] = []) -> None:
        super().__init__(is_ok, message)
        self.results = results


class UtilAPI:
    def __init__(self, host: str, port: int) -> None:
        self.__HOST = host
        self.__PORT = port
        self.__BASE = f"{self.__HOST}:{self.__PORT}/api"
        self.__LYRICS_SOURCES = ["ln", "genius"]

    def __api_call(self, endpoint: str, query_params: Dict) -> Dict:
        try:
            r = requests.get(url=f"{self.__BASE}{endpoint}", params=query_params)
            content_type = r.headers.get("Content-Type")
            if content_type.find("json") == -1:
                return r.text
            else:
                return r.json()
        except requests.exceptions.JSONDecodeError:
            raise Exception("Error occur while parsing request from the server")
        except Exception:
            raise Exception("Error occur while sending request to server")

    def search_lyrics(self, query: str, source: Optional[List[str]] = None) -> UtilAPIResponse:
        ENDPOINT = "/lyrics"
        query_params = {"q": query}
        if source:
            if len([x.strip() for x in source if x.strip() in self.__LYRICS_SOURCES]) == 0:
                raise Exception(
                    f'Please provide a valid lyrics source. Source available "{", ".join(self.__LYRICS_SOURCES)}"'
                )
            query_params["p"] = source
        res = self.__api_call(endpoint=ENDPOINT, query_params=query_params)
        if res.get("status") != "OK":
            return UtilAPIResponse(is_ok=False, message=res.get("message"))
        else:
            query_params["lyricsonly"] = 1

            results = [
                LyricsItem(
                    entry.get("title"),
                    entry.get("artist"),
                    entry.get("provider"),
                    lambda x=index: (self.__api_call(endpoint=f"{ENDPOINT}/{x}", query_params=query_params)),
                )
                for index, entry in enumerate(res.get("results"), 1)
            ]
            return UtilAPIResponse(results=results, is_ok=True)
