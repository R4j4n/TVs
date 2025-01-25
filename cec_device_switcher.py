import logging
import re
import subprocess
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Device(BaseModel):
    number: int
    name: str
    address: str
    vendor: str
    osd_string: str
    active: bool


class Cache:
    def __init__(self):
        self.devices = None
        self.last_scan = None
        self.cache_duration = 3600

    def is_valid(self):
        if not self.last_scan:
            return False
        return (datetime.now() - self.last_scan).seconds < self.cache_duration

    def set(self, devices):
        self.devices = devices
        self.last_scan = datetime.now()

    def get(self):
        return self.devices if self.is_valid() else None


class CECController:
    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logger = logging.getLogger("cec_controller")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _execute_cec_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"CEC command failed: {e}")
            raise

    def scan_devices(self) -> List[Device]:
        output = self._execute_cec_command(
            "echo 'scan' | cec-client -o RaspberryPi -s -d 1"
        )
        devices = []
        current_device = None
        default_input = None

        for line in output.splitlines():
            if device_match := re.match(r"device #(\d+): (.+)", line):
                if current_device:
                    addr_num = int(current_device.address.split(".")[0])
                    current_device.number = addr_num
                    if current_device.osd_string in ["CECTester", "RaspberryPi"]:
                        default_input = addr_num
                    devices.append(Device(**current_device.__dict__))
                name = device_match.group(2)
                current_device = Device(
                    number=0,
                    name=name,
                    address="",
                    vendor="",
                    osd_string="",
                    active=False,
                )

            if current_device:
                # Rest of parsing stays same
                if address_match := re.match(r"\s*address:\s*(.+)", line):
                    current_device.address = address_match.group(1)
                elif vendor_match := re.match(r"\s*vendor:\s*(.+)", line):
                    current_device.vendor = vendor_match.group(1)
                elif osd_match := re.match(r"\s*osd string:\s*(.+)", line):
                    current_device.osd_string = osd_match.group(1)
                elif "active source: yes" in line:
                    current_device.active = True

        if current_device:
            addr_num = int(current_device.address.split(".")[0])
            current_device.number = addr_num
            if current_device.osd_string in ["CECTester", "RaspberryPi"]:
                default_input = addr_num
            devices.append(Device(**current_device.__dict__))

        return {"devices": devices, "default_input": default_input}

    def switch_input(self, device_number: int) -> bool:
        try:
            device_hex = format(device_number * 16, "02x").upper()
            command = f'echo "tx 1F:82:{device_hex}:00" | cec-client -s -d 1'
            self._execute_cec_command(command)
            self.logger.info(f"Switched to input {device_number}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch input: {e}")
            return False


cache = Cache()
controller = CECController()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/devices")
async def get_devices():
    try:
        cached_data = cache.get()
        if not cached_data:
            cached_data = controller.scan_devices()
            cache.set(cached_data)
        return cached_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rescan")
async def rescan_devices():
    try:
        devices = controller.scan_devices()
        cache.set(devices)
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/switch/{device_number}")
async def switch_input(device_number: int):
    try:
        success = controller.switch_input(device_number)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to switch input")
        return {"message": f"Successfully switched to input {device_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
