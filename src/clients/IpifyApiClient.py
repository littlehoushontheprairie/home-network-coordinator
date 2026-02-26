import requests

class IpifyApiClientError(Exception):
    pass

class IpifyApiClient:
    __IPIFY_API_URL: str = "https://api64.ipify.org?format=json"

    @staticmethod
    def get_ip() -> str:
        try:
            response: requests.Response = requests.get(IpifyApiClient.__IPIFY_API_URL)

            if response.status_code == 200:
                return response.json().get("ip", "")
            else:
                raise IpifyApiClientError(f"An unexpected response code was returned: {response.status_code}")
        except requests.RequestException:
            raise IpifyApiClientError("An error has occurred during call to Ipify.")