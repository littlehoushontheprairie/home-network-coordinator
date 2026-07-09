import os
import requests

from helpers.DataclassHelper import DataclassHelper
from dataclasses import dataclass
from typing import Optional

class NginxApiClientError(Exception):
    pass

@dataclass
class NginxApiToken:
    expires: str
    token: str

@dataclass
class NginxAccessList:
    id: Optional[int]
    name: str
    created_on: Optional[str]
    modified_on: Optional[str]
    owner_user_id: int
    satisfy_any: bool
    pass_auth: bool
    proxy_host_count: int
    clients: list[NginxAccessListClient]

    @staticmethod
    def from_dict(data: dict) -> NginxAccessList:
        return DataclassHelper.from_dict(NginxAccessList, data)

    def to_update_request(self):
        return {
            "name": self.name,
            "satisfy_any": self.satisfy_any,
            "pass_auth": self.pass_auth,
            "clients": [client.to_update_request() for client in self.clients] if self.clients else []
        }

@dataclass
class NginxAccessListClient:
    address: str
    access_list_id: int
    id: Optional[int] = None
    created_on: Optional[str] = None
    modified_on: Optional[str] = None
    directive: str = "allow"

    def to_update_request(self):
        return {
            "directive": self.directive,
            "address": self.address
        }

@dataclass
class NginxProxyHost:
    id: int
    created_on: Optional[str]
    modified_on: Optional[str]
    owner_user_id: int
    domain_names: list[str]
    forward_host: str
    forward_port: int
    access_list_id: Optional[int]
    certificate_id: Optional[int]
    ssl_forced: bool
    caching_enabled: bool
    block_exploits: bool
    advanced_config: str
    allow_websocket_upgrade: bool
    http2_support: bool
    forward_scheme: str
    enabled: bool
    locations: list
    hsts_enabled: bool
    hsts_subdomains: bool

    @staticmethod
    def from_dict(data: dict) -> NginxProxyHost:
        return DataclassHelper.from_dict(NginxProxyHost, data)

    def to_update_request(self):
        return {
            "domain_names": self.domain_names,
            "forward_host": self.forward_host,
            "forward_port": self.forward_port,
            "access_list_id": self.access_list_id,
            "certificate_id": self.certificate_id,
            "ssl_forced": self.ssl_forced,
            "caching_enabled": self.caching_enabled,
            "block_exploits": self.block_exploits,
            "advanced_config": self.advanced_config,
            "allow_websocket_upgrade": self.allow_websocket_upgrade,
            "http2_support": self.http2_support,
            "forward_scheme": self.forward_scheme,
            "enabled": self.enabled,
            "hsts_enabled": self.hsts_enabled,
            "hsts_subdomains": self.hsts_subdomains
        }


class NginxApiClient:
    __REQUEST_TIMEOUT: int = 30 # in seconds
    __api_url: str
    __identity: str
    __secret: str
    __token: Optional[NginxApiToken] = None

    def __init__(self):
        base_url = os.getenv("NGINX_API_BASE_URL")
        self.__identity = os.getenv("NGINX_API_IDENTITY")
        self.__secret = os.getenv("NGINX_API_SECRET")

        if base_url is None or not len(base_url):
            raise NginxApiClientError("Nginx API base URL is not set as environment variable: NGINX_API_BASE_URL")

        if self.__identity is None or not len(self.__identity) or self.__secret is None or not len(self.__secret):
            raise NginxApiClientError("Nginx API secrets are not set in environment variables: NGINX_API_IDENTITY and NGINX_API_SECRET")

        self.__api_url = f"{base_url}/api"

    def check_token(self, token: Optional[NginxApiToken]) -> Optional[NginxApiToken]:
        if token is None:
            return None

        response = requests.get(
            url = f"{self.__api_url}/tokens",
            headers = {"Authorization": f"Bearer {token.token}"},
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return NginxApiToken(**response.json())
        if response.status_code == 400:
            return None
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error during token check. status_code={response.status_code}, body={response.json()}")

    def request_token(self) -> NginxApiToken:
        response = requests.post(
            url = f"{self.__api_url}/tokens",
            json = {
                "identity" : self.__identity,
                "secret" : self.__secret
            },
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return NginxApiToken(**response.json())
        else:
            raise NginxApiClientError("Nginx API client encountered an error: Unable to authenticate.")

    def get_token(self) -> str:
        self.__token = self.check_token(self.__token)

        if self.__token is None:
            self.__token = self.request_token()

        return self.__token.token

    def fetch_access_list_by_name(self, access_list_name: str) -> Optional[NginxAccessList]:
        response = requests.get(
            url = f"{self.__api_url}/nginx/access-lists?expand=clients",
            headers = {"Authorization": f"Bearer {self.get_token()}"},
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            for access_list in response.json():
                if access_list.get("name", "") == access_list_name:
                    return NginxAccessList.from_dict(access_list)

            return None
        elif response.status_code == 404:
            return None
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to fetch allow list by name. status_code={response.status_code}, body={response.json()}")

    def update_access_list(self, access_list: NginxAccessList) -> NginxAccessList:
        response = requests.put(
            url = f"{self.__api_url}/nginx/access-lists/{access_list.id}",
            headers = {"Authorization": f"Bearer {self.get_token()}"},
            json = access_list.to_update_request(),
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return NginxAccessList.from_dict(response.json())
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to update access list. status_code={response.status_code}, body={response.json()}")


    def fetch_proxy_hosts_by_ip(self, ip: Optional[str] = None) -> Optional[list[NginxProxyHost]]:
        response = requests.get(
            url = f"{self.__api_url}/nginx/proxy-hosts",
            headers = {"Authorization": f"Bearer {self.get_token()}"},
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            proxy_hosts = [NginxProxyHost.from_dict(proxy_host) for proxy_host in response.json()]

            if ip is None:
                return proxy_hosts
            else:
                return [proxy_host for proxy_host in proxy_hosts if proxy_host.forward_host == ip]
        elif response.status_code == 404:
            return None
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to fetch proxy hosts. status_code={response.status_code}, body={response.json()}")


    def update_proxy_host(self, proxy_host: NginxProxyHost) -> NginxProxyHost:
        response = requests.put(
            url = f"{self.__api_url}/nginx/proxy-hosts/{proxy_host.id}",
            headers = {"Authorization": f"Bearer {self.get_token()}"},
            json = proxy_host.to_update_request(),
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return NginxProxyHost.from_dict(response.json())
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to update proxy host. status_code={response.status_code}, body={response.json()}")
