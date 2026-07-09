import os
import requests

from dataclasses import dataclass

class PorkbunApiClientError(Exception):
    pass

@dataclass
class PorkbunApiCertificates:
    private_key: str
    public_key: str
    certificate_chain: str

    @staticmethod
    def from_dict(data: dict) -> PorkbunApiCertificates:
        return PorkbunApiCertificates(
            private_key = data.get("privatekey"),
            public_key = data.get("publickey"),
            certificate_chain = data.get("certificatechain")
        )

class PorkbunApiClient:
    __REQUEST_TIMEOUT: int = 30 # in seconds
    __PORKBUN_API_URL: str = "https://api.porkbun.com/api/json/v3"
    __secrets: dict = {}

    def __init__(self):
        api_key = os.getenv("PORKBUN_API_KEY")
        secret_api_key = os.getenv("PORKBUN_SECRET_API_KEY")

        if api_key is None or not len(api_key) or secret_api_key is None or not len(secret_api_key):
            raise PorkbunApiClientError("Porkbun API secrets are not set in environment variables: PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY")

        self.__secrets = {
            "apikey" : api_key,
            "secretapikey" : secret_api_key
        }

    def fetch_certificates_by_domain(self, domain: str) -> PorkbunApiCertificates:
        response = requests.post(
            url = f"{self.__PORKBUN_API_URL}/ssl/retrieve/{domain}",
            json = self.__secrets,
            timeout = self.__REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return PorkbunApiCertificates.from_dict(response.json())
        else:
            raise PorkbunApiClientError(f"Porkbun API returned an unexpected status code: {response.status_code}")
