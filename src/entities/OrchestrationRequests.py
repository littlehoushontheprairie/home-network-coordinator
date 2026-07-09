from dataclasses import dataclass
from ipaddress import ip_address

@dataclass
class UpdateIpRequest:
    from_ip: str
    to_ip: str

    def is_valid(self) -> bool:
        try:
            ip_address(self.from_ip)
            ip_address(self.to_ip)
            return True
        except ValueError:
            return False