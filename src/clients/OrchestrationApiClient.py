import os
import requests

class OrchestrationApiClientError(Exception):
    pass

class OrchestrationApiClient:
    __api_base_url: str
    __api_token: str

    def __init__(self):
        self.__api_base_url = os.getenv("ORCHESTRATION_API_BASE_URL")
        self.__api_token = os.getenv("ORCHESTRATION_API_TOKEN")

        if self.__api_base_url is None or not len(self.__api_base_url):
            raise OrchestrationApiClientError("Orchestration API base URL is not set in environment variables: ORCHESTRATION_API_BASE_URL")

        if self.__api_token is None or not len(self.__api_token):
            raise OrchestrationApiClientError("Orchestration API token is not set in environment variables: ORCHESTRATION_API_TOKEN")


    def update_allow_list_with_ip(self, from_ip: str, to_ip: str):
        response = requests.patch(
            url = f"{self.__api_base_url}/api/allow-list",
            headers = {"Authorization": f"Bearer {self.__api_token}"},
            json = {"from_ip": from_ip, "to_ip": to_ip},
            timeout = 30
        )

        if response.status_code != 200:
            raise OrchestrationApiClientError(f"Failed to update allow list: status_code={response.status_code}, body={response.text}")


    def update_proxy_hosts_with_ip(self, from_ip: str, to_ip: str):
        response = requests.patch(
            url = f"{self.__api_base_url}/api/proxy-hosts",
            headers = {"Authorization": f"Bearer {self.__api_token}"},
            json = {"from_ip": from_ip, "to_ip": to_ip},
            timeout = 30
        )

        if response.status_code != 200:
            raise OrchestrationApiClientError(f"Failed to update proxy hosts: status_code={response.status_code}, body={response.text}")