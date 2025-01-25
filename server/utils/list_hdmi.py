import logging
import re
import subprocess
from datetime import datetime
from typing import List

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
        output = self._execute_cec_command("echo 'scan' | cec-client -s -d 1")
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
