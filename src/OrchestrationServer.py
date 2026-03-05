from fastapi import FastAPI, Header, Body, Path, HTTPException
from typing import Annotated

from clients.NginxApiClient import NginxApiClient, NginxAccessListClient
from entities.OrchestratedRequests import NginxAllowListRequest
from helpers.AuthenticationHelper import AuthenticationHelper

authentication_helper = AuthenticationHelper()
nginx_api_client: NginxApiClient = NginxApiClient()

app: FastAPI = FastAPI()

@app.patch("/api/nginx/access-list/{access_list_id}", status_code = 200)
async def update_nginx_access_list(
    access_list_id: Annotated[int, Path()],
    authorization: Annotated[str | None, Header()] = None,
    request: Annotated[NginxAllowListRequest | None, Body()] = None
):
    if not authentication_helper.validate_authorization_header(authorization):
        raise HTTPException(status_code = 401)

    if request is None or not request.is_valid():
        raise HTTPException(status_code = 400, detail = "All fields are required: from_ip and to_ip.")

    access_list = nginx_api_client.fetch_access_list_by_id(access_list_id, ["clients"])

    # Remove clients matching the from_ip
    access_list.clients = [client for client in access_list.clients if client.address != request.from_ip]

    # Add client for to_ip
    access_list.clients.append(NginxAccessListClient(access_list_id = access_list_id, address = request.to_ip))

    # if to_ip already exists, don't update
    if len(access_list.clients) > 1 and any(client.address == request.to_ip for client in access_list.clients if client.address != request.to_ip):
        return access_list

    updated_access_list = nginx_api_client.update_access_list(access_list)

    return updated_access_list