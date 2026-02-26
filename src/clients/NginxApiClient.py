from os import environ
import requests

class NginxApiClientError(Exception):
    pass

class NginxApiTokenExpiredError(Exception):
    pass

class NginxApiClient:
    __api_url: str = None
    __identity: str = None
    __secret: str = None
    __token: str = None

    def __init__(self):
        base_url: str = environ.get("NGINX_API_BASE_URL", None)
        self.__identity = environ.get("NGINX_API_IDENTITY", None)
        self.__secret = environ.get("NGINX_API_SECRET", None)

        if base_url is None or not len(base_url):
            raise NginxApiClientError("Nginx API base URL is not set as environment variable: NGINX_API_BASE_URL")

        if self.__identity is None or not len(self.__identity) or self.__secret is None or not len(self.__secret):
            raise NginxApiClientError("Nginx API secrets are not set in environment variables: NGINX_API_IDENTITY and NGINX_API_SECRET")

        self.__api_url = f"{base_url}/api"

    def check_token(self) -> dict:
        if self.__token is None:
            return None


        return {}


    def request_token(self) -> dict:
        return {}







