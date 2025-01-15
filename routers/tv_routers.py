import asyncio
import socket
import time
from typing import Any, Dict, List

import httpx
import uvicorn
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf


# Pydantic models for response validation
class PiStatus(BaseModel):
    error: str | None = None
    status: Dict[str, Any] | None = None


class PiDiscovery:
    def __init__(self):
        self.pis = {}
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(
            self.zeroconf,
            "_pivideo._tcp.local.",
            handlers=[self.on_service_state_change],
        )
        # Give initial time for discovery
        time.sleep(2)

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = self.zeroconf.get_service_info(service_type, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0])
                hostname = info.properties.get(b"hostname", b"").decode("utf-8")
                self.pis[hostname] = ip
        elif state_change is ServiceStateChange.Removed:
            # Remove the service when it's no longer available
            for hostname, url in list(self.pis.items()):
                if name.startswith(hostname):
                    del self.pis[hostname]

    def get_pis(self):
        return self.pis

    def __del__(self):
        self.zeroconf.close()


# Create FastAPI app
router = APIRouter()


# Create global discovery instance
discovery = PiDiscovery()


@router.get("/", response_model=dict)
async def root():
    """Root endpoint returning service information"""
    return {
        "service": "Pi Discovery",
        "status": "running",
        "endpoints": ["/pis", "/refresh", "/status"],
    }


@router.get("/pis")
async def get_pis():
    """Get status of all discovered Pis"""
    pi_statuses = []
    current_pis = discovery.get_pis()

    async with httpx.AsyncClient() as client:
        for hostname, url in current_pis.items():
            data = {}
            if hostname != "":
                data["name"] = hostname
                data["host"] = url
                pi_statuses.append(data)
    return JSONResponse(pi_statuses)
