import os
import pickle

from typing import Optional

class CacheIpHelper:
    __CURRENT_IP_FILE: str = "cached_ip.pkl"

    @staticmethod
    def cache_ip(ip: str):
        with open(CacheIpHelper.__CURRENT_IP_FILE, "wb") as output:
            pickle.dump(ip, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def get_cached_ip() -> Optional[str]:
        try:
            with open(CacheIpHelper.__CURRENT_IP_FILE, "rb") as input_file:
                return pickle.load(input_file)
        except (FileNotFoundError, EOFError):
            return None

    @staticmethod
    def clear_cached_ip():
        try:
            os.remove(CacheIpHelper.__CURRENT_IP_FILE)
        except FileNotFoundError:
            pass