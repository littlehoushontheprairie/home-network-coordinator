import os
import logging

from typing import Optional
from linode_api4 import LinodeClient

from clients.IpifyApiClient import IpifyApiClient
from clients.OrchestrationApiClient import OrchestrationApiClient, OrchestrationApiClientError
from entities.OrchestrationErrors import LinodeNotConfiguredError
from helpers.CacheIpHelper import CacheIpHelper

# Logging configuration
logging.basicConfig(format="[IpUpdateOrchestrator] %(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

def update_linode_firewalls(ip: str):
    ip_with_mask = f"{ip}/32"

    try:
        linode_label_name = os.getenv("LINODE_LABEL_NAME")
        linode_api_token = os.getenv("LINODE_API_TOKEN")

        if linode_label_name is None or linode_api_token is None:
            raise LinodeNotConfiguredError()

        linode_client = LinodeClient(linode_api_token)
        linode_label = linode_label_name + "-"

        firewalls = linode_client.networking.firewalls()

        for firewall in firewalls:
            rules = firewall.get_rules()
            inbound_rules = rules["inbound"]

            for inbound_rule in inbound_rules:
                if linode_label in inbound_rule["label"] and ip_with_mask not in inbound_rule["addresses"]["ipv4"]:
                    inbound_rule["addresses"]["ipv4"] = [ip_with_mask]

            firewall.update_rules(rules)
    except LinodeNotConfiguredError:
        logging.warning("Linode API is not fully configured. Ignoring firewall updates.")
    except Exception as e:
        logging.error(e)

def update_npm_via_orchestration_api(from_ip: Optional[str], to_ip: str):
    if from_ip is None or from_ip == to_ip:
        return

    try:
        orchestration_api_client = OrchestrationApiClient()
        orchestration_api_client.update_allow_list_with_ip(from_ip, to_ip)
        orchestration_api_client.update_proxy_hosts_with_ip(from_ip, to_ip)
    except OrchestrationApiClientError as e:
        logging.warning(f"Orchestration API is not fully configured. Ignoring proxy updates. Details: {e}")
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    logging.info("Running job...")

    ip = IpifyApiClient.get_ip()
    cached_ip = CacheIpHelper.get_cached_ip()

    if cached_ip is None:
        CacheIpHelper.cache_ip(ip)
        logging.info("Finished running job. No update but cached value from Ipify.")
    elif ip != cached_ip:
        update_linode_firewalls(ip)
        update_npm_via_orchestration_api(cached_ip, ip)
        CacheIpHelper.cache_ip(ip)
        logging.info(f"Finished running job. Updated IP from {cached_ip} to {ip}.")
    else:
        logging.info("Finished running job. No update.")