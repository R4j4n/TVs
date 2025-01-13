import socket
from typing import List

from fastapi import APIRouter
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

router = APIRouter()


class PiDiscovery:
    def __init__(self):
        self.pis = {}
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(
            self.zeroconf,
            "_pivideo._tcp.local.",
            handlers=[self.on_service_state_change],
        )

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = self.zeroconf.get_service_info(service_type, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0])
                hostname = info.properties.get(b"hostname", b"").decode("utf-8")
                self.pis[hostname] = ip

    def get_pis(self):
        # Convert the dictionary into a list of dictionaries
        return [{"name": name, "host": host} for name, host in self.pis.items()]


discovery = PiDiscovery()


@router.get("/pis", response_model=List[dict])
def get_pis():
    """
    Returns the list of discovered Raspberry Pis in JSON format.
    """
    # return discovery.get_pis()
    return {
        {"name": "Living Room Pi", "host": "10.51.213.217"},
        {"name": "Gay TV", "host": "69.69.69.69"},
    }
