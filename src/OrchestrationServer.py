from fastapi import FastAPI, Header, HTTPException
from typing import Annotated
from helpers.AuthenticationHelper import AuthenticationHelper

app: FastAPI = FastAPI()
authentication_helper: AuthenticationHelper = AuthenticationHelper()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.patch("/api/nginx/allowlist", status_code = 200)
def update_nginx_allowlist(authorization: Annotated[str | None, Header()] = None):
    if not authentication_helper.validate_authorization_header(authorization):
        raise HTTPException(status_code=401)

    return {}