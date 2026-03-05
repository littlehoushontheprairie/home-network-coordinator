from clients.IpifyApiClient import IpifyApiClient
from clients.PorkbunApiClient import PorkbunApiClient

print(IpifyApiClient.get_ip())

porkbun_client: PorkbunApiClient = PorkbunApiClient()
porkbun_client.fetch_certificates_by_domain("")