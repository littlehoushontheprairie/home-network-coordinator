from os import environ
import bcrypt

class AuthenticationFailedError(Exception):
    pass

class AuthenticationHelper:
    __api_key_hash: str

    def __init__(self):
        self.__api_key_hash = environ.get("HOME_NETWORK_API_KEY_HASH", "$2a$12$TSiLqfqpkJbugT2JxUKO4ObTbxCoqs6m4MHZi0g5gYW/crKUJHiw.")

        if self.__api_key_hash is None or not len(self.__api_key_hash):
            raise AuthenticationFailedError("Hashed API Key was not set in environment variables. Set HOME_NETWORK_API_KEY_HASH")

    def validate_authorization_header(self, authorization: str) -> bool:
        if authorization is None or not len(authorization):
            return False

        params = authorization.split(" ")
        return len(params) == 2 and params[0] == "Bearer" and self.validate_api_key(params[1])

    def validate_api_key(self, api_key: str) -> bool:
        return bcrypt.checkpw(api_key.encode("utf-8"), self.__api_key_hash.encode("utf-8"))