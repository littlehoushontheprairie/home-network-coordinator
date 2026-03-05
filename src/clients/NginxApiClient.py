import requests
from dataclasses import dataclass, field
from os import environ

class NginxApiClientError(Exception):
    pass

@dataclass
class NginxApiToken:
    expires: str
    token: str

@dataclass
class NginxCertificates:
    certificate: str
    certificate_key: str
    intermediate_certificate: str

@dataclass
class NginxAccessList:
    id: int | None
    name: str
    created_on: str | None
    modified_on: str | None
    owner_user_id: int
    satisfy_any: bool
    pass_auth: bool
    proxy_host_count: int
    clients: list[NginxAccessListClient] | None
    owner: dict = field(default_factory=dict) # this can be ignored
    items: list[dict] = field(default_factory=list) # this can be ignored
    proxy_hosts: list[dict] = field(default_factory=list) # this can be ignored
    meta: dict = field(default_factory=dict) # this can be ignored

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
    id: int | None = None
    created_on: str | None = None
    modified_on: str | None = None
    directive: str = "allow"
    meta: dict = field(default_factory=dict) # this can be ignored

    def to_update_request(self):
        return {
            "directive": self.directive,
            "address": self.address
        }

class NginxApiClient:
    __api_url: str
    __identity: str
    __secret: str
    __token: NginxApiToken | None = None

    def __init__(self):
        base_url = environ.get("NGINX_API_BASE_URL")
        self.__identity = environ.get("NGINX_API_IDENTITY")
        self.__secret = environ.get("NGINX_API_SECRET")

        if base_url is None or not len(base_url):
            raise NginxApiClientError("Nginx API base URL is not set as environment variable: NGINX_API_BASE_URL")

        if self.__identity is None or not len(self.__identity) or self.__secret is None or not len(self.__secret):
            raise NginxApiClientError("Nginx API secrets are not set in environment variables: NGINX_API_IDENTITY and NGINX_API_SECRET")

        self.__api_url = f"{base_url}/api"

    def check_token(self, token: NginxApiToken | None) -> NginxApiToken | None:
        if token is None:
            return None

        response = requests.get(
            url = f"{self.__api_url}/tokens",
            headers = {"Authorization": f"Bearer {token.token}"}
        )

        if response.status_code == 200:
            data = response.json()
            return NginxApiToken(**data)
        if response.status_code == 400:
            return None
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Token expired. status_code={response.status_code}, body={response.json()}")

    def request_token(self) -> NginxApiToken:
        response = requests.post(
            url = f"{self.__api_url}/tokens",
            json = {
                "identity" : self.__identity,
                "secret" : self.__secret
            }
        )

        if response.status_code == 200:
            data = response.json()
            return NginxApiToken(**data)
        else:
            raise NginxApiClientError("Nginx API client encountered an error: Unable to authenticate.")

    def get_token(self) -> str:
        self.__token = self.check_token(self.__token)

        if self.__token is None:
            self.__token = self.request_token()

        return self.__token.token

    def update_certificate(self, certificate_id: str, new_certificates: NginxCertificates) -> NginxCertificates:
        response = requests.post(
            url = f"{self.__api_url}/certificates/{certificate_id}",
            json = new_certificates,
            headers = {"Authorization": f"Bearer {self.get_token()}"}
        )

        if response.status_code == 200:
            data = response.json()
            return NginxCertificates(**data)

        raise NginxApiClientError(f"Nginx API client encountered an error: Unable to update certificate.")

    def fetch_certificate_by_id(self, certificate_id: str) -> NginxCertificates | None:
        response = requests.get(
            url = f"{self.__api_url}/certificates/{certificate_id}",
            headers = {"Authorization": f"Bearer {self.get_token()}"}
        )

        if response.status_code == 200:
            data = response.json()
            return NginxCertificates(**data)
        elif response.status_code == 404:
            return None
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to retrieve certificate by ID.")

    def fetch_access_list_by_id(self, access_list_id: int, expand_param: list[str] | None) -> NginxAccessList:
        response = requests.get(
            url = f"{self.__api_url}/nginx/access-lists/{access_list_id}?expand={",".join(expand_param) if len(expand_param) > 0 else ""}",
            headers = {"Authorization": f"Bearer {self.get_token()}"}
        )

        if response.status_code == 200:
            data = response.json()
            clients = [NginxAccessListClient(**client) for client in data.get("clients", [])] if data.get("clients") else None
            return NginxAccessList(**{**data, "clients": clients})
        elif response.status_code == 404:
            return None
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to retrieve allow list by ID. status_code={response.status_code}, body={response.json()}")

    def update_access_list(self, access_list: NginxAccessList) -> NginxAccessList:
        response = requests.put(
            url = f"{self.__api_url}/nginx/access-lists/{access_list.id}",
            headers = {"Authorization": f"Bearer {self.get_token()}"},
            json = access_list.to_update_request()
        )

        if response.status_code == 200:
            data = response.json()
            clients = [NginxAccessListClient(**client) for client in data.get("clients", [])] if data.get("clients") else None
            return NginxAccessList(**{**data, "clients": clients})
        else:
            raise NginxApiClientError(f"Nginx API client encountered an error: Unable to update access list. status_code={response.status_code}, body={response.json()}")
