import bcrypt
import os


class AuthenticationFailedError(Exception):
    pass

class AuthenticationHelper:
    __api_key_hash: str

    def __init__(self):
        self.__api_key_hash = os.getenv("HOME_NETWORK_ORCHESTRATION_API_KEY_HASH", "$2a$12$TSiLqfqpkJbugT2JxUKO4ObTbxCoqs6m4MHZi0g5gYW/crKUJHiw.")

        if self.__api_key_hash is None or not len(self.__api_key_hash):
            raise AuthenticationFailedError("Hashed API Key was not set in environment variables. Set HOME_NETWORK_ORCHESTRATION_API_KEY_HASH")

    def validate_token(self, token: str) -> bool:
        return bcrypt.checkpw(token.encode("utf-8"), self.__api_key_hash.encode("utf-8"))