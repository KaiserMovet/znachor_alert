import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, NamedTuple

import requests
from requests.compat import urljoin


class WykopConnectorException(Exception):
    ...


class Methods(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class WykopResponse:
    code: int
    data: List | Dict
    error: Dict
    pagination: Dict
    next: str | int | None = None


class WykopConnector:

    URL = "https://wykop.pl/api/v3/"

    def __init__(
        self,
        key: str | None = None,
        secret: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        """
        Wykop Connector constructor.
        You need to provide a key and secret OR refresh_token.
        To obtain a refresh token, you need to provide key and secret,
        execute self.connect(), open link
        and login to your Wykop account.
        Refresh token will be shown in url in 'rtoken' variable.

        Args:
            key (str | None, optional): Key. Defaults to None.
            secret (str | None, optional): Secret. Defaults to None.
            refresh_token (str | None, optional): Refresh token.
            Defaults to None.
        """
        self._key = key
        self._secret = secret
        self._refresh_token = refresh_token
        self._token: str | None = self._get_token()
        self.header = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
        }
        self.connect()

    # pylint disable=method-cache-max-size-none
    def _get_token(self) -> str:
        header = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._key and self._secret:
            # Auth
            url = urljoin(self.URL, "auth")
            data = {"key": self._key, "secret": self._secret}
        elif self._refresh_token:
            # Refresh token
            url = urljoin(self.URL, "refresh-token")
            data = {"refresh_token": self._refresh_token}

        else:
            raise WykopConnectorException(
                "You need to provide key and secret OR refresh_token"
            )

        res = requests.post(
            url, json={"data": data}, headers=header, timeout=15
        )
        return res.json()["data"]["token"]

    def connect(self) -> str:
        res = requests.get(
            "https://wykop.pl/api/v3/connect", headers=self.header, timeout=15
        )
        return res.json()["data"]["connect_url"]

    def request(
        self,
        method: Methods,
        endpoint: str,
        data: Dict | None = None,
        params: Dict | None = None,
        timeout: int = 10,
    ) -> WykopResponse:
        url = urljoin(self.URL, endpoint)
        logging.info(
            "Executing %s - %s, params: %s, data: %s",
            method,
            url,
            str(params),
            str(data),
        )
        res = requests.request(
            method=method,
            url=url,
            data={"data": data} if data else None,
            params=params,
            headers=self.header,
            timeout=timeout,
        )
        res_json = res.json()
        res_data = res_json.get("data", []) if res_json else []
        res_error = res_json.get("error", {}) if res_json else {}
        res_pagination = res_json.get("pagination", {}) if res_json else {}

        return WykopResponse(
            res.status_code, res_data, res_error, res_pagination
        )

    def request_with_pagination(
        self,
        method: Methods,
        endpoint: str,
        page: int | str | None = None,
        data: Dict | None = None,
        params: Dict | None = None,
        timeout: int = 10,
        page_count: int = 1,
    ) -> WykopResponse:
        params = params or {}
        last_response: WykopResponse = None  # type: ignore
        all_data: List[Dict] = []
        while page_count > 0:
            page_count -= 1
            if page:
                params["page"] = page
            res = self.request(method, endpoint, data, params, timeout)
            last_response = res
            all_data += res.data  # type: ignore
            # Break if wrong status code
            if 200 > res.code or res.code > 299:
                break
            # Get next page
            if "next" in res.pagination:
                page = res.pagination["next"]
            elif page is None:
                page = 2
            elif isinstance(page, int):
                page += 1
            else:
                break
        last_response.data = all_data
        last_response.next = page
        return last_response
