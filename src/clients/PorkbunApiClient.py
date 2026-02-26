from os import environ
from dataclasses import dataclass
import requests

class PorkbunApiClientError(Exception):
    pass

@dataclass
class PorkbunApiCertificates:
    private_key: str
    public_key: str
    certificate_chain: str

class PorkbunApiClient:
    __PORKBUN_API_URL: str = "https://api.porkbun.com/api/json/v3"
    __secrets: dict = {}

    def __init__(self):
        api_key: str = environ.get("PORKBUN_API_KEY", None)
        secret_api_key: str = environ.get("PORKBUN_SECRET_API_KEY", None)

        if api_key is None or not len(api_key) or secret_api_key is None or not len(secret_api_key):
            raise PorkbunApiClientError("Porkbun API secrets are not set in environment variables: PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY")

        self.__secrets = {
            "apikey" : api_key,
            "secretapikey" : secret_api_key
        }

    def get_certs(self, domain):
        url: str = f"{self.__PORKBUN_API_URL}/ssl/retrieve/{domain}"

        response: requests.Response = requests.post(
            url = url,
            json = self.__secrets
        )

        if response.status_code == 200:
            certs: dict = response.json()

            return PorkbunApiCertificates(
                private_key = certs.get("privatekey"),
                public_key = certs.get("publickey"),
                certificate_chain = certs.get("certificatechain")
            )
        else:
            raise PorkbunApiClientError(f"Porkbun API returned an unexpected status code: {response.status_code}")




