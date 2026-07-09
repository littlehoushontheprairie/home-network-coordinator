import os

from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

from clients.NginxApiClient import NginxApiClient, NginxAccessListClient
from entities.OrchestrationRequests import UpdateIpRequest
from helpers.AuthenticationHelper import AuthenticationHelper

authentication_helper = AuthenticationHelper()
nginx_api_client = NginxApiClient()

app = FastAPI()
security = HTTPBearer()

@app.patch("/api/allow-list", status_code = 200)
async def update_ip_in_allow_list(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    request: Annotated[UpdateIpRequest, Body()]
):
    if not authentication_helper.validate_token(authorization.credentials):
        raise HTTPException(status_code = 401)

    if not request.is_valid():
        raise HTTPException(status_code = 400, detail = "All fields are required: from_ip and to_ip.")

    allow_list = nginx_api_client.fetch_access_list_by_name(os.getenv("ORCHESTRATION_ALLOWLIST_NAME", "allowlist"))

    # if access list has the from_ip update the client to the to_ip
    if allow_list is not None and len(allow_list.clients) and any(client.address == request.from_ip for client in allow_list.clients):
        # Remove clients matching from_ip
        allow_list.clients = [client for client in allow_list.clients if client.address != request.from_ip]

        # Only add to_ip if it's not already in the list
        if not any(client.address == request.to_ip for client in allow_list.clients):
            allow_list.clients.append(NginxAccessListClient(access_list_id = allow_list.id, address = request.to_ip))

        updated_access_list = nginx_api_client.update_access_list(allow_list)

        return updated_access_list

    raise HTTPException(status_code = 412, detail = f"Client with IP, {request.from_ip}, was not found in access list.")

@app.patch("/api/proxy-hosts", status_code = 200)
async def update_ip_in_proxy_hosts(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    request: Annotated[UpdateIpRequest, Body()]
):
    if not authentication_helper.validate_token(authorization.credentials):
        raise HTTPException(status_code = 401)

    if not request.is_valid():
        raise HTTPException(status_code = 400, detail = "All fields are required: from_ip and to_ip.")

    proxy_hosts = nginx_api_client.fetch_proxy_hosts_by_ip(request.from_ip)

    if proxy_hosts is not None and len(proxy_hosts):
        for proxy_host in proxy_hosts:
            proxy_host.forward_host = request.to_ip
            nginx_api_client.update_proxy_host(proxy_host)

        return proxy_hosts

    raise HTTPException(status_code = 412, detail = f"No proxy hosts with IP address, {request.from_ip}, were updated.")
