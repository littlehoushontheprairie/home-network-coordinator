from dataclasses import dataclass
from ipaddress import ip_address

@dataclass
class NginxAllowListRequest:
    from_ip: str
    to_ip: str

    def is_valid(self) -> bool:
        return len(self.from_ip) and ip_address(self.from_ip) and len(self.to_ip) and ip_address(self.to_ip)
